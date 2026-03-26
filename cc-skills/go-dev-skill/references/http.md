# HTTP Servers and Clients

## net/http ServeMux Enhanced Routing (Go 1.22+)

Go 1.22 added method-based routing, path parameters, and wildcards directly into `net/http.ServeMux`.

```go
mux := http.NewServeMux()

// Method-based routing
mux.HandleFunc("GET /users", listUsers)
mux.HandleFunc("POST /users", createUser)

// Path parameters — retrieved with r.PathValue
mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("PUT /users/{id}", updateUser)
mux.HandleFunc("DELETE /users/{id}", deleteUser)

// Wildcard: matches /files/any/nested/path
mux.HandleFunc("GET /files/{path...}", serveFile)

func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id") // "42" from /users/42
    // ...
}

func serveFile(w http.ResponseWriter, r *http.Request) {
    path := r.PathValue("path") // "static/css/main.css"
    // ...
}
```

**Security note:** Always use `http.NewServeMux()` rather than the default `http.DefaultServeMux`. Third-party packages can register handlers on `DefaultServeMux`, creating an unintended attack surface.

## Middleware Pattern

Middleware is a function that wraps an `http.Handler` and returns a new `http.Handler`.

```go
// Middleware signature
type Middleware func(next http.Handler) http.Handler

// Logging middleware
func LoggingMiddleware(log *slog.Logger) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            rw := &responseWriter{ResponseWriter: w, status: http.StatusOK}
            next.ServeHTTP(rw, r)
            log.Info("request",
                "method", r.Method,
                "path", r.URL.Path,
                "status", rw.status,
                "duration", time.Since(start),
            )
        })
    }
}

// responseWriter captures status code
type responseWriter struct {
    http.ResponseWriter
    status int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.status = code
    rw.ResponseWriter.WriteHeader(code)
}

// Chain middlewares
func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}

// Usage
mux := http.NewServeMux()
mux.HandleFunc("GET /users", listUsers)

handler := Chain(mux,
    LoggingMiddleware(logger),
    AuthMiddleware(authSvc),
)
```

## Request Parsing Helpers

```go
// Parse JSON request body
func decodeJSON[T any](r *http.Request, v *T) error {
    defer r.Body.Close()
    dec := json.NewDecoder(r.Body)
    dec.DisallowUnknownFields()
    return dec.Decode(v)
}

// Path parameter
id := r.PathValue("id")

// Query parameter
page := r.URL.Query().Get("page")
if page == "" {
    page = "1"
}

// Required header
authHeader := r.Header.Get("Authorization")
```

## Response Helpers

```go
// Write JSON response
func writeJSON(w http.ResponseWriter, status int, v any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    if err := json.NewEncoder(w).Encode(v); err != nil {
        // encoding to ResponseWriter rarely fails; log if needed
        slog.Error("writeJSON encode", "err", err)
    }
}

// Write error response as JSON
type errorResponse struct {
    Error string `json:"error"`
}

func writeError(w http.ResponseWriter, status int, msg string) {
    writeJSON(w, status, errorResponse{Error: msg})
}

// Usage in handlers
func createUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := decodeJSON(r, &req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid request body")
        return
    }
    user, err := svc.Create(r.Context(), req)
    if err != nil {
        switch {
        case errors.Is(err, ErrConflict):
            writeError(w, http.StatusConflict, "user already exists")
        default:
            writeError(w, http.StatusInternalServerError, "internal server error")
        }
        return
    }
    writeJSON(w, http.StatusCreated, user)
}
```

## Testing HTTP Handlers

```go
import (
    "net/http"
    "net/http/httptest"
    "testing"
)

// httptest.NewRecorder — unit test a single handler
func TestGetUser(t *testing.T) {
    svc := &mockUserService{user: &User{ID: 1, Name: "Alice"}}
    h := NewHandler(svc, slog.Default())

    req := httptest.NewRequest("GET", "/users/1", nil)
    w := httptest.NewRecorder()

    h.ServeHTTP(w, req)

    if w.Code != http.StatusOK {
        t.Errorf("expected 200, got %d", w.Code)
    }

    var got User
    if err := json.NewDecoder(w.Body).Decode(&got); err != nil {
        t.Fatalf("decode response: %v", err)
    }
    if got.Name != "Alice" {
        t.Errorf("want Name=Alice, got %q", got.Name)
    }
}

// httptest.NewServer — integration / client test against a real TCP server
func TestClient(t *testing.T) {
    ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
    }))
    defer ts.Close()

    resp, err := http.Get(ts.URL + "/health")
    if err != nil {
        t.Fatal(err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        t.Errorf("expected 200, got %d", resp.StatusCode)
    }
}
```

## http.Server Configuration

Always configure timeouts to prevent resource exhaustion from slow or malicious clients.

```go
srv := &http.Server{
    Addr:    ":8080",
    Handler: mux,

    // Maximum duration to read the entire request, including body.
    ReadTimeout: 5 * time.Second,

    // Maximum duration before timing out writes of the response.
    WriteTimeout: 10 * time.Second,

    // Maximum amount of time to wait for the next request (keep-alive).
    IdleTimeout: 120 * time.Second,

    // Maximum duration to read request headers.
    ReadHeaderTimeout: 2 * time.Second,
}

if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
    log.Fatal(err)
}
```

## Quick Reference

| Feature | API |
|---------|-----|
| Method routing | `mux.HandleFunc("GET /path", handler)` |
| Path parameter | `r.PathValue("name")` |
| Wildcard suffix | `"GET /files/{path...}"` |
| New mux (safe) | `http.NewServeMux()` |
| Recorder (unit test) | `httptest.NewRecorder()` |
| Real server (integration) | `httptest.NewServer(handler)` |
| Graceful shutdown | `srv.Shutdown(ctx)` |
