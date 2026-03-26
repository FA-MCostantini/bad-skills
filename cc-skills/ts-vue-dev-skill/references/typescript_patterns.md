# TypeScript Patterns & Best Practices

## Strict Configuration (tsconfig.json)
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022", "DOM"],
    "moduleResolution": "bundler",
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
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### Why These Extra Options Matter

- **`moduleResolution: "bundler"`** — Matches how Vite/esbuild resolve modules; avoids spurious errors with `.ts` extension imports and package `exports` fields.
- **`exactOptionalPropertyTypes`** — Prevents assigning `undefined` to an optional property that doesn't include `undefined` in its type. Makes `{ foo?: string }` mean the key either has a `string` value or is absent, not `string | undefined`.
- **`noUncheckedIndexedAccess`** — Index signatures (arrays, `Record<string, T>`) return `T | undefined` instead of `T`, forcing you to handle the "not found" case explicitly.

## Type Guards & Narrowing

### User-Defined Type Guards
```typescript
interface User {
  id: number;
  email: string;
  role: 'admin' | 'user';
}

function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value &&
    'role' in value &&
    typeof (value as User).id === 'number' &&
    typeof (value as User).email === 'string' &&
    ['admin', 'user'].includes((value as User).role)
  );
}

// Usage with narrowing
function processData(data: unknown): void {
  if (isUser(data)) {
    // TypeScript knows data is User here
    console.log(data.email.toUpperCase());
  }
}
```

### Discriminated Unions
```typescript
type Result<T> = 
  | { success: true; data: T }
  | { success: false; error: Error };

function handleResult<T>(result: Result<T>): T {
  if (result.success) {
    // Narrowed to success case
    return result.data;
  } else {
    // Narrowed to error case
    throw result.error;
  }
}
```

## Utility Types

### Custom Utility Types
```typescript
// Deep readonly
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object 
    ? DeepReadonly<T[K]> 
    : T[K];
};

// Deep partial
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object 
    ? DeepPartial<T[K]> 
    : T[K];
};

// Strict omit (better than built-in)
type StrictOmit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

// Mutable (remove readonly)
type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};

// Value of object
type ValueOf<T> = T[keyof T];

// Nullable
type Nullable<T> = T | null | undefined;
```

### Branded Types (Nominal Typing)
```typescript
type Brand<K, T> = K & { __brand: T };

type UserId = Brand<number, 'UserId'>;
type PostId = Brand<number, 'PostId'>;

function getUserById(id: UserId): User {
  // ...
}

// Type-safe IDs
const userId = 123 as UserId;
const postId = 456 as PostId;

getUserById(userId); // ✅ OK
// getUserById(postId); // ❌ Error: Type 'PostId' not assignable to 'UserId'
```

## Generics & Constraints

### Advanced Generic Patterns
```typescript
// Generic with constraints
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Generic class with interface constraint
interface Identifiable {
  id: number;
}

class Repository<T extends Identifiable> {
  private items = new Map<number, T>();
  
  add(item: T): void {
    this.items.set(item.id, item);
  }
  
  find(id: number): T | undefined {
    return this.items.get(id);
  }
  
  findAll(): T[] {
    return Array.from(this.items.values());
  }
}

// Conditional types
type IsArray<T> = T extends Array<infer U> ? U : never;
type Unpacked<T> = T extends Promise<infer U> ? U : T;
```

## Exhaustive Checking

### Never Type for Exhaustiveness
```typescript
type Status = 'pending' | 'active' | 'suspended' | 'deleted';

function handleStatus(status: Status): string {
  switch (status) {
    case 'pending':
      return 'Waiting for activation';
    case 'active':
      return 'Currently active';
    case 'suspended':
      return 'Temporarily suspended';
    case 'deleted':
      return 'Permanently deleted';
    default:
      // This ensures we handle all cases
      const _exhaustive: never = status;
      throw new Error(`Unhandled status: ${status}`);
  }
}
```

## Async Patterns

### Typed Promises and Error Handling
```typescript
// Result type for async operations
type AsyncResult<T, E = Error> = Promise<
  { ok: true; value: T } | { ok: false; error: E }
>;

async function safeAsync<T>(
  fn: () => Promise<T>
): AsyncResult<T> {
  try {
    const value = await fn();
    return { ok: true, value };
  } catch (error) {
    return { ok: false, error: error as Error };
  }
}

// Usage
const result = await safeAsync(async () => {
  const response = await fetch('/api/data');
  return response.json();
});

if (result.ok) {
  console.log(result.value);
} else {
  console.error(result.error);
}
```

### Async Queue with Typing
```typescript
class AsyncQueue<T> {
  private queue: (() => Promise<T>)[] = [];
  private processing = false;
  
  async add(task: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await task();
          resolve(result);
          return result;
        } catch (error) {
          reject(error);
          throw error;
        }
      });
      
      if (!this.processing) {
        this.process();
      }
    });
  }
  
  private async process(): Promise<void> {
    this.processing = true;
    
    while (this.queue.length > 0) {
      const task = this.queue.shift();
      if (task) {
        await task();
      }
    }
    
    this.processing = false;
  }
}
```

## Decorators

> **Note on decorator APIs:** TypeScript 5.x supports two decorator APIs.
> - **Legacy (experimentalDecorators)** — the original `target/propertyKey/descriptor` API used by many frameworks. Still works but is not standard.
> - **TC39 Stage 3 (context-based)** — the standardised API (enabled by default in TS 5.0 without `experimentalDecorators`). Uses a `context` object instead of a descriptor.
>
> Prefer the Stage 3 API for new code. Legacy examples are shown below for compatibility with older frameworks (e.g., NestJS, TypeORM).

### Method Decorators — TC39 Stage 3 (preferred)
```typescript
function throttle(delay: number) {
  return function <T extends (...args: unknown[]) => unknown>(
    fn: T,
    _context: ClassMethodDecoratorContext
  ): T {
    let timeout: ReturnType<typeof setTimeout> | null = null;
    return function (this: unknown, ...args: Parameters<T>): ReturnType<T> {
      if (timeout) return undefined as ReturnType<T>;
      timeout = setTimeout(() => { timeout = null; }, delay);
      return fn.apply(this, args) as ReturnType<T>;
    } as T;
  };
}

class SearchComponent {
  @throttle(300)
  async search(query: string): Promise<void> {
    // Search implementation
  }
}
```

### Method Decorators — Legacy (experimentalDecorators)
```typescript
function throttleLegacy(delay: number) {
  return function (
    target: object,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ): PropertyDescriptor {
    let timeout: ReturnType<typeof setTimeout> | null = null;
    const original = descriptor.value;

    descriptor.value = function (...args: unknown[]) {
      if (timeout) return;
      timeout = setTimeout(() => { timeout = null; }, delay);
      return original.apply(this, args);
    };

    return descriptor;
  };
}
```

### Property Decorators — TC39 Stage 3 (preferred)
```typescript
function validate(validator: (value: unknown) => boolean) {
  return function <T>(
    _target: undefined,
    context: ClassFieldDecoratorContext
  ) {
    context.addInitializer(function (this: Record<string, unknown>) {
      const key = context.name as string;
      let _value: unknown = this[key];
      Object.defineProperty(this, key, {
        get() { return _value; },
        set(newVal: unknown) {
          if (!validator(newVal)) {
            throw new Error(`Invalid value for ${key}`);
          }
          _value = newVal;
        },
        enumerable: true,
        configurable: true,
      });
    });
  };
}

class User {
  @validate((v) => typeof v === 'string' && v.includes('@'))
  email!: string;
}
```

## Module Patterns

### Barrel Exports
```typescript
// types/index.ts
export * from './user';
export * from './post';
export * from './comment';

// Or selective exports
export type { User, UserRole } from './user';
export type { Post, PostStatus } from './post';
```

### Namespace Pattern
```typescript
namespace API {
  export interface Config {
    baseUrl: string;
    timeout: number;
  }
  
  export class Client {
    constructor(private config: Config) {}
    
    async get<T>(endpoint: string): Promise<T> {
      // Implementation
      return {} as T;
    }
  }
  
  export function createClient(config: Config): Client {
    return new Client(config);
  }
}

// Usage
const client = API.createClient({
  baseUrl: 'https://api.example.com',
  timeout: 5000,
});
```

## Type-Safe Event Emitter

```typescript
type EventMap = {
  'user:login': { userId: number; timestamp: Date };
  'user:logout': { userId: number };
  'data:update': { id: string; changes: Record<string, any> };
};

class TypedEventEmitter<T extends Record<string, any>> {
  private listeners: Partial<{
    [K in keyof T]: Array<(data: T[K]) => void>;
  }> = {};
  
  on<K extends keyof T>(event: K, listener: (data: T[K]) => void): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event]!.push(listener);
  }
  
  emit<K extends keyof T>(event: K, data: T[K]): void {
    this.listeners[event]?.forEach(listener => listener(data));
  }
  
  off<K extends keyof T>(event: K, listener: (data: T[K]) => void): void {
    const listeners = this.listeners[event];
    if (listeners) {
      const index = listeners.indexOf(listener);
      if (index !== -1) {
        listeners.splice(index, 1);
      }
    }
  }
}

// Usage
const emitter = new TypedEventEmitter<EventMap>();

emitter.on('user:login', ({ userId, timestamp }) => {
  // TypeScript knows the exact shape of the data
  console.log(`User ${userId} logged in at ${timestamp}`);
});
```

## Performance Patterns

### Lazy Loading with Type Safety
```typescript
class LazyValue<T> {
  private value?: T;
  private loaded = false;
  
  constructor(private loader: () => T | Promise<T>) {}
  
  async get(): Promise<T> {
    if (!this.loaded) {
      this.value = await this.loader();
      this.loaded = true;
    }
    return this.value!;
  }
  
  reset(): void {
    this.value = undefined;
    this.loaded = false;
  }
}

// Usage
const config = new LazyValue(async () => {
  const response = await fetch('/api/config');
  return response.json();
});
```

## Testing Patterns

### Type-Safe Mocks
```typescript
import { vi, type Mock } from 'vitest';

type DeepPartialMock<T> = {
  [P in keyof T]?: T[P] extends (...args: any[]) => any
    ? Mock<Parameters<T[P]>, ReturnType<T[P]>>
    : T[P] extends object
    ? DeepPartialMock<T[P]>
    : T[P];
};

function createMock<T>(partial: DeepPartialMock<T> = {}): T {
  return partial as T;
}

// Usage in tests (Vitest — not jest.fn / jest.Mock)
const mockUser = createMock<User>({
  id: 1,
  email: 'test@example.com',
  save: vi.fn().mockResolvedValue(true),
});
```

## Satisfies Operator

Use `satisfies` to validate a value against a type without widening the inferred type. This preserves narrow literal types while still catching shape errors.

```typescript
type ColorConfig = Record<string, { hex: string }>;

// Type-safe without widening
const colors = {
  primary: { hex: '#007bff' },
  danger: { hex: '#dc3545' },
} satisfies ColorConfig;

// colors.primary is still narrowly typed — wouldn't be the case with `as ColorConfig`
colors.primary.hex; // OK — string, not widened to unknown
// colors.missing;  // Error: property does not exist
```

## Const Type Parameters (TypeScript 5.0+)

`const` on a type parameter infers the narrowest possible literal type, equivalent to `as const` on the call site.

```typescript
function literal<const T>(value: T): T { return value; }

const result = literal({ status: 'active', count: 42 });
// type is { readonly status: "active"; readonly count: 42 }
// Without `const`: { status: string; count: number }
```

## Using Declarations (Symbol.dispose — TypeScript 5.2+)

The `using` keyword calls `[Symbol.dispose]()` at the end of the enclosing block, replacing fragile try/finally teardown.

```typescript
function connectToDb(): Disposable {
  const conn = createConnection();
  return {
    [Symbol.dispose]() { conn.close(); }
  };
}

{
  using db = connectToDb();
  // db.close() called automatically when the block exits (including on throw)
}

// Async variant
async function openFile(path: string): Promise<AsyncDisposable> {
  const handle = await fs.open(path);
  return {
    async [Symbol.asyncDispose]() { await handle.close(); }
  };
}

{
  await using file = await openFile('data.csv');
}
```

## Template Literal Types

Combine string literal types to describe patterns at the type level.

```typescript
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<'click'>; // 'onClick'

type CssVar<T extends string> = `--${T}`;
type ThemeVars = CssVar<'primary' | 'secondary'>; // '--primary' | '--secondary'

// Inferring from template literals
type ExtractRoute<T extends string> =
  T extends `/api/${infer Route}` ? Route : never;
type UserRoute = ExtractRoute<'/api/users'>; // 'users'
```

## Mapped Types with `as` Clause

The `as` clause in a mapped type lets you rename or filter keys.

```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface User { name: string; age: number; }
type UserGetters = Getters<User>;
// { getName: () => string; getAge: () => number; }

// Filter out keys with `never`
type NonNullableProps<T> = {
  [K in keyof T as T[K] extends null | undefined ? never : K]: T[K];
};
```
