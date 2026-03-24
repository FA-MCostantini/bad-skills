# Error Handling

## Wrapping Errors with fmt.Errorf

Use `%w` to wrap an error so callers can inspect it with `errors.Is` and `errors.As`.

```go
func getUser(id int64) (*User, error) {
    user, err := db.QueryUser(id)
    if err != nil {
        return nil, fmt.Errorf("getUser id=%d: %w", id, err)
    }
    return user, nil
}
```

The wrapping chain is preserved: `fmt.Errorf("...: %w", err)` creates a new error whose `Unwrap()` returns `err`.

## errors.Join (Go 1.20+)

`errors.Join` combines multiple errors into one. Both are accessible via `errors.Is` / `errors.As`.

```go
func validate(u *User) error {
    var errs []error
    if u.Name == "" {
        errs = append(errs, errors.New("name is required"))
    }
    if u.Email == "" {
        errs = append(errs, errors.New("email is required"))
    }
    return errors.Join(errs...) // nil if errs is empty
}
```

## Sentinel Errors

Declare package-level sentinel errors for conditions callers need to distinguish.

```go
var (
    ErrNotFound   = errors.New("not found")
    ErrConflict   = errors.New("conflict")
    ErrUnauthorized = errors.New("unauthorized")
)

func (r *userRepository) Find(ctx context.Context, id int64) (*User, error) {
    // ...
    if pgx.ErrNoRows == err {
        return nil, ErrNotFound
    }
    return user, nil
}
```

## Custom Error Types

Implement `Error()` for the message, `Unwrap()` to expose the cause, `Is()` for identity comparison, and `As()` for type-asserting wrapped errors.

```go
// ValidationError carries field-level detail.
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error: field %q — %s", e.Field, e.Message)
}

// Is lets errors.Is match any *ValidationError regardless of field.
func (e *ValidationError) Is(target error) bool {
    _, ok := target.(*ValidationError)
    return ok
}

// NotFoundError wraps an underlying cause.
type NotFoundError struct {
    Resource string
    ID       any
    Cause    error
}

func (e *NotFoundError) Error() string {
    return fmt.Sprintf("%s with id %v not found", e.Resource, e.ID)
}

func (e *NotFoundError) Unwrap() error { return e.Cause }
```

## errors.Is and errors.As

`errors.Is` traverses the error chain comparing by value (or via `Is()` method).
`errors.As` traverses the chain and type-asserts to the target type.

```go
// errors.Is — check for a specific sentinel or type
err := getUser(42)
if errors.Is(err, ErrNotFound) {
    // handle not found
}

// errors.As — extract concrete type from the chain
var valErr *ValidationError
if errors.As(err, &valErr) {
    fmt.Println("bad field:", valErr.Field)
}
```

## Error Translation at Layer Boundaries

Translate low-level errors at each layer boundary so the caller receives the vocabulary appropriate to its level.

```go
// Repository layer: translates storage errors → domain errors
func (r *postgresUserRepo) Find(ctx context.Context, id int64) (*User, error) {
    row := r.pool.QueryRow(ctx, `SELECT id, name, email FROM users WHERE id = $1`, id)
    var u User
    if err := row.Scan(&u.ID, &u.Name, &u.Email); err != nil {
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, ErrNotFound
        }
        return nil, fmt.Errorf("find user %d: %w", id, err)
    }
    return &u, nil
}

// Service layer: may add business-rule context
func (s *userService) GetProfile(ctx context.Context, id int64) (*Profile, error) {
    user, err := s.repo.Find(ctx, id)
    if err != nil {
        return nil, fmt.Errorf("get profile: %w", err) // preserves ErrNotFound
    }
    return toProfile(user), nil
}

// HTTP handler: translates domain errors → HTTP status codes
func (h *handler) handleGetUser(w http.ResponseWriter, r *http.Request) {
    id, _ := strconv.ParseInt(r.PathValue("id"), 10, 64)
    profile, err := h.svc.GetProfile(r.Context(), id)
    if err != nil {
        switch {
        case errors.Is(err, ErrNotFound):
            http.Error(w, "not found", http.StatusNotFound)
        case errors.Is(err, ErrUnauthorized):
            http.Error(w, "unauthorized", http.StatusUnauthorized)
        default:
            http.Error(w, "internal server error", http.StatusInternalServerError)
        }
        return
    }
    _ = json.NewEncoder(w).Encode(profile)
}
```

## Anti-Patterns

```go
// BAD: creating a new errors.New at every call site loses the ability to use errors.Is
func findUser(id int) (*User, error) {
    if id == 0 {
        return nil, errors.New("user not found") // different instance each call
    }
    // ...
}

// GOOD: use a package-level sentinel
var ErrNotFound = errors.New("not found")

func findUser(id int) (*User, error) {
    if id == 0 {
        return nil, ErrNotFound
    }
    // ...
}

// BAD: ignoring errors
user, _ := repo.Find(ctx, id)

// GOOD: always handle errors
user, err := repo.Find(ctx, id)
if err != nil {
    return fmt.Errorf("...: %w", err)
}

// BAD: logging and returning the same error (double-logging)
if err != nil {
    log.Printf("error: %v", err)
    return err
}

// GOOD: either log or return, not both — let the boundary layer log
if err != nil {
    return fmt.Errorf("context: %w", err)
}
```

## Quick Reference

| Function | Purpose |
|----------|---------|
| `fmt.Errorf("...: %w", err)` | Wrap with context, preserving chain |
| `errors.New("msg")` | Sentinel / leaf error |
| `errors.Join(e1, e2)` | Combine multiple errors (Go 1.20+) |
| `errors.Is(err, target)` | Check chain for sentinel or via `Is()` |
| `errors.As(err, &target)` | Extract concrete type from chain |
| `err.Unwrap()` | Return wrapped cause |
