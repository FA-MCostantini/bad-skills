# Concurrency Patterns

## Goroutine Lifecycle Management

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

// Worker pool with bounded concurrency
type WorkerPool struct {
    workers int
    tasks   chan func()
    wg      sync.WaitGroup
}

func NewWorkerPool(workers int) *WorkerPool {
    wp := &WorkerPool{
        workers: workers,
        tasks:   make(chan func(), workers*2), // Buffered channel
    }
    wp.start()
    return wp
}

func (wp *WorkerPool) start() {
    for i := 0; i < wp.workers; i++ {
        wp.wg.Add(1)
        go func() {
            defer wp.wg.Done()
            for task := range wp.tasks {
                task()
            }
        }()
    }
}

func (wp *WorkerPool) Submit(task func()) {
    wp.tasks <- task
}

func (wp *WorkerPool) Shutdown() {
    close(wp.tasks)
    wp.wg.Wait()
}
```

## Channel Patterns

```go
// Generator pattern
func generateNumbers(ctx context.Context, max int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for i := 0; i < max; i++ {
            select {
            case out <- i:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}

// Fan-out, fan-in pattern
func fanOut(ctx context.Context, input <-chan int, workers int) []<-chan int {
    channels := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        channels[i] = process(ctx, input)
    }
    return channels
}

func process(ctx context.Context, input <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for val := range input {
            select {
            case out <- val * 2:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}

func fanIn(ctx context.Context, channels ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range channels {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for val := range c {
                select {
                case out <- val:
                case <-ctx.Done():
                    return
                }
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}
```

## Select Statement Patterns

```go
// Timeout pattern
func fetchWithTimeout(ctx context.Context, url string) (string, error) {
    result := make(chan string, 1)
    errCh := make(chan error, 1)

    go func() {
        // Simulate network call
        time.Sleep(100 * time.Millisecond)
        result <- "data from " + url
    }()

    select {
    case res := <-result:
        return res, nil
    case err := <-errCh:
        return "", err
    case <-time.After(50 * time.Millisecond):
        return "", fmt.Errorf("timeout")
    case <-ctx.Done():
        return "", ctx.Err()
    }
}

// Done channel pattern for graceful shutdown
type Server struct {
    done chan struct{}
}

func (s *Server) Shutdown() {
    close(s.done)
}

func (s *Server) Run(ctx context.Context) {
    ticker := time.NewTicker(1 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            fmt.Println("tick")
        case <-s.done:
            fmt.Println("shutting down")
            return
        case <-ctx.Done():
            fmt.Println("context cancelled")
            return
        }
    }
}
```

## Sync Primitives

```go
import "sync"

// Mutex for protecting shared state
type Counter struct {
    mu    sync.Mutex
    count int
}

func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}

// RWMutex for read-heavy workloads
type Cache struct {
    mu    sync.RWMutex
    items map[string]string
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    val, ok := c.items[key]
    return val, ok
}

func (c *Cache) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = value
}

// sync.Once for initialization
type Service struct {
    once   sync.Once
    config *Config
}

func (s *Service) getConfig() *Config {
    s.once.Do(func() {
        s.config = loadConfig() // Only called once
    })
    return s.config
}
```

## Rate Limiting and Backpressure

```go
import "golang.org/x/time/rate"

// Token bucket rate limiter
type RateLimiter struct {
    limiter *rate.Limiter
}

func NewRateLimiter(rps int) *RateLimiter {
    return &RateLimiter{
        limiter: rate.NewLimiter(rate.Limit(rps), rps),
    }
}

func (rl *RateLimiter) Process(ctx context.Context, item string) error {
    if err := rl.limiter.Wait(ctx); err != nil {
        return err
    }
    // Process item
    return nil
}

// Semaphore pattern for limiting concurrency
type Semaphore struct {
    slots chan struct{}
}

func NewSemaphore(n int) *Semaphore {
    return &Semaphore{
        slots: make(chan struct{}, n),
    }
}

func (s *Semaphore) Acquire() {
    s.slots <- struct{}{}
}

func (s *Semaphore) Release() {
    <-s.slots
}

func (s *Semaphore) Do(fn func()) {
    s.Acquire()
    defer s.Release()
    fn()
}
```

## Pipeline Pattern

```go
// Stage-based processing pipeline
func pipeline(ctx context.Context, input <-chan int) <-chan int {
    // Stage 1: Square numbers
    stage1 := make(chan int)
    go func() {
        defer close(stage1)
        for num := range input {
            select {
            case stage1 <- num * num:
            case <-ctx.Done():
                return
            }
        }
    }()

    // Stage 2: Filter even numbers
    stage2 := make(chan int)
    go func() {
        defer close(stage2)
        for num := range stage1 {
            if num%2 == 0 {
                select {
                case stage2 <- num:
                case <-ctx.Done():
                    return
                }
            }
        }
    }()

    return stage2
}
```

## errgroup (golang.org/x/sync/errgroup)

`errgroup` coordinates a group of goroutines and collects the first non-nil error.

```go
import "golang.org/x/sync/errgroup"

// Basic usage: g.Go() launches goroutines, g.Wait() blocks until all finish.
func fetchAll(urls []string) error {
    var g errgroup.Group
    for _, url := range urls {
        url := url // captured for Go < 1.22; safe to omit in Go 1.22+
        g.Go(func() error {
            return fetch(url)
        })
    }
    return g.Wait() // returns the first non-nil error
}

// errgroup.WithContext — cancel sibling goroutines on first error
func processWithContext(ctx context.Context, items []string) error {
    g, ctx := errgroup.WithContext(ctx)
    results := make([]string, len(items))

    for i, item := range items {
        i, item := i, item
        g.Go(func() error {
            result, err := processItem(ctx, item)
            if err != nil {
                return err // ctx is cancelled for all siblings
            }
            results[i] = result
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return err
    }
    // use results
    return nil
}

// g.SetLimit(n) — cap the number of goroutines running concurrently
func processLimited(ctx context.Context, items []string) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(10) // at most 10 goroutines at a time

    for _, item := range items {
        item := item
        g.Go(func() error {
            return processItem(ctx, item)
        })
    }
    return g.Wait()
}
```

## atomic Types (sync/atomic)

Go 1.19+ exposes typed atomic wrappers that avoid unsafe pointer casts.

```go
import "sync/atomic"

// atomic.Int64 — lock-free integer counter
var hits atomic.Int64

hits.Add(1)
hits.Store(0)
current := hits.Load()
fmt.Println(current)

// atomic.Bool — flag without a mutex
var ready atomic.Bool

ready.Store(true)
if ready.Load() {
    // ...
}

// atomic.Pointer[T] — lock-free pointer swap
type Config struct{ MaxConns int }

var current atomic.Pointer[Config]
current.Store(&Config{MaxConns: 10})

// Hot-reload config without locking readers
cfg := current.Load()
fmt.Println(cfg.MaxConns)

// Swap atomically
old := current.Swap(&Config{MaxConns: 20})
_ = old
```

## Graceful HTTP Server Shutdown

```go
import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func runServer(handler http.Handler) error {
    srv := &http.Server{
        Addr:         ":8080",
        Handler:      handler,
        ReadTimeout:  5 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
    }

    // Start server in background goroutine.
    serverErr := make(chan error, 1)
    go func() {
        slog.Info("server listening", "addr", srv.Addr)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            serverErr <- err
        }
    }()

    // Wait for OS signal or server error.
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

    select {
    case err := <-serverErr:
        return err
    case sig := <-quit:
        slog.Info("shutdown signal received", "signal", sig)
    }

    // Graceful shutdown: drain in-flight requests within the deadline.
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        return fmt.Errorf("server shutdown: %w", err)
    }
    slog.Info("server stopped gracefully")
    return nil
}
```

## Quick Reference

| Pattern | Use Case | Key Points |
|---------|----------|------------|
| Worker Pool | Bounded concurrency | Limit goroutines, reuse workers |
| Fan-out/Fan-in | Parallel processing | Distribute work, merge results |
| Pipeline | Stream processing | Chain transformations |
| Rate Limiter | API throttling | Control request rate |
| Semaphore | Resource limits | Cap concurrent operations |
| Done Channel | Graceful shutdown | Signal completion |
| errgroup | Parallel tasks with error propagation | g.Go, g.Wait, g.SetLimit |
| atomic types | Lock-free counters/flags | atomic.Int64, atomic.Bool, atomic.Pointer |
| http.Server.Shutdown | Graceful HTTP drain | Signal handler + context deadline |
