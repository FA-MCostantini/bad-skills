#!/usr/bin/env python3
"""Generate a final readonly DTO class (Data Transfer Object)."""

import argparse


# Types that need a use statement
USE_MAP: dict[str, str] = {
    "DateTimeImmutable": "use DateTimeImmutable;",
    "DateTimeInterface": "use DateTimeInterface;",
    "DateTime": "use DateTime;",
}

BUILTIN_TYPES = {
    "string", "int", "float", "bool", "array", "object", "null", "void",
    "never", "mixed", "self", "static", "iterable", "callable", "true", "false",
}


def collect_uses(prop_types: list[str]) -> list[str]:
    uses = set()
    for t in prop_types:
        bare = t.lstrip("?")
        if bare in USE_MAP:
            uses.add(USE_MAP[bare])
    if uses:
        uses_sorted = sorted(uses)
        return uses_sorted
    return []


def parse_properties(raw: list[str] | None) -> list[tuple[str, str]]:
    """Parse name:type pairs, defaulting type to string."""
    if not raw:
        return []
    result = []
    for item in raw:
        if ":" in item:
            n, t = item.split(":", 1)
            result.append((n.strip(), t.strip()))
        else:
            result.append((item.strip(), "string"))
    return result


def generate_dto(
    name: str,
    properties: list[tuple[str, str]],
    namespace: str | None = None,
    with_from_array: bool = False,
    with_to_array: bool = False,
    with_json_serializable: bool = False,
) -> str:
    lines: list[str] = ["<?php", "declare(strict_types=1);", ""]

    if namespace:
        lines += [f"namespace {namespace};", ""]

    # use statements
    prop_types = [t for _, t in properties]
    uses = collect_uses(prop_types)
    if with_json_serializable:
        # JsonSerializable is a built-in interface, no use needed
        pass
    if uses:
        lines += uses + [""]

    implements = " implements \\JsonSerializable" if with_json_serializable else ""

    lines.append(f"final readonly class {name}{implements}")
    lines.append("{")

    # Constructor
    if properties:
        lines.append("    public function __construct(")
        for i, (prop_name, prop_type) in enumerate(properties):
            comma = "," if i < len(properties) - 1 else ","
            lines.append(f"        public {prop_type} ${prop_name}{comma}")
        lines.append("    ) {")
        lines.append("    }")
    else:
        lines.append("    public function __construct(")
        lines.append("        // TODO: add properties")
        lines.append("    ) {")
        lines.append("    }")

    # fromArray()
    if with_from_array:
        lines += [
            "",
            "    /**",
            "     * @param array<string, mixed> $data",
            "     */",
            "    public static function fromArray(array $data): self",
            "    {",
            "        return new self(",
        ]
        for prop_name, prop_type in properties:
            lines.append(
                f"            {prop_name}: $data['{prop_name}'], // {prop_type}"
            )
        lines += [
            "        );",
            "    }",
        ]

    # toArray()
    if with_to_array:
        lines += [
            "",
            "    /**",
            "     * @return array<string, mixed>",
            "     */",
            "    public function toArray(): array",
            "    {",
            "        return [",
        ]
        for prop_name, _ in properties:
            lines.append(f"            '{prop_name}' => $this->{prop_name},")
        lines += [
            "        ];",
            "    }",
        ]

    # jsonSerialize()
    if with_json_serializable:
        lines += [
            "",
            "    /**",
            "     * @return array<string, mixed>",
            "     */",
            "    public function jsonSerialize(): array",
            "    {",
            "        return [",
        ]
        for prop_name, _ in properties:
            lines.append(f"            '{prop_name}' => $this->{prop_name},")
        lines += [
            "        ];",
            "    }",
        ]

    lines += ["}", ""]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a PHP readonly DTO class")
    parser.add_argument("name", help="Class name (e.g. CreateOrderCommand)")
    parser.add_argument(
        "-p",
        "--properties",
        nargs="+",
        help="Properties as name:type pairs (e.g. userId:int email:string)",
    )
    parser.add_argument("-n", "--namespace", help="PHP namespace")
    parser.add_argument(
        "--with-from-array",
        action="store_true",
        help="Add static fromArray() factory method",
    )
    parser.add_argument(
        "--with-to-array",
        action="store_true",
        help="Add toArray() method",
    )
    parser.add_argument(
        "--with-json-serializable",
        action="store_true",
        help="Implement JsonSerializable interface",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    properties = parse_properties(args.properties)

    code = generate_dto(
        name=args.name,
        properties=properties,
        namespace=args.namespace,
        with_from_array=args.with_from_array,
        with_to_array=args.with_to_array,
        with_json_serializable=args.with_json_serializable,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
    else:
        print(code)


if __name__ == "__main__":
    main()
