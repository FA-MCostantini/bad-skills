#!/usr/bin/env python3
"""Generate TypeScript interfaces, types and utilities."""

import argparse
import sys
from typing import List, Optional


def parse_property(prop: str):
    """Parse a property string into (name, type, is_optional, is_readonly).

    Uses split(":", 1) so types like Record<string, number> are preserved.
    """
    # Strip leading 'readonly ' marker if present
    is_readonly = False
    work = prop
    if work.startswith("readonly "):
        is_readonly = True
        work = work[len("readonly "):]

    parts = work.split(":", 1)
    raw_name = parts[0]
    prop_type = parts[1].strip() if len(parts) > 1 else "unknown"

    is_optional = raw_name.endswith("?")
    prop_name = raw_name[:-1] if is_optional else raw_name

    return prop_name, prop_type, is_optional, is_readonly


def generate_interface(
    name: str,
    properties: Optional[List[str]] = None,
    extends: Optional[str] = None,
) -> str:
    """Generate TypeScript interface with properties."""

    output = []

    if extends:
        output.append(f"export interface {name} extends {extends} {{")
    else:
        output.append(f"export interface {name} {{")

    if properties:
        for prop in properties:
            prop_name, prop_type, is_optional, is_readonly = parse_property(prop)
            readonly_prefix = "readonly " if is_readonly else ""
            optional_suffix = "?" if is_optional else ""
            output.append(f"  {readonly_prefix}{prop_name}{optional_suffix}: {prop_type};")

    output.append("}")

    return "\n".join(output)


def generate_type_guard(
    interface_name: str,
    properties: Optional[List[str]] = None,
    check_property: str = "id",
) -> str:
    """Generate type guard function for an interface.

    Emits property-type checks for each declared property, not just
    a simple 'key in value' presence check.
    """

    checks = [
        "    typeof value === 'object'",
        "    value !== null",
    ]

    if properties:
        for prop in properties:
            prop_name, prop_type, is_optional, _ = parse_property(prop)

            # Determine the JS typeof string for simple types
            simple_type_map = {
                "string": "string",
                "number": "number",
                "boolean": "boolean",
                "bigint": "bigint",
                "symbol": "symbol",
            }

            normalized = prop_type.strip().rstrip("[]")

            if is_optional:
                # Optional: either absent or correct type
                if normalized in simple_type_map:
                    js_type = simple_type_map[normalized]
                    checks.append(
                        f"    (!('{prop_name}' in value) || "
                        f"typeof (value as {interface_name}).{prop_name} === '{js_type}')"
                    )
                else:
                    checks.append(
                        f"    (!('{prop_name}' in value) || "
                        f"(value as {interface_name}).{prop_name} !== undefined)"
                    )
            else:
                checks.append(f"    '{prop_name}' in value")
                if normalized in simple_type_map:
                    js_type = simple_type_map[normalized]
                    checks.append(
                        f"    typeof (value as {interface_name}).{prop_name} === '{js_type}'"
                    )
                elif prop_type.endswith("[]") or prop_type.startswith("Array<"):
                    checks.append(
                        f"    Array.isArray((value as {interface_name}).{prop_name})"
                    )
                else:
                    checks.append(
                        f"    (value as {interface_name}).{prop_name} !== null && "
                        f"typeof (value as {interface_name}).{prop_name} === 'object'"
                    )
    else:
        # Fallback: check the single named property
        checks.append(f"    '{check_property}' in value")
        checks.append(
            f"    typeof (value as any).{check_property} !== 'undefined'"
        )

    checks_str = " &&\n".join(checks)

    return f"""export function is{interface_name}(value: unknown): value is {interface_name} {{
  return (
{checks_str}
  );
}}"""


def generate_dto_class(name: str, properties: Optional[List[str]] = None) -> str:
    """Generate DTO class with validation."""

    output = [f"export class {name}DTO {{"]

    # Properties
    if properties:
        for prop in properties:
            prop_name, prop_type, is_optional, _ = parse_property(prop)

            if is_optional:
                output.append(f"  {prop_name}?: {prop_type};")
            else:
                output.append(f"  {prop_name}!: {prop_type};")

    output.append("")

    # Constructor
    output.append(f"  constructor(data: Partial<{name}DTO>) {{")
    output.append("    Object.assign(this, data);")
    output.append("    this.validate();")
    output.append("  }")
    output.append("")

    # Validation method
    output.append("  private validate(): void {")
    if properties:
        for prop in properties:
            prop_name, _, is_optional, _ = parse_property(prop)

            if not is_optional:
                output.append(f"    if (this.{prop_name} === undefined) {{")
                output.append(f"      throw new Error('{prop_name} is required');")
                output.append("    }")
    output.append("  }")
    output.append("")

    # toJSON method
    output.append("  toJSON(): Record<string, unknown> {")
    output.append("    return { ...this };")
    output.append("  }")
    output.append("}")

    return "\n".join(output)


def generate_enum(name: str, values: List[str]) -> str:
    """Generate TypeScript enum."""

    output = [f"export enum {name} {{"]

    for value in values:
        if "=" in value:
            parts = value.split("=")
            key = parts[0].strip()
            val = parts[1].strip()
            output.append(f"  {key} = {val},")
        else:
            # Auto generate string value
            output.append(f"  {value} = '{value.lower()}',")

    output.append("}")

    return "\n".join(output)


def generate_utility_types(base_type: str) -> str:
    """Generate common utility types for a base type."""

    return f"""// Utility types for {base_type}
export type {base_type}ID = {base_type}['id'];
export type Partial{base_type} = Partial<{base_type}>;
export type {base_type}WithoutID = Omit<{base_type}, 'id'>;
export type {base_type}Keys = keyof {base_type};
export type {base_type}Values = {base_type}[{base_type}Keys];

// Create type (for new entities)
export type Create{base_type} = Omit<{base_type}, 'id' | 'createdAt' | 'updatedAt'>;

// Update type (all optional except ID)
export type Update{base_type} = Partial<Omit<{base_type}, 'id'>> & {{ id: {base_type}['id'] }};

// Response wrapper
export interface {base_type}Response {{
  data: {base_type};
  meta?: {{
    timestamp: string;
    version: string;
  }};
}}

// List response
export interface {base_type}ListResponse {{
  data: {base_type}[];
  pagination: {{
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  }};
}}"""


def generate_api_client(name: str) -> str:
    """Generate typed API client class."""

    return f"""export class {name}ApiClient {{
  constructor(
    private readonly baseUrl: string,
    private readonly headers: HeadersInit = {{}}
  ) {{}}

  private async request<T>(
    endpoint: string,
    options: RequestInit = {{}}
  ): Promise<T> {{
    const response = await fetch(
      `${{this.baseUrl}}${{endpoint}}`,
      {{
        ...options,
        headers: {{
          'Content-Type': 'application/json',
          ...this.headers,
          ...options.headers,
        }},
      }}
    );

    if (!response.ok) {{
      throw new Error(`HTTP error! status: ${{response.status}}`);
    }}

    return response.json() as Promise<T>;
  }}

  async get{name}(id: number): Promise<{name}> {{
    return this.request<{name}>(`/{name.lower()}s/${{id}}`);
  }}

  async list{name}s(params?: {{
    page?: number;
    pageSize?: number;
    sort?: string;
    filter?: Record<string, unknown>;
  }}): Promise<{name}ListResponse> {{
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.pageSize) query.append('pageSize', params.pageSize.toString());
    if (params?.sort) query.append('sort', params.sort);
    if (params?.filter) {{
      Object.entries(params.filter).forEach(([key, value]) => {{
        query.append(`filter[${{key}}]`, String(value));
      }});
    }}

    return this.request<{name}ListResponse>(
      `/{name.lower()}s?${{query.toString()}}`
    );
  }}

  async create{name}(data: Create{name}): Promise<{name}> {{
    return this.request<{name}>(`/{name.lower()}s`, {{
      method: 'POST',
      body: JSON.stringify(data),
    }});
  }}

  async update{name}(id: number, data: Update{name}): Promise<{name}> {{
    return this.request<{name}>(`/{name.lower()}s/${{id}}`, {{
      method: 'PATCH',
      body: JSON.stringify(data),
    }});
  }}

  async delete{name}(id: number): Promise<void> {{
    await this.request<void>(`/{name.lower()}s/${{id}}`, {{
      method: 'DELETE',
    }});
  }}
}}"""


def main():
    parser = argparse.ArgumentParser(description="Generate TypeScript interfaces and types")
    parser.add_argument("name", help="Interface/Type name")
    parser.add_argument("-p", "--properties", nargs="+", help="Properties (format: name:type or name?:type)")
    parser.add_argument(
        "-t", "--type",
        choices=["interface", "dto", "enum", "guard", "utility", "api"],
        default="interface",
        help="Type of output to generate",
    )
    parser.add_argument("-e", "--extends", help="Interface to extend from")
    parser.add_argument("-v", "--values", nargs="+", help="Enum values")
    parser.add_argument("-c", "--check", help="Property to check in type guard (fallback when no --properties)")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write output to FILE instead of stdout")

    args = parser.parse_args()

    if args.type == "interface":
        output = generate_interface(args.name, args.properties, args.extends)
    elif args.type == "dto":
        output = generate_dto_class(args.name, args.properties)
    elif args.type == "enum":
        if not args.values:
            print("Error: Enum requires --values", file=sys.stderr)
            sys.exit(1)
        output = generate_enum(args.name, args.values)
    elif args.type == "guard":
        check_prop = args.check or "id"
        output = generate_interface(args.name, args.properties, args.extends)
        output += "\n\n"
        output += generate_type_guard(args.name, args.properties, check_prop)
    elif args.type == "utility":
        output = generate_utility_types(args.name)
    elif args.type == "api":
        output = generate_api_client(args.name)
    else:
        output = generate_interface(args.name, args.properties, args.extends)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
