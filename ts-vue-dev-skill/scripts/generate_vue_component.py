#!/usr/bin/env python3
"""Generate Vue 3 Composition API component with TypeScript."""

import argparse
import sys
from typing import List, Optional


def generate_vue_component(
    name: str,
    props: Optional[List[str]] = None,
    emits: Optional[List[str]] = None,
    with_store: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """Generate a Vue 3 component with script setup and TypeScript."""

    # Parse props into interface
    props_interface = ""
    props_defaults = ""
    if props:
        prop_lines = []
        defaults = []
        for prop in props:
            parts = prop.split(":", 1)
            prop_name = parts[0]
            prop_type = parts[1] if len(parts) > 1 else "unknown"

            # Check for optional prop (ending with ?)
            is_optional = prop_name.endswith("?")
            if is_optional:
                prop_name = prop_name[:-1]
                prop_lines.append(f"  {prop_name}?: {prop_type};")
            else:
                prop_lines.append(f"  {prop_name}: {prop_type};")

            # Add default for optional props
            if is_optional:
                if prop_type == "boolean":
                    defaults.append(f"  {prop_name}: false")
                elif prop_type == "number":
                    defaults.append(f"  {prop_name}: 0")
                elif prop_type == "string":
                    defaults.append(f"  {prop_name}: ''")

        props_interface = "interface Props {\n" + "\n".join(prop_lines) + "\n}\n"
        if defaults:
            defaults_body = ",\n".join(defaults)
            props_defaults = f", {{\n{defaults_body}\n}}"

    # Parse emits
    emits_interface = ""
    if emits:
        emit_lines = []
        for emit in emits:
            parts = emit.split(":", 1)
            emit_name = parts[0]
            emit_payload = parts[1] if len(parts) > 1 else "void"

            if emit_payload == "void":
                emit_lines.append(f"  {emit_name}: [];")
            else:
                emit_lines.append(f"  {emit_name}: [{emit_payload}];")

        emits_interface = "\nconst emit = defineEmits<{\n" + "\n".join(emit_lines) + "\n}>();"

    # defineModel support
    model_line = ""
    if model:
        model_parts = model.split(":", 1)
        model_type = model_parts[1] if len(model_parts) > 1 else "string"
        model_name = model_parts[0] if len(model_parts) > 1 else "modelValue"
        if model_name == "modelValue":
            model_line = f"\nconst modelValue = defineModel<{model_type}>();"
        else:
            model_line = f"\nconst {model_name} = defineModel<{model_type}>('{model_name}');"

    # Store import
    store_import = ""
    store_usage = ""
    if with_store:
        store_camel = with_store[0].lower() + with_store[1:] if with_store else ""
        store_fn = f"use{with_store[0].upper() + with_store[1:]}"
        store_import = f"import {{ {store_fn} }} from '@/stores/{store_camel}';"
        store_usage = f"\nconst store = {store_fn}();"

    # Generate component template
    template = f"""<template>
  <div class="{name.lower()}-container">
    <div v-if="isLoading" class="loading">
      Loading...
    </div>
    <div v-else class="content">
      <!-- Component content here -->
      <h2>{{{{ title }}}}</h2>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ ref, computed, onMounted }} from 'vue';
{store_import}

{props_interface if props else ""}\
{f"const props = defineProps<Props>(){props_defaults};" if props else ""}\
{emits_interface if emits else ""}\
{model_line if model else ""}

// State
const isLoading = ref(false);
const data = ref<Record<string, unknown> | null>(null);
const error = ref<Error | null>(null);
{store_usage}

// Computed
const title = computed(() => '{name} Component');

// Methods
async function loadData(): Promise<void> {{
  isLoading.value = true;
  error.value = null;

  try {{
    // Implement data loading
    await new Promise(resolve => setTimeout(resolve, 1000));
    data.value = {{ loaded: true }};
  }} catch (err) {{
    error.value = err instanceof Error ? err : new Error('Unknown error');
    console.error('Failed to load data:', err);
  }} finally {{
    isLoading.value = false;
  }}
}}

// Lifecycle
onMounted(() => {{
  loadData();
}});
</script>

<style scoped lang="scss">
.{name.lower()}-container {{
  padding: 1rem;

  .loading {{
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
    color: #666;
  }}

  .content {{
    h2 {{
      margin-bottom: 1rem;
      color: #333;
    }}
  }}
}}
</style>
"""

    return template


def generate_composable(
    name: str,
    state: Optional[List[str]] = None,
    options: Optional[List[str]] = None,
    with_fetch: bool = False,
    with_cleanup: bool = False,
) -> str:
    """Generate a Vue 3 composable with TypeScript."""

    # Parse state entries
    state_lines = []
    return_fields = []
    if state:
        for entry in state:
            parts = entry.split(":", 1)
            field_name = parts[0]
            field_type = parts[1] if len(parts) > 1 else "unknown"
            state_lines.append(f"  const {field_name} = ref<{field_type} | null>(null);")
            return_fields.append(field_name)
    else:
        state_lines.append("  const data = ref<Record<string, unknown> | null>(null);")
        return_fields.append("data")

    # Parse options entries
    options_params = ""
    options_interface_lines = []
    if options:
        for opt in options:
            parts = opt.split(":", 1)
            opt_name = parts[0]
            opt_type = parts[1] if len(parts) > 1 else "unknown"
            options_interface_lines.append(f"  {opt_name}?: {opt_type};")
        options_params = f"options: Use{name}Options = {{}}"
    else:
        options_params = f"options: Use{name}Options = {{}}"

    options_interface = ""
    if options_interface_lines:
        options_interface = (
            f"interface Use{name}Options {{\n"
            + "\n".join(options_interface_lines)
            + "\n}\n\n"
        )
    else:
        options_interface = f"interface Use{name}Options {{\n  // Add options here\n}}\n\n"

    # Loading / error state (always present)
    loading_line = "  const isLoading = ref(false);"
    error_line = "  const error = ref<Error | null>(null);"

    # Fetch block
    fetch_block = ""
    if with_fetch:
        fetch_block = f"""
  async function fetch(url: string): Promise<void> {{
    isLoading.value = true;
    error.value = null;

    try {{
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
      const json = await response.json();
      {'data' if not state else return_fields[0]}.value = json;
    }} catch (err) {{
      error.value = err instanceof Error ? err : new Error('Failed to fetch');
      throw err;
    }} finally {{
      isLoading.value = false;
    }}
  }}
"""

    # Cleanup block
    cleanup_block = ""
    if with_cleanup:
        cleanup_block = """
  onUnmounted(() => {
    // Cleanup resources here
  });
"""

    # Build return statement
    all_returns = return_fields + ["isLoading", "error"]
    if with_fetch:
        all_returns.append("fetch")

    readonly_returns = [f"    {f}: readonly({f})," for f in return_fields + ["isLoading", "error"]]
    method_returns = []
    if with_fetch:
        method_returns.append("    fetch,")

    return_block = "\n".join(readonly_returns + method_returns)

    # Imports
    imports = ["ref", "readonly"]
    if with_cleanup:
        imports.append("onUnmounted")
    imports_str = ", ".join(imports)

    state_block = "\n".join(state_lines)

    composable = f"""import {{ {imports_str} }} from 'vue';

{options_interface}export function use{name}({options_params}) {{
  // State
{state_block}
{loading_line}
{error_line}
{fetch_block}{cleanup_block}
  return {{
{return_block}
  }};
}}
"""

    return composable


def main():
    parser = argparse.ArgumentParser(description="Generate Vue 3 component with TypeScript")
    parser.add_argument("name", help="Component name (PascalCase)")
    parser.add_argument("-p", "--props", nargs="+", help="Props (format: name:type or name?:type for optional)")
    parser.add_argument("-e", "--emits", nargs="+", help="Emits (format: name or name:payload)")
    parser.add_argument("-c", "--composable", action="store_true", help="Generate composable instead of component")
    parser.add_argument(
        "-s", "--store",
        metavar="STORE_NAME",
        help="Include Pinia store integration (provide store name, e.g. UserStore)",
    )
    parser.add_argument(
        "--model",
        metavar="NAME:TYPE",
        help="Add defineModel support (e.g. modelValue:string or title:string)",
    )
    # Composable-specific flags
    parser.add_argument("--state", nargs="+", help="Composable state (format: name:type)")
    parser.add_argument("--options", nargs="+", help="Composable option params (format: name:type)")
    parser.add_argument("--with-fetch", action="store_true", help="Add fetch pattern to composable")
    parser.add_argument("--with-cleanup", action="store_true", help="Add onUnmounted cleanup to composable")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write output to FILE instead of stdout")

    args = parser.parse_args()

    if args.composable:
        output = generate_composable(
            args.name,
            state=args.state,
            options=args.options,
            with_fetch=args.with_fetch,
            with_cleanup=args.with_cleanup,
        )
    else:
        output = generate_vue_component(
            args.name,
            args.props,
            args.emits,
            with_store=args.store,
            model=args.model,
        )

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
