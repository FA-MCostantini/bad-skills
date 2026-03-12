#!/usr/bin/env python3
"""Generate Vue 3 Composition API component with TypeScript."""

import argparse
from typing import List, Optional

def generate_vue_component(
    name: str,
    props: Optional[List[str]] = None,
    emits: Optional[List[str]] = None,
    with_store: bool = False
) -> str:
    """Generate a Vue 3 component with script setup and TypeScript."""
    
    # Parse props into interface
    props_interface = ""
    props_defaults = ""
    if props:
        prop_lines = []
        defaults = []
        for prop in props:
            parts = prop.split(":")
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
            props_defaults = f", {{\n{',\\n'.join(defaults)}\n}}"
    
    # Parse emits
    emits_interface = ""
    if emits:
        emit_lines = []
        for emit in emits:
            parts = emit.split(":")
            emit_name = parts[0]
            emit_payload = parts[1] if len(parts) > 1 else "void"
            
            if emit_payload == "void":
                emit_lines.append(f"  {emit_name}: [];")
            else:
                emit_lines.append(f"  {emit_name}: [{emit_payload}];")
        
        emits_interface = "\nconst emit = defineEmits<{\n" + "\n".join(emit_lines) + "\n}>();"
    
    # Generate component template
    template = f"""<template>
  <div class="{name.lower()}-container">
    <div v-if="isLoading" class="loading">
      Loading...
    </div>
    <div v-else class="content">
      <!-- Component content here -->
      <h2>{{ title }}</h2>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ ref, computed, onMounted }} from 'vue';
{f"import {{ useStore }} from '@/stores';" if with_store else ""}

{props_interface if props else ""}
{f"const props = defineProps<Props>(){props_defaults};" if props else ""}{emits_interface if emits else ""}

// State
const isLoading = ref(false);
const data = ref<any>(null);
const error = ref<Error | null>(null);
{f"const store = useStore();" if with_store else ""}

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

def generate_composable(name: str) -> str:
    """Generate a Vue 3 composable with TypeScript."""
    
    composable = f"""import {{ ref, computed, Ref }} from 'vue';

interface Use{name}Options {{
  initialValue?: any;
  // Add options here
}}

interface Use{name}Return {{
  data: Ref<any>;
  isLoading: Ref<boolean>;
  error: Ref<Error | null>;
  load: () => Promise<void>;
  reset: () => void;
}}

export function use{name}(options: Use{name}Options = {{}}): Use{name}Return {{
  const {{ initialValue = null }} = options;
  
  // State
  const data = ref<any>(initialValue);
  const isLoading = ref(false);
  const error = ref<Error | null>(null);
  
  // Methods
  async function load(): Promise<void> {{
    isLoading.value = true;
    error.value = null;
    
    try {{
      // Implement loading logic
      const response = await fetch('/api/data');
      data.value = await response.json();
    }} catch (err) {{
      error.value = err instanceof Error ? err : new Error('Failed to load');
      throw err;
    }} finally {{
      isLoading.value = false;
    }}
  }}
  
  function reset(): void {{
    data.value = initialValue;
    isLoading.value = false;
    error.value = null;
  }}
  
  return {{
    data,
    isLoading,
    error,
    load,
    reset
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
    parser.add_argument("-s", "--store", action="store_true", help="Include Pinia store integration")
    
    args = parser.parse_args()
    
    if args.composable:
        output = generate_composable(args.name)
    else:
        output = generate_vue_component(args.name, args.props, args.emits, args.store)
    
    print(output)

if __name__ == "__main__":
    main()
