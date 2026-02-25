# Vue 3 Patterns & Best Practices

## Script Setup with TypeScript

### Component Structure
```vue
<template>
  <div class="component-name">
    <!-- Template here -->
  </div>
</template>

<script setup lang="ts">
// Imports first
import { ref, computed, watch, onMounted } from 'vue';
import type { PropType } from 'vue';

// Types/Interfaces
interface User {
  id: number;
  name: string;
}

// Props with TypeScript
interface Props {
  user: User;
  title?: string;
  maxItems?: number;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Default Title',
  maxItems: 10
});

// Emits with TypeScript
const emit = defineEmits<{
  update: [id: number, data: Partial<User>];
  delete: [id: number];
  'update:modelValue': [value: string];
}>();

// Reactive state
const isLoading = ref(false);
const items = ref<User[]>([]);

// Computed
const itemCount = computed(() => items.value.length);

// Methods
async function loadData(): Promise<void> {
  // Implementation
}

// Lifecycle
onMounted(() => {
  loadData();
});

// Watchers
watch(() => props.user.id, (newId) => {
  console.log('User ID changed:', newId);
});
</script>

<style scoped lang="scss">
.component-name {
  // Styles here
}
</style>
```

## Composables Pattern

### Basic Composable
```typescript
// composables/useUser.ts
import { ref, computed, Ref } from 'vue';
import type { User } from '@/types';

export function useUser(userId: Ref<number> | number) {
  // Normalize to ref
  const id = ref(userId);
  
  // State
  const user = ref<User | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);
  
  // Computed
  const hasUser = computed(() => user.value !== null);
  const userName = computed(() => user.value?.name ?? 'Unknown');
  
  // Methods
  async function fetchUser(): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch(`/api/users/${id.value}`);
      if (!response.ok) throw new Error('Failed to fetch user');
      user.value = await response.json();
    } catch (err) {
      error.value = err as Error;
      console.error('Error fetching user:', err);
    } finally {
      loading.value = false;
    }
  }
  
  async function updateUser(data: Partial<User>): Promise<void> {
    if (!user.value) return;
    
    loading.value = true;
    try {
      const response = await fetch(`/api/users/${id.value}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) throw new Error('Failed to update user');
      user.value = await response.json();
    } catch (err) {
      error.value = err as Error;
      throw err;
    } finally {
      loading.value = false;
    }
  }
  
  // Auto-fetch when ID changes
  watch(id, () => {
    if (id.value) fetchUser();
  }, { immediate: true });
  
  return {
    user: readonly(user),
    loading: readonly(loading),
    error: readonly(error),
    hasUser,
    userName,
    fetchUser,
    updateUser
  };
}
```

### Advanced Composable with Options
```typescript
// composables/useApi.ts
interface UseApiOptions<T> {
  immediate?: boolean;
  transform?: (data: any) => T;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  retryCount?: number;
  retryDelay?: number;
}

export function useApi<T>(
  url: string | Ref<string>,
  options: UseApiOptions<T> = {}
) {
  const {
    immediate = true,
    transform = (data) => data,
    onSuccess,
    onError,
    retryCount = 0,
    retryDelay = 1000
  } = options;
  
  const urlRef = ref(url);
  const data = ref<T | null>(null);
  const loading = ref(false);
  const error = ref<Error | null>(null);
  
  async function execute(retries = retryCount): Promise<void> {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await fetch(urlRef.value);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const rawData = await response.json();
      data.value = transform(rawData);
      
      onSuccess?.(data.value);
    } catch (err) {
      error.value = err as Error;
      
      if (retries > 0) {
        await new Promise(resolve => setTimeout(resolve, retryDelay));
        return execute(retries - 1);
      }
      
      onError?.(error.value);
    } finally {
      loading.value = false;
    }
  }
  
  if (immediate) {
    execute();
  }
  
  // Re-fetch when URL changes
  watch(urlRef, () => execute());
  
  return {
    data: readonly(data),
    loading: readonly(loading),
    error: readonly(error),
    execute,
    refresh: () => execute()
  };
}
```

## Provide/Inject Pattern

### Type-Safe Provide/Inject
```typescript
// injection-keys.ts
import type { InjectionKey, Ref } from 'vue';
import type { User, Store } from '@/types';

export const userKey: InjectionKey<Ref<User>> = Symbol('user');
export const storeKey: InjectionKey<Store> = Symbol('store');

// Provider component
import { provide } from 'vue';

const user = ref<User>({ id: 1, name: 'John' });
provide(userKey, user);

// Consumer component
import { inject } from 'vue';

const user = inject(userKey);
if (!user) {
  throw new Error('User injection not provided');
}

// With default value
const user = inject(userKey, ref({ id: 0, name: 'Guest' }));
```

### Plugin with Provide
```typescript
// plugins/auth.ts
import type { App, InjectionKey } from 'vue';

interface AuthPlugin {
  isAuthenticated: Ref<boolean>;
  login(credentials: Credentials): Promise<void>;
  logout(): void;
}

export const authKey: InjectionKey<AuthPlugin> = Symbol('auth');

export function createAuth(): AuthPlugin {
  const isAuthenticated = ref(false);
  
  return {
    isAuthenticated: readonly(isAuthenticated),
    async login(credentials) {
      // Implementation
      isAuthenticated.value = true;
    },
    logout() {
      isAuthenticated.value = false;
    }
  };
}

export default {
  install(app: App) {
    app.provide(authKey, createAuth());
  }
};
```

## Reactive Patterns

### Reactive Transform with toRefs
```typescript
function useMousePosition() {
  const position = reactive({
    x: 0,
    y: 0
  });
  
  function update(event: MouseEvent) {
    position.x = event.clientX;
    position.y = event.clientY;
  }
  
  onMounted(() => {
    window.addEventListener('mousemove', update);
  });
  
  onUnmounted(() => {
    window.removeEventListener('mousemove', update);
  });
  
  // Return refs for destructuring
  return toRefs(position);
}

// Usage with destructuring
const { x, y } = useMousePosition();
```

### shallowRef for Performance
```typescript
// For large objects that change completely
const largeData = shallowRef<ComplexData[]>([]);

// Update by replacing entire array
function updateData(newData: ComplexData[]) {
  largeData.value = newData; // Triggers reactivity
}

// Modifications to nested properties won't trigger updates
largeData.value[0].property = 'new'; // No reactivity
```

### triggerRef for Manual Updates
```typescript
const data = shallowRef({ count: 0 });

// This won't trigger reactivity
data.value.count++;

// Manually trigger update
triggerRef(data);
```

## Component Patterns

### Async Components
```typescript
import { defineAsyncComponent } from 'vue';

// Basic async component
const AsyncComponent = defineAsyncComponent(() =>
  import('./components/HeavyComponent.vue')
);

// With loading/error states
const AsyncComponentWithStates = defineAsyncComponent({
  loader: () => import('./components/HeavyComponent.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200, // Show loading after 200ms
  timeout: 3000, // Show error after 3s
  onError(error, retry, fail, attempts) {
    if (attempts <= 3) {
      retry(); // Retry up to 3 times
    } else {
      fail();
    }
  }
});
```

### Renderless Components
```vue
<!-- MouseTracker.vue -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const x = ref(0);
const y = ref(0);

function update(event: MouseEvent) {
  x.value = event.clientX;
  y.value = event.clientY;
}

onMounted(() => window.addEventListener('mousemove', update));
onUnmounted(() => window.removeEventListener('mousemove', update));
</script>

<template>
  <slot :x="x" :y="y" />
</template>

<!-- Usage -->
<MouseTracker v-slot="{ x, y }">
  <div>Mouse position: {{ x }}, {{ y }}</div>
</MouseTracker>
```

### Compound Components
```vue
<!-- Tabs.vue -->
<script setup lang="ts">
import { provide, ref, InjectionKey } from 'vue';

interface TabsContext {
  activeTab: Ref<string>;
  setActiveTab: (name: string) => void;
}

export const tabsKey: InjectionKey<TabsContext> = Symbol('tabs');

const activeTab = ref('');

function setActiveTab(name: string) {
  activeTab.value = name;
}

provide(tabsKey, { activeTab, setActiveTab });
</script>

<!-- Tab.vue -->
<script setup lang="ts">
import { inject, computed } from 'vue';
import { tabsKey } from './Tabs.vue';

const props = defineProps<{
  name: string;
  label: string;
}>();

const context = inject(tabsKey)!;
const isActive = computed(() => context.activeTab.value === props.name);

function activate() {
  context.setActiveTab(props.name);
}
</script>
```

## Performance Optimization

### v-memo for List Optimization
```vue
<template>
  <div v-for="item in list" :key="item.id" v-memo="[item.id, item.updated]">
    <!-- Only re-renders when item.id or item.updated changes -->
    <ExpensiveComponent :item="item" />
  </div>
</template>
```

### Keep-Alive with Lifecycle
```vue
<template>
  <keep-alive :max="10" :include="['ComponentA', 'ComponentB']">
    <component :is="currentComponent" />
  </keep-alive>
</template>

<script setup lang="ts">
import { onActivated, onDeactivated } from 'vue';

// Called when component is activated from keep-alive
onActivated(() => {
  console.log('Component activated');
  refreshData();
});

// Called when component is deactivated
onDeactivated(() => {
  console.log('Component deactivated');
  clearTimers();
});
</script>
```

### Lazy Hydration Pattern
```typescript
// composables/useLazyHydration.ts
export function useLazyHydration() {
  const isHydrated = ref(false);
  
  onMounted(() => {
    // Hydrate when idle
    requestIdleCallback(() => {
      isHydrated.value = true;
    });
  });
  
  return { isHydrated };
}

// Component usage
<template>
  <div>
    <div v-if="!isHydrated">
      <!-- Lightweight placeholder -->
      <div class="skeleton" />
    </div>
    <HeavyComponent v-else />
  </div>
</template>
```

## Form Handling

### Form Composable with Validation
```typescript
// composables/useForm.ts
interface ValidationRule<T> {
  validator: (value: T) => boolean;
  message: string;
}

interface FormField<T> {
  value: Ref<T>;
  error: Ref<string | null>;
  rules: ValidationRule<T>[];
  validate(): boolean;
  reset(): void;
}

export function useForm<T extends Record<string, any>>(
  initialValues: T,
  rules: Partial<Record<keyof T, ValidationRule<T[keyof T]>[]>> = {}
) {
  const fields: Record<string, FormField<any>> = {};
  const isValid = ref(true);
  
  // Create fields
  for (const key in initialValues) {
    const value = ref(initialValues[key]);
    const error = ref<string | null>(null);
    const fieldRules = rules[key] || [];
    
    fields[key] = {
      value,
      error,
      rules: fieldRules,
      validate() {
        error.value = null;
        for (const rule of fieldRules) {
          if (!rule.validator(value.value)) {
            error.value = rule.message;
            return false;
          }
        }
        return true;
      },
      reset() {
        value.value = initialValues[key];
        error.value = null;
      }
    };
  }
  
  // Form methods
  function validate(): boolean {
    let valid = true;
    for (const field of Object.values(fields)) {
      if (!field.validate()) {
        valid = false;
      }
    }
    isValid.value = valid;
    return valid;
  }
  
  function reset(): void {
    for (const field of Object.values(fields)) {
      field.reset();
    }
    isValid.value = true;
  }
  
  function getValues(): T {
    const values = {} as T;
    for (const key in fields) {
      values[key as keyof T] = fields[key].value.value;
    }
    return values;
  }
  
  return {
    fields,
    isValid: readonly(isValid),
    validate,
    reset,
    getValues
  };
}
```

### v-model with Computed
```vue
<script setup lang="ts">
// Two-way binding with computed
const props = defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const value = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});
</script>

<template>
  <input v-model="value" />
</template>
```

## Testing Patterns

### Component Testing with TypeScript
```typescript
import { mount } from '@vue/test-utils';
import { describe, it, expect, vi } from 'vitest';
import MyComponent from './MyComponent.vue';

describe('MyComponent', () => {
  it('emits update event', async () => {
    const wrapper = mount(MyComponent, {
      props: {
        user: { id: 1, name: 'Test' }
      }
    });
    
    // Type-safe component instance
    const vm = wrapper.vm as InstanceType<typeof MyComponent>;
    
    await wrapper.find('button').trigger('click');
    
    // Check emitted events
    expect(wrapper.emitted('update')).toBeTruthy();
    expect(wrapper.emitted('update')![0]).toEqual([
      1,
      { name: 'Updated' }
    ]);
  });
  
  it('uses composable correctly', () => {
    const useUserMock = vi.fn(() => ({
      user: ref({ id: 1, name: 'Test' }),
      loading: ref(false),
      fetchUser: vi.fn()
    }));
    
    vi.mock('./composables/useUser', () => ({
      useUser: useUserMock
    }));
    
    const wrapper = mount(MyComponent);
    expect(useUserMock).toHaveBeenCalled();
  });
});
```

## Pinia Store with TypeScript

```typescript
// stores/user.ts
import { defineStore } from 'pinia';
import type { User } from '@/types';

interface UserState {
  users: User[];
  currentUser: User | null;
  loading: boolean;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    users: [],
    currentUser: null,
    loading: false
  }),
  
  getters: {
    activeUsers: (state) => 
      state.users.filter(user => user.active),
    
    getUserById: (state) => 
      (id: number) => state.users.find(u => u.id === id)
  },
  
  actions: {
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await fetch('/api/users');
        this.users = await response.json();
      } finally {
        this.loading = false;
      }
    },
    
    setCurrentUser(user: User) {
      this.currentUser = user;
    }
  }
});

// Setup store alternative
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
    fetchUsers
  };
});
```
