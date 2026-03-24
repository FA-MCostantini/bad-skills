# Structured Logging with log/slog

`log/slog` is the structured logging package added to the Go standard library in Go 1.21. Prefer it over third-party loggers for most applications.

## Creating a Logger

```go
import "log/slog"

// JSON handler — machine-readable output for production
jsonLogger := slog.New(slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

// Text handler — human-readable output for development
textLogger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelDebug,
}))

// Set as the default logger (use sparingly; prefer explicit injection)
slog.SetDefault(jsonLogger)
```

## Log Levels

```go
slog.Debug("cache miss", "key", "user:42")
slog.Info("request received", "method", "GET", "path", "/users")
slog.Warn("rate limit approaching", "current", 950, "limit", 1000)
slog.Error("database query failed", "err", err, "query", "SELECT ...")
```

## Structured Fields

Attach typed key-value pairs instead of formatted strings.

```go
// Convenience attributes
slog.Info("user created",
    slog.String("email", user.Email),
    slog.Int("id", user.ID),
    slog.Duration("elapsed", time.Since(start)),
    slog.Any("roles", user.Roles),
    slog.Time("created_at", user.CreatedAt),
)

// Inline key-value pairs (any alternating key, value)
slog.Info("payment processed",
    "amount", 9999,
    "currency", "USD",
    "user_id", userID,
)
```

## slog.With — Adding Context Fields

Use `With` to derive a logger with pre-attached fields. This is ideal for per-request loggers.

```go
// Request-scoped logger with correlation ID
func handleRequest(log *slog.Logger, r *http.Request) {
    reqLog := log.With(
        slog.String("request_id", r.Header.Get("X-Request-ID")),
        slog.String("method", r.Method),
        slog.String("path", r.URL.Path),
    )

    reqLog.Info("processing request")

    user, err := fetchUser(r.Context())
    if err != nil {
        reqLog.Error("fetch user failed", "err", err)
        return
    }

    // Derive further with user context
    userLog := reqLog.With(slog.Int64("user_id", user.ID))
    userLog.Info("user authenticated")
}
```

## slog.LogValuer — Lazy and Custom Formatting

Implement `slog.LogValuer` to defer expensive formatting or to redact sensitive fields.

```go
// Redact sensitive values at log time
type SecretString string

func (s SecretString) LogValue() slog.Value {
    return slog.StringValue("[REDACTED]")
}

// Usage
password := SecretString("hunter2")
slog.Info("login attempt", "password", password)
// output: password=[REDACTED]

// Lazy struct formatting — avoids allocation when log level is disabled
type UserValue struct{ u *User }

func (v UserValue) LogValue() slog.Value {
    return slog.GroupValue(
        slog.Int64("id", v.u.ID),
        slog.String("email", v.u.Email),
    )
}

slog.Info("profile loaded", "user", UserValue{u: user})
// output: user.id=42 user.email=alice@example.com
```

## Injecting *slog.Logger as a Dependency

Do not rely on the global `slog.Default()` inside business logic. Pass the logger explicitly so behavior is testable and replaceable.

```go
// Handler carrying its own logger
type UserHandler struct {
    svc UserService
    log *slog.Logger
}

func NewUserHandler(svc UserService, log *slog.Logger) *UserHandler {
    return &UserHandler{svc: svc, log: log}
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    h.log.Info("creating user")
    // ...
}

// Wire at startup
logger := slog.New(slog.NewJSONHandler(os.Stderr, nil))
handler := NewUserHandler(svc, logger.With("component", "user-handler"))
```

## Custom Handler Implementation

Wrap an existing handler to add behaviour (e.g., always include hostname).

```go
type HostnameHandler struct {
    inner   slog.Handler
    hostname string
}

func NewHostnameHandler(inner slog.Handler) *HostnameHandler {
    h, _ := os.Hostname()
    return &HostnameHandler{inner: inner, hostname: h}
}

func (h *HostnameHandler) Enabled(ctx context.Context, level slog.Level) bool {
    return h.inner.Enabled(ctx, level)
}

func (h *HostnameHandler) Handle(ctx context.Context, r slog.Record) error {
    r.AddAttrs(slog.String("hostname", h.hostname))
    return h.inner.Handle(ctx, r)
}

func (h *HostnameHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
    return &HostnameHandler{inner: h.inner.WithAttrs(attrs), hostname: h.hostname}
}

func (h *HostnameHandler) WithGroup(name string) slog.Handler {
    return &HostnameHandler{inner: h.inner.WithGroup(name), hostname: h.hostname}
}
```

## Request Logging Middleware with Correlation ID

```go
const requestIDKey = "request_id"

// RequestIDMiddleware injects a correlation ID into the request context and logger.
func RequestIDMiddleware(log *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            reqID := r.Header.Get("X-Request-ID")
            if reqID == "" {
                reqID = newRequestID()
            }
            w.Header().Set("X-Request-ID", reqID)

            // Attach request-scoped logger to context
            reqLog := log.With(slog.String(requestIDKey, reqID))
            ctx := context.WithValue(r.Context(), loggerKey{}, reqLog)

            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

type loggerKey struct{}

// LoggerFromContext retrieves the request-scoped logger, falling back to the default.
func LoggerFromContext(ctx context.Context) *slog.Logger {
    if log, ok := ctx.Value(loggerKey{}).(*slog.Logger); ok {
        return log
    }
    return slog.Default()
}

func newRequestID() string {
    b := make([]byte, 8)
    _, _ = rand.Read(b)
    return fmt.Sprintf("%x", b)
}
```

## Quick Reference

| API | Purpose |
|-----|---------|
| `slog.New(handler)` | Create logger with handler |
| `slog.NewJSONHandler(w, opts)` | JSON output (production) |
| `slog.NewTextHandler(w, opts)` | Text output (development) |
| `log.With(attrs...)` | Derive logger with extra fields |
| `slog.String/Int/Bool/Any` | Typed attribute constructors |
| `slog.Group("name", attrs...)` | Nest attributes under a key |
| `slog.LogValuer` | Lazy / redacted field values |
| `slog.SetDefault(log)` | Set package-level default |
