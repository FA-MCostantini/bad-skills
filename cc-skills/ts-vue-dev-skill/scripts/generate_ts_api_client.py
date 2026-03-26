#!/usr/bin/env python3
"""Generate TypeScript API client class from endpoint definitions."""

import argparse
import re
import sys
from typing import List, Optional, Tuple


def to_pascal_case(name: str) -> str:
    """Convert first character to uppercase."""
    return name[0].upper() + name[1:] if name else name


def to_camel_case(name: str) -> str:
    """Convert first character to lowercase."""
    return name[0].lower() + name[1:] if name else name


def extract_path_params(path: str) -> List[str]:
    """Return list of path parameter names found in {param} syntax."""
    return re.findall(r"\{(\w+)\}", path)


def interpolate_path(path: str) -> str:
    """Replace {param} placeholders with template literal syntax."""
    return re.sub(r"\{(\w+)\}", r"${\1}", path)


def parse_endpoint(entry: str) -> Tuple[str, str, str]:
    """Parse 'methodName:METHOD:path' into (method_name, http_method, path)."""
    parts = entry.split(":", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid endpoint format (expected name:METHOD:path): {entry!r}")
    return parts[0].strip(), parts[1].strip().upper(), parts[2].strip()


def build_endpoint_method(method_name: str, http_method: str, path: str) -> str:
    """Generate a single typed endpoint method."""

    path_params = extract_path_params(path)
    has_body = http_method in ("POST", "PUT", "PATCH")
    has_path_params = bool(path_params)
    use_template = has_path_params

    # Determine return type heuristic from method name
    # e.g. getUsers -> User[], createUser -> User, getUser -> User
    words = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", method_name)
    if not words:
        return_type = "unknown"
        body_type = "Record<string, unknown>"
    else:
        verb = words[0].lower() if words else ""
        noun_words = words[1:] if len(words) > 1 else words
        noun = "".join(to_pascal_case(w) for w in noun_words)

        if not noun:
            noun = "unknown"

        # Pluralised name -> array return
        if noun.endswith("s") and verb in ("get", "list", "fetch"):
            return_type = f"{noun}[]"
        elif noun.endswith("s") and verb in ("create", "update", "delete"):
            return_type = noun.rstrip("s") if noun.endswith("s") else noun
        else:
            return_type = noun

        # Body input type: singularise for POST/PUT/PATCH
        singular_noun = noun.rstrip("s") if noun.endswith("s") else noun
        body_type = f"Create{singular_noun}Request"

    # Build parameter list
    params: List[str] = []
    for pp in path_params:
        params.append(f"{pp}: string")
    if has_body:
        params.append(f"data: {body_type} /* TODO: type properly */")
    params.append("config?: RequestConfig")
    params_str = ", ".join(params)

    # Build path expression
    if use_template:
        interpolated = interpolate_path(path)
        path_expr = f"`{interpolated}`"
    else:
        path_expr = f"'{path}'"

    # Body argument
    body_arg = "data" if has_body else "undefined"

    lines = [
        f"  async {method_name}({params_str}): Promise<{return_type}> {{",
        f"    return this.request<{return_type}>('{http_method}', {path_expr}, {body_arg}, config);",
        "  }",
    ]

    return "\n".join(lines)


def generate_ts_api_client(
    name: str,
    endpoints: Optional[List[str]] = None,
    base_url: str = "",
    with_interceptors: bool = False,
) -> str:
    """Generate a typed TypeScript API client class."""

    class_name = f"Api{to_pascal_case(name)}"
    instance_name = f"api{to_pascal_case(name)}"

    # Error + config interfaces
    preamble_lines = [
        "interface ApiError {",
        "  status: number;",
        "  message: string;",
        "  details?: Record<string, unknown>;",
        "}",
        "",
        "interface RequestConfig {",
        "  headers?: Record<string, string>;",
        "  signal?: AbortSignal;",
        "}",
    ]

    # Optional interceptor types
    interceptor_fields = ""
    interceptor_method = ""
    if with_interceptors:
        interceptor_fields = (
            "\n  private requestInterceptors: Array<(config: RequestConfig) => RequestConfig> = [];\n"
            "  private responseInterceptors: Array<(response: Response) => Response> = [];\n"
        )
        interceptor_method = (
            "\n  addRequestInterceptor(fn: (config: RequestConfig) => RequestConfig): void {\n"
            "    this.requestInterceptors.push(fn);\n"
            "  }\n\n"
            "  addResponseInterceptor(fn: (response: Response) => Response): void {\n"
            "    this.responseInterceptors.push(fn);\n"
            "  }\n"
        )

    # Private request method
    interceptor_run = ""
    if with_interceptors:
        interceptor_run = (
            "\n    let resolvedConfig = config ?? {};\n"
            "    for (const fn of this.requestInterceptors) {\n"
            "      resolvedConfig = fn(resolvedConfig);\n"
            "    }\n"
        )

    request_method_lines = [
        "  private async request<T>(",
        "    method: string,",
        "    path: string,",
        "    body?: unknown,",
        "    config?: RequestConfig,",
        "  ): Promise<T> {",
    ]
    if with_interceptors:
        request_method_lines.append(
            "    let resolvedConfig = config ?? {};\n"
            "    for (const fn of this.requestInterceptors) {\n"
            "      resolvedConfig = fn(resolvedConfig);\n"
            "    }"
        )
        headers_ref = "resolvedConfig?.headers"
        signal_ref = "resolvedConfig?.signal"
    else:
        headers_ref = "config?.headers"
        signal_ref = "config?.signal"

    request_method_lines += [
        f"    const response = await fetch(`${{this.baseUrl}}${{path}}`, {{",
        "      method,",
        f"      headers: {{ ...this.defaultHeaders, ...{headers_ref} }},",
        "      body: body ? JSON.stringify(body) : undefined,",
        f"      signal: {signal_ref},",
        "    });",
        "",
        "    if (!response.ok) {",
        "      const error: ApiError = {",
        "        status: response.status,",
        "        message: response.statusText,",
        "      };",
        "      try { error.details = await response.json(); } catch {}",
        "      throw error;",
        "    }",
        "",
        "    return response.json() as Promise<T>;",
        "  }",
    ]
    request_method = "\n".join(request_method_lines)

    # Endpoint methods
    endpoint_methods = []
    if endpoints:
        for entry in endpoints:
            try:
                method_name, http_method, path = parse_endpoint(entry)
                endpoint_methods.append(build_endpoint_method(method_name, http_method, path))
            except ValueError as exc:
                print(f"Warning: {exc}", file=sys.stderr)

    endpoints_section = ""
    if endpoint_methods:
        endpoints_section = (
            "\n  // Generated endpoint methods\n"
            + "\n\n".join(endpoint_methods)
            + "\n"
        )

    default_base = f"'{base_url}'" if base_url else "''"

    class_lines = [
        f"class {class_name} {{",
        f"  private baseUrl: string;",
        "  private defaultHeaders: Record<string, string> = {",
        "    'Content-Type': 'application/json',",
        "  };",
    ]
    if with_interceptors:
        class_lines += [
            "  private requestInterceptors: Array<(config: RequestConfig) => RequestConfig> = [];",
            "  private responseInterceptors: Array<(response: Response) => Response> = [];",
        ]
    class_lines += [
        "",
        f"  constructor(baseUrl = {default_base}) {{",
        "    this.baseUrl = baseUrl;",
        "  }",
        "",
        "  setAuthToken(token: string): void {",
        "    this.defaultHeaders['Authorization'] = `Bearer ${token}`;",
        "  }",
    ]
    if with_interceptors:
        class_lines += [
            "",
            "  addRequestInterceptor(fn: (config: RequestConfig) => RequestConfig): void {",
            "    this.requestInterceptors.push(fn);",
            "  }",
            "",
            "  addResponseInterceptor(fn: (response: Response) => Response): void {",
            "    this.responseInterceptors.push(fn);",
            "  }",
        ]
    class_lines += [
        "",
        request_method,
    ]
    if endpoints_section:
        class_lines.append(endpoints_section)
    class_lines.append("}")

    export_line = f"\nexport const {instance_name} = new {class_name}();"

    output = (
        "\n".join(preamble_lines)
        + "\n\n"
        + "\n".join(class_lines)
        + export_line
        + "\n"
    )

    return output


def main():
    parser = argparse.ArgumentParser(description="Generate TypeScript API client class")
    parser.add_argument("name", help="Client name (e.g. 'user' produces ApiUser / apiUser)")
    parser.add_argument(
        "-e", "--endpoints",
        metavar="name:METHOD:path",
        help=(
            "Comma-separated endpoint definitions "
            "(e.g. 'getUsers:GET:/api/users,createUser:POST:/api/users,getUser:GET:/api/users/{id}')"
        ),
    )
    parser.add_argument(
        "--base-url",
        metavar="URL",
        default="",
        help="Default base URL (default: empty string)",
    )
    parser.add_argument(
        "--with-interceptors",
        action="store_true",
        help="Add request/response interceptor support",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write output to FILE instead of stdout")

    args = parser.parse_args()

    endpoints = [e.strip() for e in args.endpoints.split(",")] if args.endpoints else None

    output = generate_ts_api_client(
        args.name,
        endpoints=endpoints,
        base_url=args.base_url,
        with_interceptors=args.with_interceptors,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
