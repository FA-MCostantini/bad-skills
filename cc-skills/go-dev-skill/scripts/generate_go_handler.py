#!/usr/bin/env python3
"""Generate a Go 1.22+ HTTP handler with route registrations and method stubs."""

import argparse
import re
import sys
import textwrap


def snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def pascal_to_camel(name: str) -> str:
    if not name:
        return name
    return name[0].lower() + name[1:]


# HTTP method → verb prefix for the handler function name.
_METHOD_VERB = {
    "GET": "List",
    "POST": "Create",
    "PUT": "Update",
    "PATCH": "Patch",
    "DELETE": "Delete",
}


def _route_to_method_name(method: str, path: str) -> str:
    """Derive a camelCase handler method name from an HTTP method + path.

    Rules:
    - Use the last non-empty path segment (strip {…} braces if present).
    - If the last segment is a path parameter (had braces), treat the route as
      a single-resource operation (Get / Update / Delete / …) — drop the
      trailing 's' from the resource noun when the verb implies a single item.
    - "GET /users"       → handleListUsers
    - "POST /users"      → handleCreateUsers
    - "GET /users/{id}"  → handleGetUser   (singular)
    - "DELETE /users/{id}" → handleDeleteUser
    - "PUT /users/{id}"  → handleUpdateUser
    """
    segments = [s for s in path.split("/") if s]
    if not segments:
        return "handleRoot"

    last = segments[-1]
    has_param = last.startswith("{") and last.endswith("}")

    # Use the second-to-last segment as the resource noun when the last is a
    # path parameter; otherwise use the last segment itself.
    if has_param:
        resource_segment = segments[-2] if len(segments) >= 2 else "resource"
        singular = True
    else:
        resource_segment = last
        singular = False

    # Convert kebab/snake path segment to PascalCase resource name.
    resource = snake_to_pascal(resource_segment)

    # Strip trailing 's' for singular references (best-effort).
    if singular and resource.endswith("s"):
        resource = resource[:-1]

    if has_param:
        # For parameterised routes GET still means "get one", not "list".
        verb_map = {
            "GET": "Get",
            "POST": "Create",
            "PUT": "Update",
            "PATCH": "Patch",
            "DELETE": "Delete",
        }
        verb = verb_map.get(method.upper(), snake_to_pascal(method.lower()))
    else:
        verb = _METHOD_VERB.get(method.upper(), snake_to_pascal(method.lower()))

    return f"handle{verb}{resource}"


def _path_params(path: str) -> list[str]:
    """Return path parameter names (without braces) from a route pattern."""
    return re.findall(r"\{(\w+)\}", path)


def generate_handler(name: str, routes: list[str], service: str) -> str:
    pascal = snake_to_pascal(name)
    camel = pascal_to_camel(pascal)

    service_pascal = snake_to_pascal(service) if service else pascal
    service_iface = f"{service_pascal}Service"

    # Collect unique method names in declaration order; duplicate routes get
    # the same handler, so we de-duplicate while preserving order.
    seen: set[str] = set()
    route_entries: list[tuple[str, str, str]] = []  # (method, path, func_name)
    for route in routes:
        parts = route.strip().split(None, 1)
        if len(parts) != 2:
            continue
        http_method, path = parts
        func_name = _route_to_method_name(http_method, path)
        route_entries.append((http_method, path, func_name))
        seen.add(func_name)

    # Build RegisterRoutes body.
    register_lines = []
    for http_method, path, func_name in route_entries:
        register_lines.append(
            f'\tmux.HandleFunc("{http_method} {path}", h.{func_name})'
        )

    # Build method stubs.
    generated_stubs: dict[str, str] = {}
    for http_method, path, func_name in route_entries:
        if func_name in generated_stubs:
            continue
        params = _path_params(path)
        body_lines: list[str] = ["\tctx := r.Context()"]
        unused: list[str] = ["ctx"]
        for p in params:
            body_lines.append(f'\t{p} := r.PathValue("{p}")')
            unused.append(p)
        body_lines.append("\t// TODO: implement")
        if unused:
            body_lines.append(f"\t_, _ = {', '.join(unused)}" if len(unused) > 1 else f"\t_ = {unused[0]}")
        body_lines.append("\twriteJSON(w, http.StatusOK, nil)")

        stub = textwrap.dedent(f"""\
            func (h *{pascal}Handler) {func_name}(w http.ResponseWriter, r *http.Request) {{
            {chr(10).join(body_lines)}
            }}""")
        generated_stubs[func_name] = stub

    lines: list[str] = [
        "package api",
        "",
        "import (",
        '\t"encoding/json"',
        '\t"log/slog"',
        '\t"net/http"',
        ")",
        "",
        f"// {pascal}Handler handles HTTP requests for {pascal} resources.",
        f"type {pascal}Handler struct {{",
        f"\tservice {service_iface}",
        "\tlogger  *slog.Logger",
        "}",
        "",
        f"// New{pascal}Handler creates a new {pascal}Handler.",
        f"func New{pascal}Handler(svc {service_iface}, log *slog.Logger) *{pascal}Handler {{",
        f"\treturn &{pascal}Handler{{service: svc, logger: log}}",
        "}",
        "",
        f"// RegisterRoutes registers all {pascal} routes on mux.",
        f"func (h *{pascal}Handler) RegisterRoutes(mux *http.ServeMux) {{",
        *register_lines,
        "}",
        "",
    ]

    for stub in generated_stubs.values():
        lines.append(stub)
        lines.append("")

    # writeJSON / writeError helpers.
    helpers = textwrap.dedent(f"""\
        func writeJSON(w http.ResponseWriter, status int, data any) {{
        \tw.Header().Set("Content-Type", "application/json")
        \tw.WriteHeader(status)
        \tif data != nil {{
        \t\tjson.NewEncoder(w).Encode(data)
        \t}}
        }}

        func writeError(w http.ResponseWriter, status int, msg string) {{
        \twriteJSON(w, status, map[string]string{{"error": msg}})
        }}""")
    lines.append(helpers)

    # Suppress unused import of camel if no deps reference it (keep compiler happy).
    _ = camel

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Go 1.22+ HTTP handler skeleton."
    )
    parser.add_argument("name", help="Handler base name (e.g. 'user' → UserHandler)")
    parser.add_argument(
        "-r", "--routes",
        default="",
        help=(
            "Comma-separated routes (e.g. 'GET /users,POST /users,GET /users/{id}'). "
            "Each entry is '<METHOD> <path>'."
        ),
    )
    parser.add_argument(
        "-s", "--service",
        default="",
        metavar="SERVICE",
        help="Service interface base name (e.g. 'user' → UserService). Defaults to handler name.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    args = parser.parse_args()

    routes = [r.strip() for r in args.routes.split(",") if r.strip()]
    code = generate_handler(args.name, routes, args.service)

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(code)


if __name__ == "__main__":
    main()
