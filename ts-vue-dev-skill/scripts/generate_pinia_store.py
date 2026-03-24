#!/usr/bin/env python3
"""Generate Pinia setup-style store with TypeScript."""

import argparse
import sys
from typing import List, Optional


def parse_name_type(entry: str):
    """Parse a 'name:type' string into (name, type)."""
    parts = entry.split(":", 1)
    return parts[0], parts[1].strip() if len(parts) > 1 else "unknown"


def to_pascal_case(name: str) -> str:
    """Convert camelCase or lowercase to PascalCase."""
    return name[0].upper() + name[1:] if name else name


def generate_pinia_store(
    name: str,
    state: Optional[List[str]] = None,
    getters: Optional[List[str]] = None,
    actions: Optional[List[str]] = None,
    with_persist: bool = False,
) -> str:
    """Generate a Pinia setup-style store."""

    store_fn = f"use{to_pascal_case(name)}Store"

    # Build state refs
    state_lines = []
    state_names = []
    if state:
        for entry in state:
            field_name, field_type = parse_name_type(entry)
            state_names.append(field_name)
            # Detect nullable types for proper ref initialisation
            if field_type.endswith("[]"):
                state_lines.append(f"  const {field_name} = ref<{field_type}>([]);")
            elif field_type == "boolean":
                state_lines.append(f"  const {field_name} = ref<{field_type}>(false);")
            elif field_type == "number":
                state_lines.append(f"  const {field_name} = ref<{field_type}>(0);")
            elif "|" in field_type and "null" in field_type:
                state_lines.append(f"  const {field_name} = ref<{field_type}>(null);")
            elif field_type == "string":
                state_lines.append(f"  const {field_name} = ref<{field_type}>('');")
            else:
                state_lines.append(f"  const {field_name} = ref<{field_type} | null>(null);")

    # Default state when none provided
    if not state_lines:
        state_lines = [
            f"  const {name}s = ref<unknown[]>([]);",
            "  const loading = ref<boolean>(false);",
            "  const error = ref<string | null>(null);",
        ]
        state_names = [f"{name}s", "loading", "error"]

    # Build getters (computed)
    getter_lines = []
    if getters:
        for getter in getters:
            # Pick the first state field as the basis for the TODO body
            base = state_names[0] if state_names else "undefined"
            getter_lines.append(
                f"  const {getter} = computed(() => {{\n"
                f"    // TODO: implement\n"
                f"    return {base}.value;\n"
                f"  }});"
            )

    # Build actions (async functions)
    action_lines = []
    if actions:
        loading_field = next(
            (n for n in state_names if "loading" in n.lower()), None
        )
        error_field = next(
            (n for n in state_names if "error" in n.lower()), None
        )
        for action in actions:
            lines = [f"  async function {action}(): Promise<void> {{"]
            if loading_field:
                lines.append(f"    {loading_field}.value = true;")
            if error_field:
                lines.append(f"    {error_field}.value = null;")
            lines.append("    try {")
            lines.append("      // TODO: implement")
            lines.append("    } catch (e) {")
            if error_field:
                lines.append(
                    f"      {error_field}.value = e instanceof Error ? e.message : 'Unknown error';"
                )
            else:
                lines.append("      console.error(e);")
            lines.append("    } finally {")
            if loading_field:
                lines.append(f"      {loading_field}.value = false;")
            lines.append("    }")
            lines.append("  }")
            action_lines.append("\n".join(lines))

    # Build return block
    return_state = "\n".join(f"    {n}: readonly({n})," for n in state_names)
    return_getters = "\n".join(f"    {g}," for g in (getters or []))
    return_actions = "\n".join(f"    {a}," for a in (actions or []))

    return_sections = []
    if state_names:
        return_sections.append("    // State\n" + return_state)
    if getters:
        return_sections.append("    // Getters\n" + return_getters)
    if actions:
        return_sections.append("    // Actions\n" + return_actions)
    return_block = "\n".join(return_sections)

    # Assemble body sections
    body_parts = []

    if state_lines:
        body_parts.append("  // State\n" + "\n".join(state_lines))
    if getter_lines:
        body_parts.append("  // Getters\n" + "\n\n".join(getter_lines))
    if action_lines:
        body_parts.append("  // Actions\n" + "\n\n".join(action_lines))

    body = "\n\n".join(body_parts)

    # Persist comment
    persist_comment = ""
    if with_persist:
        persist_comment = (
            "\n// Persistence: wrap with persistedState plugin\n"
            "// e.g. import { useStorage } from '@vueuse/core';\n"
        )

    # Usage hint: pick first two state names
    hint_refs = ", ".join(state_names[:2]) if state_names else name
    usage_hint = f"// Usage: const {{ {hint_refs} }} = storeToRefs({store_fn}());"

    store = (
        f"import {{ ref, computed, readonly }} from 'vue';\n"
        f"import {{ defineStore }} from 'pinia';\n"
        f"{persist_comment}\n"
        f"export const {store_fn} = defineStore('{name}', () => {{\n"
        f"{body}\n\n"
        f"  return {{\n"
        f"{return_block}\n"
        f"  }};\n"
        f"}});\n\n"
        f"{usage_hint}\n"
    )

    return store


def main():
    parser = argparse.ArgumentParser(description="Generate Pinia setup-style store with TypeScript")
    parser.add_argument("name", help="Store name (camelCase, e.g. 'user')")
    parser.add_argument(
        "-s", "--state",
        metavar="name:type",
        help="Comma-separated state fields (e.g. 'users:User[],loading:boolean,error:string|null')",
    )
    parser.add_argument(
        "-g", "--getters",
        metavar="GETTER_NAMES",
        help="Comma-separated getter names",
    )
    parser.add_argument(
        "-a", "--actions",
        metavar="ACTION_NAMES",
        help="Comma-separated async action names",
    )
    parser.add_argument(
        "--with-persist",
        action="store_true",
        help="Add persistence plugin comment",
    )
    parser.add_argument("-o", "--output", metavar="FILE", help="Write output to FILE instead of stdout")

    args = parser.parse_args()

    state = [s.strip() for s in args.state.split(",")] if args.state else None
    getters = [g.strip() for g in args.getters.split(",")] if args.getters else None
    actions = [a.strip() for a in args.actions.split(",")] if args.actions else None

    output = generate_pinia_store(
        args.name,
        state=state,
        getters=getters,
        actions=actions,
        with_persist=args.with_persist,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
