#!/usr/bin/env python3
"""Generate a backed PHP 8.1+ Enum."""

import argparse
import sys


def namespace_block(namespace: str | None) -> str:
    if namespace:
        return f"namespace {namespace};\n\n"
    return ""


def generate_enum(
    name: str,
    backing_type: str = "string",
    cases: list[tuple[str, str]] | None = None,
    interface: str | None = None,
    with_label: bool = False,
    namespace: str | None = None,
) -> str:
    lines = [
        "<?php",
        "declare(strict_types=1);",
        "",
    ]

    if namespace:
        lines += [f"namespace {namespace};", ""]

    # Interface declaration
    implements = f" implements {interface}" if interface else ""

    lines.append(f"enum {name}: {backing_type}{implements}")
    lines.append("{")

    # Cases
    if cases:
        for case_name, case_value in cases:
            if backing_type == "int":
                lines.append(f"    case {case_name} = {case_value};")
            else:
                lines.append(f"    case {case_name} = '{case_value}';")
    else:
        lines.append(f"    case Example = 'example'; // TODO: replace with real cases")

    # label() method
    if with_label and cases:
        lines += [
            "",
            "    public function label(): string",
            "    {",
            "        return match($this) {",
        ]
        for case_name, _ in cases:
            # Convert UPPER_SNAKE to Title Case for label
            label = case_name.replace("_", " ").title()
            lines.append(f"            self::{case_name} => '{label}',")
        lines += [
            "        };",
            "    }",
        ]
    elif with_label:
        lines += [
            "",
            "    public function label(): string",
            "    {",
            "        // TODO: implement labels",
            "        return $this->name;",
            "    }",
        ]

    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def parse_cases(raw: str | None) -> list[tuple[str, str]]:
    """Parse comma-separated NAME:value pairs."""
    if not raw:
        return []
    result = []
    for item in raw.split(","):
        item = item.strip()
        if ":" in item:
            n, v = item.split(":", 1)
            result.append((n.strip(), v.strip()))
        else:
            result.append((item, item.lower()))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PHP backed Enum")
    parser.add_argument("name", help="Enum name (e.g. Status)")
    parser.add_argument(
        "--type",
        choices=["string", "int"],
        default="string",
        help="Backing type (default: string)",
    )
    parser.add_argument(
        "--cases",
        help="Comma-separated NAME:value pairs (e.g. Active:active,Inactive:inactive)",
    )
    parser.add_argument(
        "--interface",
        help="Interface to implement (e.g. HasLabel)",
    )
    parser.add_argument(
        "--with-label",
        action="store_true",
        help="Add a label() method using match expression",
    )
    parser.add_argument("-n", "--namespace", help="PHP namespace")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    cases = parse_cases(args.cases)

    code = generate_enum(
        name=args.name,
        backing_type=args.type,
        cases=cases,
        interface=args.interface,
        with_label=args.with_label,
        namespace=args.namespace,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
    else:
        print(code)


if __name__ == "__main__":
    main()
