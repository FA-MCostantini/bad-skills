#!/usr/bin/env python3
"""Generate a PHP Service class with dependency injection and optional companion interface."""

import argparse


def parse_deps(raw: list[str] | None) -> list[tuple[str, str]]:
    """Parse name:Type pairs."""
    if not raw:
        return []
    result = []
    for item in raw:
        item = item.strip()
        if ":" in item:
            n, t = item.split(":", 1)
            result.append((n.strip(), t.strip()))
        else:
            # Guess type name from dep name
            type_name = item.strip().capitalize() + "Interface"
            result.append((item.strip(), type_name))
    return result


def generate_interface(name: str, methods: list[str], namespace: str | None) -> str:
    lines: list[str] = ["<?php", "declare(strict_types=1);", ""]
    if namespace:
        lines += [f"namespace {namespace};", ""]

    lines.append(f"interface {name}Interface")
    lines.append("{")
    for method in methods:
        lines.append(f"    public function {method}(): mixed;")
    lines += ["}", ""]
    return "\n".join(lines)


def generate_service(
    name: str,
    methods: list[str],
    deps: list[tuple[str, str]],
    namespace: str | None = None,
    with_interface: bool = False,
) -> dict[str, str]:
    lines: list[str] = ["<?php", "declare(strict_types=1);", ""]

    if namespace:
        lines += [f"namespace {namespace};", ""]

    lines.append("use Psr\\Log\\LoggerInterface;")
    lines.append("")

    # Implements clause
    implements = f" implements {name}Interface" if with_interface else ""

    lines.append(f"final class {name}{implements}")
    lines.append("{")

    # Constructor
    lines.append("    public function __construct(")
    for dep_name, dep_type in deps:
        lines.append(f"        private readonly {dep_type} ${dep_name},")
    lines.append("        private readonly LoggerInterface $logger,")
    lines.append("    ) {")
    lines.append("    }")

    # Methods
    for method in methods:
        lines += [
            "",
            f"    public function {method}(): mixed",
            "    {",
            "        try {",
            f"            // TODO: implement {method}",
            "            return null;",
            "        } catch (\\Throwable $e) {",
            f"            $this->logger->error('Failed in {name}::{method}', [",
            "                'exception' => $e->getMessage(),",
            "            ]);",
            "            throw $e;",
            "        }",
            "    }",
        ]

    lines += ["}", ""]

    result: dict[str, str] = {"service": "\n".join(lines)}

    if with_interface:
        result["interface"] = generate_interface(name, methods, namespace)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PHP Service class")
    parser.add_argument("name", help="Service class name (e.g. OrderService)")
    parser.add_argument(
        "-m",
        "--methods",
        nargs="+",
        help="Method names to generate (e.g. create update delete)",
    )
    parser.add_argument(
        "-d",
        "--deps",
        nargs="+",
        help="Dependencies as name:Type pairs (e.g. repository:OrderRepositoryInterface)",
    )
    parser.add_argument("-n", "--namespace", help="PHP namespace")
    parser.add_argument(
        "--with-interface",
        action="store_true",
        help="Also generate a companion interface file",
    )
    parser.add_argument("-o", "--output", help="Output file for service (default: stdout)")
    parser.add_argument(
        "--output-interface",
        help="Output file for interface (default: stdout). Requires --with-interface",
    )

    args = parser.parse_args()

    methods = args.methods or ["execute"]
    deps = parse_deps(args.deps)

    result = generate_service(
        name=args.name,
        methods=methods,
        deps=deps,
        namespace=args.namespace,
        with_interface=args.with_interface,
    )

    service_code = result["service"]
    interface_code = result.get("interface")

    if args.output:
        with open(args.output, "w") as f:
            f.write(service_code)
    else:
        print(service_code)

    if interface_code:
        if args.output_interface:
            with open(args.output_interface, "w") as f:
                f.write(interface_code)
        else:
            if args.output:
                # If service went to file, print interface to stdout
                print(interface_code)
            else:
                print("\n" + "=" * 50 + "\n")
                print(interface_code)


if __name__ == "__main__":
    main()
