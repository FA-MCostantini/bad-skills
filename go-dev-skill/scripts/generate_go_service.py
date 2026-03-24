#!/usr/bin/env python3
"""Generate a Go 1.22+ service interface, struct, constructor, and optional test skeleton."""

import argparse
import sys
import textwrap


def snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def pascal_to_camel(name: str) -> str:
    if not name:
        return name
    return name[0].lower() + name[1:]


def generate_service(name: str, methods: list[str], deps: list[str], with_tests: bool) -> str:
    pascal = snake_to_pascal(name)
    camel = pascal_to_camel(pascal)

    # Build dependency fields and constructor params
    dep_structs = []
    for dep in deps:
        dep_pascal = snake_to_pascal(dep)
        dep_camel = pascal_to_camel(dep_pascal)
        dep_structs.append((dep_camel, dep_pascal))

    # Interface methods
    iface_methods = []
    for m in methods:
        m_pascal = snake_to_pascal(m)
        iface_methods.append(f"\t{m_pascal}(ctx context.Context) error")

    # Struct fields
    struct_fields = []
    for field_name, field_type in dep_structs:
        struct_fields.append(f"\t{field_name} {field_type}")

    # Constructor params
    ctor_params = ["ctx context.Context"] if not dep_structs else []
    for field_name, field_type in dep_structs:
        ctor_params.append(f"{field_name} {field_type}")

    # Method stubs
    method_stubs = []
    for m in methods:
        m_pascal = snake_to_pascal(m)
        stub = textwrap.dedent(f"""\
            func (s *{camel}Service) {m_pascal}(ctx context.Context) error {{
            \t// TODO: implement {m_pascal}
            \treturn nil
            }}""")
        method_stubs.append(stub)

    # Imports
    imports = ["context"]

    lines = [
        "package service",
        "",
        "import (",
        *[f'\t"{imp}"' for imp in imports],
        ")",
        "",
        f"// {pascal}Service defines the {pascal} business operations.",
        f"type {pascal}Service interface {{",
        *iface_methods,
        "}",
        "",
        f"// {camel}Service is the unexported implementation of {pascal}Service.",
        f"type {camel}Service struct {{",
    ]
    if struct_fields:
        lines.extend(struct_fields)
    else:
        lines.append("\t// add dependencies here")
    lines += [
        "}",
        "",
        f"// Compile-time interface check.",
        f"var _ {pascal}Service = (*{camel}Service)(nil)",
        "",
    ]

    # Constructor
    ctor_param_str = ", ".join(f"{n} {t}" for n, t in dep_structs)
    field_inits = "\n".join(f"\t\t{n}: {n}," for n, _ in dep_structs) if dep_structs else "\t\t// no deps"
    lines += [
        f"// New{pascal}Service creates a new {pascal}Service.",
        f"func New{pascal}Service({ctor_param_str}) *{camel}Service {{",
        f"\treturn &{camel}Service{{",
        field_inits,
        "\t}",
        "}",
        "",
    ]

    lines.extend(stub + "\n" for stub in method_stubs)

    return "\n".join(lines).rstrip() + "\n"


def generate_tests(name: str, methods: list[str]) -> str:
    pascal = snake_to_pascal(name)
    camel = pascal_to_camel(pascal)

    test_funcs = []
    for m in methods:
        m_pascal = snake_to_pascal(m)
        func_code = textwrap.dedent(f"""\
            func Test{pascal}Service_{m_pascal}(t *testing.T) {{
            \ttests := []struct {{
            \t\tname    string
            \t\twantErr bool
            \t}}{{
            \t\t{{"success", false}},
            \t}}

            \tfor _, tt := range tests {{
            \t\tt.Run(tt.name, func(t *testing.T) {{
            \t\t\tsvc := New{pascal}Service()
            \t\t\terr := svc.{m_pascal}(context.Background())
            \t\t\tif (err != nil) != tt.wantErr {{
            \t\t\t\tt.Errorf("{m_pascal}() error = %v, wantErr %v", err, tt.wantErr)
            \t\t\t}}
            \t\t}})
            \t}}
            }}""")
        test_funcs.append(func_code)

    lines = [
        "package service",
        "",
        "import (",
        '\t"context"',
        '\t"testing"',
        ")",
        "",
    ]
    lines.extend(f + "\n" for f in test_funcs)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Go 1.22+ service interface and implementation skeleton."
    )
    parser.add_argument("name", help="Service name (e.g. 'user' → UserService)")
    parser.add_argument(
        "-m", "--methods",
        default="",
        help="Comma-separated method names (e.g. 'create,update,delete')",
    )
    parser.add_argument(
        "-d", "--deps",
        default="",
        help="Comma-separated dependency interface names (e.g. 'UserRepository,EmailSender')",
    )
    parser.add_argument(
        "--with-tests",
        action="store_true",
        help="Also generate a test file skeleton",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    args = parser.parse_args()

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    deps = [d.strip() for d in args.deps.split(",") if d.strip()]

    code = generate_service(args.name, methods, deps, args.with_tests)

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
        if args.with_tests:
            test_path = args.output.replace(".go", "_test.go")
            with open(test_path, "w") as f:
                f.write(generate_tests(args.name, methods))
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(code)
        if args.with_tests:
            sys.stdout.write("\n// --- test skeleton ---\n\n")
            sys.stdout.write(generate_tests(args.name, methods))


if __name__ == "__main__":
    main()
