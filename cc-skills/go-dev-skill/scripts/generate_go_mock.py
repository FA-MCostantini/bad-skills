#!/usr/bin/env python3
"""Generate a Go 1.22+ mock struct that implements a named interface."""

import argparse
import sys
import textwrap


# ---------------------------------------------------------------------------
# Name helpers
# ---------------------------------------------------------------------------

def snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def pascal_to_camel(name: str) -> str:
    if not name:
        return name
    return name[0].lower() + name[1:]


# ---------------------------------------------------------------------------
# Method / type parsing
# ---------------------------------------------------------------------------

def parse_param(raw: str) -> tuple[str, str]:
    """Parse 'ctx context.Context' → ('ctx', 'context.Context').

    Handles pointer types such as '*User' and qualified types like 'pgxpool.Pool'.
    The name is the first token; everything else is the type.
    """
    raw = raw.strip()
    parts = raw.split()
    if len(parts) < 2:
        # Only a type (no name given) — synthesise a name.
        return ("_", raw)
    name = parts[0]
    go_type = " ".join(parts[1:])
    return (name, go_type)


def parse_methods(raw: str) -> list[dict]:
    """Parse method definitions from the CLI string.

    Format:  MethodName:param1 type1;param2 type2:return1 type1;return2 type2
    Returns a list of dicts with keys:
        name       – PascalCase method name
        params     – list of (param_name, go_type)
        returns    – list of go_type strings
    """
    methods: list[dict] = []
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":", 2)
        method_name = snake_to_pascal(parts[0].strip())

        params_raw = parts[1].strip() if len(parts) > 1 else ""
        returns_raw = parts[2].strip() if len(parts) > 2 else ""

        params = [parse_param(p) for p in params_raw.split(";") if p.strip()]
        returns = [r.strip() for r in returns_raw.split(";") if r.strip()]

        methods.append({"name": method_name, "params": params, "returns": returns})
    return methods


# ---------------------------------------------------------------------------
# Import detection
# ---------------------------------------------------------------------------

def _collect_imports(methods: list[dict]) -> list[str]:
    """Return sorted stdlib / well-known imports required by method signatures."""
    imports: set[str] = set()
    for m in methods:
        all_types = [t for _, t in m["params"]] + m["returns"]
        for t in all_types:
            if "context.Context" in t:
                imports.add("context")
            if "time." in t:
                imports.add("time")
            if "sync." in t:
                imports.add("sync")
    return sorted(imports)


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def _call_struct_name(method_name: str) -> str:
    return f"{method_name}Call"


def _func_field_name(method_name: str) -> str:
    return f"{method_name}Func"


def _calls_field_name(method_name: str) -> str:
    return f"{pascal_to_camel(method_name)}Calls"


def _param_signature(params: list[tuple[str, str]]) -> str:
    return ", ".join(f"{name} {go_type}" for name, go_type in params)


def _return_signature(returns: list[str]) -> str:
    if not returns:
        return ""
    if len(returns) == 1:
        return f" {returns[0]}"
    return f" ({', '.join(returns)})"


def _zero_for(go_type: str) -> str:
    """Return the Go zero value literal for a type."""
    t = go_type.strip()
    if t.startswith("*") or t.startswith("[]") or t == "error":
        return "nil"
    if t in ("bool",):
        return "false"
    if t in ("string",):
        return '""'
    if t in ("int", "int8", "int16", "int32", "int64",
             "uint", "uint8", "uint16", "uint32", "uint64",
             "float32", "float64"):
        return "0"
    return "nil"


def generate_mock(interface_name: str, methods: list[dict]) -> str:
    pascal = snake_to_pascal(interface_name)

    imports = _collect_imports(methods)

    # ---- call structs -------------------------------------------------------
    call_struct_lines: list[str] = []
    for m in methods:
        struct_name = _call_struct_name(m["name"])
        fields: list[str] = []
        for pname, ptype in m["params"]:
            if pname == "_":
                continue
            fields.append(f"\t{snake_to_pascal(pname)}\t{ptype}")
        if fields:
            call_struct_lines += [
                f"type {struct_name} struct {{",
                *fields,
                "}",
                "",
            ]
        else:
            call_struct_lines += [
                f"type {struct_name} struct{{}}",
                "",
            ]

    # ---- Mock struct fields --------------------------------------------------
    mock_func_fields: list[str] = []
    mock_call_fields: list[str] = []
    for m in methods:
        func_sig = f"func({_param_signature(m['params'])}){_return_signature(m['returns'])}"
        mock_func_fields.append(f"\t{_func_field_name(m['name'])}\t{func_sig}")
        mock_call_fields.append(
            f"\t{_calls_field_name(m['name'])}\t[]{_call_struct_name(m['name'])}"
        )

    # ---- Method implementations ---------------------------------------------
    method_stubs: list[str] = []
    for m in methods:
        method_name = m["name"]
        params = m["params"]
        returns = m["returns"]

        # Build call struct literal
        struct_fields = {snake_to_pascal(pname): pname for pname, _ in params if pname != "_"}
        if struct_fields:
            init_fields = ", ".join(f"{k}: {v}" for k, v in struct_fields.items())
            append_line = (
                f"\tm.{_calls_field_name(method_name)} = append("
                f"m.{_calls_field_name(method_name)}, "
                f"{_call_struct_name(method_name)}{{{init_fields}}})"
            )
        else:
            append_line = (
                f"\tm.{_calls_field_name(method_name)} = append("
                f"m.{_calls_field_name(method_name)}, "
                f"{_call_struct_name(method_name)}{{}})"
            )

        # Delegate to Func field if set
        param_names = [pname for pname, _ in params if pname != "_"]
        call_args = ", ".join(param_names)

        if returns:
            zero_returns = ", ".join(_zero_for(r) for r in returns)
            delegate_block = textwrap.dedent(f"""\
                \tif m.{_func_field_name(method_name)} != nil {{
                \t\treturn m.{_func_field_name(method_name)}({call_args})
                \t}}
                \treturn {zero_returns}""")
        else:
            delegate_block = textwrap.dedent(f"""\
                \tif m.{_func_field_name(method_name)} != nil {{
                \t\tm.{_func_field_name(method_name)}({call_args})
                \t}}""")

        ret_sig = _return_signature(returns)
        stub = textwrap.dedent(f"""\
            func (m *Mock{pascal}) {method_name}({_param_signature(params)}){ret_sig} {{
            {append_line}
            {delegate_block}
            }}""")
        method_stubs.append(stub)

        # Calls accessor
        calls_accessor = textwrap.dedent(f"""\
            func (m *Mock{pascal}) {snake_to_pascal(method_name)}Calls() []{_call_struct_name(method_name)} {{
            \treturn m.{_calls_field_name(method_name)}
            }}""")
        method_stubs.append(calls_accessor)

    # ---- Assemble -----------------------------------------------------------
    lines: list[str] = ["package mock", ""]

    if imports:
        lines += [
            "import (",
            *[f'\t"{imp}"' for imp in imports],
            ")",
            "",
        ]

    # Call structs
    lines.extend(call_struct_lines)

    # Mock struct
    lines += [
        f"// Mock{pascal} is a test mock for the {pascal} interface.",
        f"type Mock{pascal} struct {{",
        *mock_func_fields,
        "",
        *mock_call_fields,
        "}",
        "",
    ]

    for stub in method_stubs:
        lines.append(stub)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Go 1.22+ mock struct that implements a named interface."
    )
    parser.add_argument(
        "name",
        help="Interface name (e.g. 'UserRepository' → MockUserRepository)",
    )
    parser.add_argument(
        "-m", "--methods",
        default="",
        help=(
            "Comma-separated method definitions.  Each definition has the form "
            "'MethodName:param1 type1;param2 type2:return1;return2'.  "
            "Example: 'Find:ctx context.Context;id int64:*User;error,"
            "Create:ctx context.Context;entity *User:error'"
        ),
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    args = parser.parse_args()

    methods = parse_methods(args.methods)
    code = generate_mock(args.name, methods)

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(code)


if __name__ == "__main__":
    main()
