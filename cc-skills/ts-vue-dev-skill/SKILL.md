---
name: ts-vue-dev-skill
description: TypeScript 5.x and Vue 3 development specialist for enterprise frontend applications. Use when writing TypeScript code, creating Vue 3 components, building composables, working with Pinia stores, implementing type guards, generic patterns, discriminated unions, or any frontend development task. Covers TypeScript strict mode enforcement, Vue 3 Composition API with script setup, typed props and emits, reactive patterns, provide/inject, async components, form handling, and component testing with Vitest. Activates autonomously when TypeScript, Vue, or frontend code context is detected.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
metadata:
  author: Mattia Costantini
  version: "1.0.0"
  domain: language
  triggers: typescript ts vue component composable pinia ref computed watch props emit template
  role: specialist
  scope: implementation
  output-format: code
  autonomy: true
  related-skills: coding-standards-skill, ears-doc-skill, postgresql16-dev-skill
---

# TypeScript & Vue 3 Development — Enterprise Edition

Specialist skill for writing production-grade TypeScript 5.x and Vue 3 frontend applications.
Apply the **coding-standards-skill** methodology (Pre-Implementation Analysis, Critical Thinking, Quality Checklist) before building components or designing frontend architecture.

---

## TypeScript — Non-Negotiable Rules

### Strict Mode — Always

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### Readonly for Immutable Properties — Always

```typescript
interface ContractPremium {
    readonly contractId: number;
    readonly amountCents: number;
    readonly currency: string;
    readonly effectiveDate: string;
}
```

### Type Guards for Runtime Validation

```typescript
function isContractPremium(value: unknown): value is ContractPremium {
    if (typeof value !== 'object' || value === null) return false;
    const obj = value as Record<string, unknown>;
    return (
        typeof obj.contractId === 'number' &&
        typeof obj.amountCents === 'number' &&
        typeof obj.currency === 'string' &&
        typeof obj.effectiveDate === 'string'
    );
}
```

### Exhaustive Checking — Always on Union Types

```typescript
type ImportStatus = 'pending' | 'processing' | 'completed' | 'failed';

function statusLabel(status: ImportStatus): string {
    switch (status) {
        case 'pending': return 'In attesa';
        case 'processing': return 'In elaborazione';
        case 'completed': return 'Completato';
        case 'failed': return 'Fallito';
        default:
            const _exhaustive: never = status;
            throw new Error(`Unhandled status: ${status}`);
    }
}
```

---

## Vue 3 — Non-Negotiable Rules

### Always Use Composition API with Script Setup

```vue
<script setup lang="ts">
import { computed, ref } from 'vue';
import type { ContractPremium } from '@/types';

// Props with TypeScript — ALWAYS typed
interface Props {
    premium: ContractPremium;
    editable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
    editable: false,
});

// Typed emits — ALWAYS
const emit = defineEmits<{
    update: [premium: ContractPremium];
    delete: [contractId: number];
}>();

// Reactive state
const isLoading = ref(false);

// Computed with type inference
const formattedAmount = computed(() =>
    new Intl.NumberFormat('it-IT', {
        style: 'currency',
        currency: props.premium.currency,
    }).format(props.premium.amountCents / 100)
);
</script>
```

### Component Structure Order

1. `<template>` — markup first
2. `<script setup lang="ts">` — logic
3. `<style scoped lang="scss">` — styles (always scoped)

Within `<script setup>`:
1. Imports
2. Types/Interfaces
3. Props with `defineProps<T>()`
4. Emits with `defineEmits<T>()`
5. Reactive state (`ref`, `reactive`)
6. Computed properties
7. Methods
8. Lifecycle hooks (`onMounted`, `onUnmounted`)
9. Watchers

### Composables — Reusable Logic

Extract shared logic into composables (`use*` pattern). Return reactive state as `readonly` where consumers shouldn't mutate directly.

```typescript
export function useUser(userId: Ref<number> | number) {
    const user = ref<User | null>(null);
    const loading = ref(false);
    const error = ref<Error | null>(null);

    async function fetchUser(): Promise<void> {
        loading.value = true;
        try {
            const response = await fetch(`/api/users/${unref(userId)}`);
            user.value = await response.json();
        } catch (err) {
            error.value = err as Error;
        } finally {
            loading.value = false;
        }
    }

    return {
        user: readonly(user),
        loading: readonly(loading),
        error: readonly(error),
        fetchUser,
    };
}
```

### Pinia Stores — Prefer Setup Syntax

```typescript
export const useUserStore = defineStore('user', () => {
    const users = ref<User[]>([]);
    const currentUser = ref<User | null>(null);
    const loading = ref(false);

    const activeUsers = computed(() =>
        users.value.filter(user => user.active)
    );

    async function fetchUsers() {
        loading.value = true;
        try {
            const response = await fetch('/api/users');
            users.value = await response.json();
        } finally {
            loading.value = false;
        }
    }

    return {
        users: readonly(users),
        currentUser,
        loading: readonly(loading),
        activeUsers,
        fetchUsers,
    };
});
```

---

## Advanced TypeScript Patterns

### Discriminated Unions

```typescript
type Result<T> =
    | { success: true; data: T }
    | { success: false; error: Error };
```

### Branded Types (Nominal Typing)

```typescript
type Brand<K, T> = K & { __brand: T };
type UserId = Brand<number, 'UserId'>;
type PostId = Brand<number, 'PostId'>;
```

### Utility Types

```typescript
type DeepReadonly<T> = {
    readonly [K in keyof T]: T[K] extends object
        ? DeepReadonly<T[K]>
        : T[K];
};

type StrictOmit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
```

---

## Vue 3 Advanced Patterns

### Type-Safe Provide/Inject

```typescript
import type { InjectionKey, Ref } from 'vue';
export const userKey: InjectionKey<Ref<User>> = Symbol('user');
```

### Async Components with States

```typescript
const AsyncComponent = defineAsyncComponent({
    loader: () => import('./HeavyComponent.vue'),
    loadingComponent: LoadingSpinner,
    errorComponent: ErrorDisplay,
    delay: 200,
    timeout: 3000,
});
```

### v-memo for List Optimization

```vue
<div v-for="item in list" :key="item.id" v-memo="[item.id, item.updated]">
    <ExpensiveComponent :item="item" />
</div>
```

### v-model with Computed

```vue
<script setup lang="ts">
const props = defineProps<{ modelValue: string }>();
const emit = defineEmits<{ 'update:modelValue': [value: string] }>();

const value = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val),
});
</script>

<template>
    <input v-model="value" />
</template>
```

---

## Testing Patterns

### Component Testing with Vitest

```typescript
import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import MyComponent from './MyComponent.vue';

describe('MyComponent', () => {
    it('emits update event', async () => {
        const wrapper = mount(MyComponent, {
            props: { user: { id: 1, name: 'Test' } },
        });

        await wrapper.find('button').trigger('click');

        expect(wrapper.emitted('update')).toBeTruthy();
        expect(wrapper.emitted('update')![0]).toEqual([1, { name: 'Updated' }]);
    });
});
```

### Type-Safe Mocks

```typescript
type DeepPartialMock<T> = {
    [P in keyof T]?: T[P] extends (...args: any[]) => any
        ? jest.Mock<ReturnType<T[P]>, Parameters<T[P]>>
        : T[P] extends object
        ? DeepPartialMock<T[P]>
        : T[P];
};

function createMock<T>(partial: DeepPartialMock<T> = {}): T {
    return partial as T;
}
```

---

## Auto-Loading Rules

| Condition | File to Load |
|-----------|-------------|
| TypeScript interface, type guard, generics, utility types | `references/typescript_patterns.md` |
| Vue component, composable, reactivity, Pinia, provide/inject | `references/vue3_patterns.md` |

When in doubt, load the reference. Better to have it and not need it.

---

## Available Scripts

**generate_vue_component.py** — Generate Vue 3 Composition API components
```bash
python3 scripts/generate_vue_component.py UserList --props userId:number userName:string --emits update delete
```

**generate_ts_interface.py** — Generate TypeScript interfaces and types
```bash
python3 scripts/generate_ts_interface.py User -p id:number email:string roles:string[]
python3 scripts/generate_ts_interface.py User -t guard -c id
python3 scripts/generate_ts_interface.py User -t utility
python3 scripts/generate_ts_interface.py User -t api
```

---

## Critical Reminders

- **ALWAYS** TypeScript strict mode — all flags enabled.
- **ALWAYS** `<script setup lang="ts">` — never Options API.
- **ALWAYS** typed props with `defineProps<T>()` and typed emits with `defineEmits<T>()`.
- **ALWAYS** exhaustive checking on union types with `never`.
- **PREFER** composables over mixins — mixins are legacy.
- **PREFER** `readonly` on refs returned from composables.
- **PREFER** Pinia setup syntax over options syntax.
- **PREFER** `shallowRef` for large objects that change entirely.
