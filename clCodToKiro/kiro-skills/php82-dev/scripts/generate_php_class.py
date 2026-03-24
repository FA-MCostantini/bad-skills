#!/usr/bin/env python3
"""Generate PHP 8.2 class with modern features."""

import argparse

# Types that require a use statement
USE_STATEMENTS = {
    "DateTimeImmutable": "use DateTimeImmutable;",
    "DateTimeInterface": "use DateTimeInterface;",
    "DateTime": "use DateTime;",
    "Closure": None,  # built-in, no use needed
    "Generator": None,  # built-in, no use needed
    "WeakMap": None,  # built-in, no use needed
}

# Known scalar / built-in types (no use statement needed)
BUILTIN_TYPES = {
    "string", "int", "float", "bool", "array", "object", "null", "void",
    "never", "mixed", "self", "static", "iterable", "callable",
    "true", "false",
}


def collect_use_statements(prop_types: list[str]) -> list[str]:
    """Return sorted list of unique use-statement lines needed for the given types."""
    uses = set()
    for raw_type in prop_types:
        # Strip nullability prefix
        type_name = raw_type.lstrip("?")
        if type_name in USE_STATEMENTS and USE_STATEMENTS[type_name] is not None:
            uses.add(USE_STATEMENTS[type_name])
    return sorted(uses)


def generate_class(class_name, properties=None, namespace=None):
    """Generate a PHP 8.2 class with constructor promotion and strict types."""

    output = ["<?php\n", "declare(strict_types=1);\n"]

    if namespace:
        output.append(f"\nnamespace {namespace};\n")

    # Collect types and build use statements
    prop_defs = []  # list of (name, type, needs_todo)
    if properties:
        for prop in properties:
            parts = prop.split(":")
            prop_name = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                prop_type = parts[1].strip()
                needs_todo = False
            else:
                prop_type = "string"  # TODO: specify correct type
                needs_todo = True
            prop_defs.append((prop_name, prop_type, needs_todo))

    # Add use statements
    if prop_defs:
        use_lines = collect_use_statements([t for _, t, _ in prop_defs])
        if use_lines:
            output.append("\n")
            for use_line in use_lines:
                output.append(use_line + "\n")

    output.append(f"\nfinal readonly class {class_name}\n{{\n")

    if prop_defs:
        output.append("    public function __construct(\n")
        for i, (prop_name, prop_type, needs_todo) in enumerate(prop_defs):
            comma = "," if i < len(prop_defs) - 1 else ","
            todo = " // TODO: specify correct type" if needs_todo else ""
            output.append(f"        private {prop_type} ${prop_name}{comma}{todo}\n")
        output.append("    ) {\n    }\n")

    output.append("}\n")

    return "".join(output)


def main():
    parser = argparse.ArgumentParser(description="Generate PHP 8.2 class")
    parser.add_argument("class_name", help="Name of the class")
    parser.add_argument("-n", "--namespace", help="Namespace for the class")
    parser.add_argument(
        "-p", "--properties", nargs="+", help="Properties (format: name:type)"
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    code = generate_class(args.class_name, args.properties, args.namespace)

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
    else:
        print(code)


if __name__ == "__main__":
    main()
