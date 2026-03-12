#!/usr/bin/env python3
"""Generate PHP 8.2 class with modern features."""

import sys
import argparse

def generate_class(class_name, properties=None, namespace=None):
    """Generate a PHP 8.2 class with constructor promotion and strict types."""
    
    output = ["<?php\n", "declare(strict_types=1);\n"]
    
    if namespace:
        output.append(f"\nnamespace {namespace};\n")
    
    output.append(f"\nfinal readonly class {class_name}\n{{\n")
    
    if properties:
        # Constructor with property promotion
        output.append("    public function __construct(\n")
        for i, prop in enumerate(properties):
            prop_parts = prop.split(":")
            prop_name = prop_parts[0]
            prop_type = prop_parts[1] if len(prop_parts) > 1 else "mixed"
            comma = "," if i < len(properties) - 1 else ""
            output.append(f"        private {prop_type} ${prop_name}{comma}\n")
        output.append("    ) {\n    }\n")
    
    output.append("}\n")
    
    return "".join(output)

def main():
    parser = argparse.ArgumentParser(description="Generate PHP 8.2 class")
    parser.add_argument("class_name", help="Name of the class")
    parser.add_argument("-n", "--namespace", help="Namespace for the class")
    parser.add_argument("-p", "--properties", nargs="+", help="Properties (format: name:type)")
    
    args = parser.parse_args()
    
    code = generate_class(args.class_name, args.properties, args.namespace)
    print(code)

if __name__ == "__main__":
    main()
