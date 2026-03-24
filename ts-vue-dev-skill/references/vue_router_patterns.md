# Vue Router 4 Patterns

## Setup
```typescript
import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Home' },
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('@/views/UsersView.vue'),
    meta: { requiresAuth: true, title: 'Users' },
    children: [
      {
        path: ':id',
        name: 'user-detail',
        component: () => import('@/views/UserDetailView.vue'),
        props: true,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
```

## Route Meta Typing
```typescript
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    title?: string;
    roles?: string[];
    layout?: 'default' | 'admin' | 'blank';
  }
}
```

## Navigation Guards
```typescript
// Global guard
router.beforeEach((to, from) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }

  if (to.meta.roles && !to.meta.roles.some(r => userStore.hasRole(r))) {
    return { name: 'forbidden' };
  }
});

// After each - update document title
router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} | App` : 'App';
});

// Per-route guard
{
  path: '/admin',
  beforeEnter: (to) => {
    const userStore = useUserStore();
    if (!userStore.isAdmin) return { name: 'forbidden' };
  },
}
```

## Composables
```typescript
import { useRouter, useRoute } from 'vue-router';

// In setup
const router = useRouter();
const route = useRoute();

// Programmatic navigation
router.push({ name: 'user-detail', params: { id: '123' } });
router.replace({ name: 'home' });
router.back();

// Reactive route params
const userId = computed(() => route.params.id as string);
```

## Typed useRoute with Generic
```typescript
// For strongly typed route params
function useTypedRoute<T extends Record<string, string>>() {
  const route = useRoute();
  return {
    ...route,
    params: route.params as T,
  };
}

// Usage
const route = useTypedRoute<{ id: string }>();
route.params.id; // string, not string | string[]
```
