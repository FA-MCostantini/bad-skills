# Security

## SQL Injection Prevention with pgx/v5

Always use parameterized queries. Never concatenate user input into SQL strings.

```go
import "github.com/jackc/pgx/v5/pgxpool"

// GOOD: parameterized — $1, $2 are placeholders
func (r *userRepo) FindByEmail(ctx context.Context, email string) (*User, error) {
    row := r.pool.QueryRow(ctx,
        `SELECT id, name, email FROM users WHERE email = $1`,
        email,
    )
    var u User
    if err := row.Scan(&u.ID, &u.Name, &u.Email); err != nil {
        return nil, err
    }
    return &u, nil
}

// BAD: string interpolation — NEVER do this
query := fmt.Sprintf("SELECT * FROM users WHERE email = '%s'", email)

// Named args with pgx.NamedArgs for readability
import "github.com/jackc/pgx/v5"

func (r *userRepo) Create(ctx context.Context, u *User) error {
    _, err := r.pool.Exec(ctx,
        `INSERT INTO users (name, email) VALUES (@name, @email)`,
        pgx.NamedArgs{"name": u.Name, "email": u.Email},
    )
    return err
}
```

## XSS: html/template vs text/template

Use `html/template` for all HTML output — it auto-escapes values in the appropriate context (HTML, JS, URL, CSS).

```go
import "html/template"

// GOOD: html/template escapes user input automatically
tmpl := template.Must(template.New("page").Parse(`
    <h1>Hello, {{.Name}}</h1>
    <p>{{.Bio}}</p>
`))
tmpl.Execute(w, userData)

// BAD: text/template does NOT escape — never use for HTML
import "text/template" // do not use for HTML responses
```

Only use `template.HTML`, `template.JS`, `template.URL` when you have explicitly sanitized and trust the content.

## CSRF: Token Generation and Double-Submit Cookie

```go
import (
    "crypto/rand"
    "encoding/hex"
    "net/http"
)

// Generate a cryptographically random CSRF token
func generateCSRFToken() (string, error) {
    b := make([]byte, 32)
    if _, err := rand.Read(b); err != nil {
        return "", fmt.Errorf("generate csrf token: %w", err)
    }
    return hex.EncodeToString(b), nil
}

// Double-submit cookie pattern:
// 1. Set a CSRF token as a cookie on form load.
// 2. Require the same token in a request header or hidden form field.
// 3. Compare the two on the server.

func setCSRFCookie(w http.ResponseWriter) (string, error) {
    token, err := generateCSRFToken()
    if err != nil {
        return "", err
    }
    http.SetCookie(w, &http.Cookie{
        Name:     "csrf_token",
        Value:    token,
        HttpOnly: false, // must be readable by JS to set the header
        Secure:   true,
        SameSite: http.SameSiteStrictMode,
        Path:     "/",
    })
    return token, nil
}

func validateCSRF(r *http.Request) bool {
    cookie, err := r.Cookie("csrf_token")
    if err != nil {
        return false
    }
    header := r.Header.Get("X-CSRF-Token")
    return cookie.Value != "" && cookie.Value == header
}
```

## Input Validation

### Manual validation

```go
type CreateUserRequest struct {
    Name  string `json:"name"`
    Email string `json:"email"`
    Age   int    `json:"age"`
}

func (r CreateUserRequest) Validate() error {
    var errs []error
    if strings.TrimSpace(r.Name) == "" {
        errs = append(errs, &ValidationError{Field: "name", Message: "required"})
    }
    if !strings.Contains(r.Email, "@") {
        errs = append(errs, &ValidationError{Field: "email", Message: "invalid format"})
    }
    if r.Age < 0 || r.Age > 150 {
        errs = append(errs, &ValidationError{Field: "age", Message: "must be 0–150"})
    }
    return errors.Join(errs...)
}
```

### go-playground/validator

```go
import "github.com/go-playground/validator/v10"

type CreateUserRequest struct {
    Name  string `json:"name"  validate:"required,min=1,max=100"`
    Email string `json:"email" validate:"required,email"`
    Age   int    `json:"age"   validate:"min=0,max=150"`
}

var validate = validator.New()

func decodeAndValidate[T any](r *http.Request, v *T) error {
    if err := json.NewDecoder(r.Body).Decode(v); err != nil {
        return fmt.Errorf("decode: %w", err)
    }
    if err := validate.Struct(v); err != nil {
        return fmt.Errorf("validate: %w", err)
    }
    return nil
}
```

## JWT: Validation Pitfalls

Never implement JWT validation by hand. Use a well-maintained library.

```go
import "github.com/golang-jwt/jwt/v5"

var jwtSecret = []byte(os.Getenv("JWT_SECRET"))

// GOOD: specify the expected algorithm explicitly
func parseToken(tokenStr string) (*jwt.RegisteredClaims, error) {
    token, err := jwt.ParseWithClaims(
        tokenStr,
        &jwt.RegisteredClaims{},
        func(t *jwt.Token) (any, error) {
            // Reject any token whose algorithm is not HMAC
            if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
            }
            return jwtSecret, nil
        },
    )
    if err != nil {
        return nil, fmt.Errorf("parse token: %w", err)
    }
    claims, ok := token.Claims.(*jwt.RegisteredClaims)
    if !ok || !token.Valid {
        return nil, errors.New("invalid token")
    }
    return claims, nil
}
```

**Common pitfalls:**
- `alg: none` attack — always reject tokens with `alg: none`.
- Algorithm confusion — always assert the expected signing method as shown above.
- Missing expiry check — `jwt.ParseWithClaims` checks `exp` by default with `golang-jwt/jwt/v5`.

## TLS Configuration Hardening

```go
import "crypto/tls"

// Minimum TLS 1.2; prefer TLS 1.3 where possible
tlsConfig := &tls.Config{
    MinVersion: tls.VersionTLS12,
    CurvePreferences: []tls.CurveID{
        tls.X25519,
        tls.CurveP256,
    },
    CipherSuites: []uint16{
        tls.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
        tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
        tls.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,
        tls.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256,
    },
}

srv := &http.Server{
    Addr:      ":443",
    Handler:   mux,
    TLSConfig: tlsConfig,
}
```

## Secret Management

```go
// GOOD: read secrets from environment
dbURL := os.Getenv("DATABASE_URL")
if dbURL == "" {
    log.Fatal("DATABASE_URL is required")
}

// BAD: hardcoded secrets
const dbPassword = "hunter2" // NEVER do this

// .env file pattern (development only — never commit .env to git)
// Use a library like github.com/joho/godotenv or direnv.
// Add .env to .gitignore.

// .gitignore
// .env
// *.local
```

For production, prefer a secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager) over env files.

## Rate Limiting with golang.org/x/time/rate

```go
import "golang.org/x/time/rate"

// Per-IP rate limiter
type IPRateLimiter struct {
    mu       sync.Mutex
    limiters map[string]*rate.Limiter
    r        rate.Limit
    b        int
}

func NewIPRateLimiter(r rate.Limit, b int) *IPRateLimiter {
    return &IPRateLimiter{
        limiters: make(map[string]*rate.Limiter),
        r:        r,
        b:        b,
    }
}

func (i *IPRateLimiter) getLimiter(ip string) *rate.Limiter {
    i.mu.Lock()
    defer i.mu.Unlock()
    if l, ok := i.limiters[ip]; ok {
        return l
    }
    l := rate.NewLimiter(i.r, i.b)
    i.limiters[ip] = l
    return l
}

// Middleware
func (i *IPRateLimiter) Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ip, _, _ := net.SplitHostPort(r.RemoteAddr)
        if !i.getLimiter(ip).Allow() {
            http.Error(w, "rate limit exceeded", http.StatusTooManyRequests)
            return
        }
        next.ServeHTTP(w, r)
    })
}

// Usage: 100 requests/second, burst of 10
limiter := NewIPRateLimiter(100, 10)
handler := limiter.Middleware(mux)
```

## Quick Reference

| Topic | Key Point |
|-------|-----------|
| SQL injection | Always use `$1`, `$2` placeholders; never interpolate |
| XSS | Use `html/template`, never `text/template` for HTML |
| CSRF | Double-submit cookie with `crypto/rand` tokens |
| JWT | Assert signing algorithm; use `golang-jwt/jwt/v5` |
| TLS | `MinVersion: tls.VersionTLS12` |
| Secrets | `os.Getenv`; never hardcode; `.env` not in git |
| Rate limiting | `golang.org/x/time/rate.NewLimiter` |
