#!/usr/bin/env python3
"""Generate Vue 3 composable with TypeScript."""

import argparse
import sys
from typing import List, Optional


def parse_name_type(entry: str):
    """Parse a 'name:type' string into (name, type)."""
    parts = entry.split(":", 1)
    return parts[0].strip(), parts[1].strip() if len(parts) > 1 else "unknown"


def to_pascal_case(name: str) -> str:
    """Convert first character to uppercase."""
    return name[0].upper() + name[1:] if name else name


def generate_vue_composable(
    name: str,
    state: Optional[List[str]] = None,
    options: Optional[List[str]] = None,
    with_fetch: Optional[str] = None,
    with_cleanup: bool = False,
) -> str:
    """Generate a typed Vue 3 composable."""

    # Strip leading 'use' for interface naming if present
    base_name = name[3:] if name.startswith("use") else name
    options_iface = f"Use{to_pascal_case(base_name)}Options"
    return_iface = f"Use{to_pascal_case(base_name)}Return"

    # Parse state fields
    state_entries = []
    if state:
        for entry in state:
            field_name, field_type = parse_name_type(entry)
            state_entries.append((field_name, field_type))
    else:
        # Default: data, loading, error
        state_entries = [
            ("data", "unknown"),
            ("loading", "boolean"),
            ("error", "string | null"),
        ]

    # Ensure loading / error are always present
    state_names = [n for n, _ in state_entries]
    has_loading = any("loading" in n.lower() for n in state_names)
    has_error = any("error" in n.lower() for n in state_names)

    # Parse options
    options_iface_lines = []
    if options:
        for opt in options:
            opt_name, opt_type = parse_name_type(opt)
            options_iface_lines.append(f"  {opt_name}?: {opt_type};")
    else:
        options_iface_lines = ["  // Add options here"]

    # Build Options interface
    options_interface_block = (
        f"interface {options_iface} {{\n"
        + "\n".join(options_iface_lines)
        + "\n}\n"
    )

    # Build Return interface
    return_iface_lines = []
    for field_name, field_type in state_entries:
        return_iface_lines.append(
            f"  readonly {field_name}: Readonly<Ref<{field_type}>>;"
        )
    if with_fetch:
        return_iface_lines.append("  fetch: () => Promise<void>;")
    return_iface_lines.append("  reset: () => void;")

    return_interface_block = (
        f"interface {return_iface} {{\n"
        + "\n".join(return_iface_lines)
        + "\n}\n"
    )

    # Imports
    imports = ["ref", "readonly"]
    if with_cleanup:
        imports.append("onUnmounted")
    imports.append("type Ref")
    imports_str = ", ".join(imports)

    # State declarations
    state_decl_lines = []
    for field_name, field_type in state_entries:
        if field_type.endswith("[]"):
            init = "[]"
        elif field_type == "boolean":
            init = "false"
        elif field_type == "number":
            init = "0"
        elif "|" in field_type and "null" in field_type:
            init = "null"
        elif field_type == "string":
            init = "''"
        else:
            init = "null"
            field_type = f"{field_type} | null"
        state_decl_lines.append(f"  const {field_name} = ref<{field_type}>({init});")

    state_block = "\n".join(state_decl_lines)

    # Fetch function
    fetch_block = ""
    loading_field = next(
        (n for n, _ in state_entries if "loading" in n.lower()), None
    )
    error_field = next(
        (n for n, _ in state_entries if "error" in n.lower()), None
    )
    data_field = next(
        (n for n, _ in state_entries if n not in ("loading", "error")), None
    ) or "data"

    if with_fetch:
        url = with_fetch
        fetch_lines = ["  async function fetch(): Promise<void> {"]
        if loading_field:
            fetch_lines.append(f"    {loading_field}.value = true;")
        if error_field:
            fetch_lines.append(f"    {error_field}.value = null;")
        fetch_lines.append("    try {")
        fetch_lines.append(f"      const response = await globalThis.fetch('{url}');")
        fetch_lines.append(
            "      if (!response.ok) throw new Error(`HTTP ${response.status}`);"
        )
        fetch_lines.append(f"      {data_field}.value = await response.json();")
        fetch_lines.append("    } catch (e) {")
        if error_field:
            fetch_lines.append(
                f"      {error_field}.value = e instanceof Error ? e.message : 'Unknown error';"
            )
        else:
            fetch_lines.append("      console.error(e);")
        fetch_lines.append("    } finally {")
        if loading_field:
            fetch_lines.append(f"      {loading_field}.value = false;")
        fetch_lines.append("    }")
        fetch_lines.append("  }")
        fetch_block = "\n".join(fetch_lines)

    # Reset function
    reset_lines = ["  function reset(): void {"]
    for field_name, field_type in state_entries:
        if field_type.endswith("[]") or ("|" in field_type and "null" in field_type):
            if field_type.endswith("[]"):
                reset_lines.append(f"    {field_name}.value = [];")
            else:
                reset_lines.append(f"    {field_name}.value = null;")
        elif field_type == "boolean":
            reset_lines.append(f"    {field_name}.value = false;")
        elif field_type == "number":
            reset_lines.append(f"    {field_name}.value = 0;")
        elif field_type == "string":
            reset_lines.append(f"    {field_name}.value = '';")
        else:
            reset_lines.append(f"    {field_name}.value = null;")
    reset_lines.append("  }")
    reset_block = "\n".join(reset_lines)

    # Cleanup block
    cleanup_block = ""
    if with_cleanup:
        cleanup_block = (
            "\n  // Cleanup\n"
            "  onUnmounted(() => {\n"
            "    // TODO: cancel pending requests\n"
            "  });\n"
        )

    # Return block
    return_lines = []
    for field_name, _ in state_entries:
        return_lines.append(f"    {field_name}: readonly({field_name}),")
    if with_fetch:
        return_lines.append("    fetch,")
    return_lines.append("    reset,")
    return_block = "\n".join(return_lines)

    # Compose function
    func_parts = []
    func_parts.append(state_block)
    if fetch_block:
        func_parts.append(fetch_block)
    func_parts.append(reset_block)
    if cleanup_block:
        func_parts.append(cleanup_block.strip())

    func_body = "\n\n".join(func_parts)

    composable = (
        f"import {{ {imports_str} }} from 'vue';\n\n"
        f"{options_interface_block}\n"
        f"{return_interface_block}\n"
        f"export function {name}(options: {options_iface} = {{}}): {return_iface} {{\n"
        f"{func_body}\n\n"
        f"  return {{\n"
        f"{return_block}\n"
        f"  }};\n"
        f"}}\n"
    )

    return composable


def main():
    parser = argparse.ArgumentParser(description="Generate Vue 3 composable with TypeScript")
    parser.add_argument("name", help="Composable name (e.g. 'useUsers')")
    parser.add_argument(
        "-s", "--state",
        metavar="name:type",
        help="Comma-separated state fields (e.g. 'data:User[],loading:boolean,error:string|null')",
    )
    parser.add_argument(
        "-o", "--options",
        metavar="name:type",
        help="Comma-separated option params with types (e.g. 'initialPage:number,pageSize:number')",
    )
    parser.add_argument(
        "--with-fetch",
        metavar="URL",
        help="Add fetch pattern targeting the given URL",
    )
    parser.add_argument(
        "--with-cleanup",
        action="store_true",
        help="Add onUnmounted cleanup hook",
    )
    parser.add_argument("-O", "--output", metavar="FILE", help="Write output to FILE instead of stdout")

    args = parser.parse_args()

    state = [s.strip() for s in args.state.split(",")] if args.state else None
    options = [o.strip() for o in args.options.split(",")] if args.options else None

    output = generate_vue_composable(
        args.name,
        state=state,
        options=options,
        with_fetch=args.with_fetch,
        with_cleanup=args.with_cleanup,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
