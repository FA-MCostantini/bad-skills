# Database Access with pgx/v5

## Connection Pool with pgxpool

```go
import (
    "context"
    "fmt"

    "github.com/jackc/pgx/v5/pgxpool"
)

func NewPool(ctx context.Context, dsn string) (*pgxpool.Pool, error) {
    cfg, err := pgxpool.ParseConfig(dsn)
    if err != nil {
        return nil, fmt.Errorf("parse pool config: %w", err)
    }

    // Tune pool settings
    cfg.MaxConns = 25
    cfg.MinConns = 5
    cfg.MaxConnLifetime = 30 * time.Minute
    cfg.MaxConnIdleTime = 5 * time.Minute

    pool, err := pgxpool.NewWithConfig(ctx, cfg)
    if err != nil {
        return nil, fmt.Errorf("create pool: %w", err)
    }

    // Verify connectivity
    if err := pool.Ping(ctx); err != nil {
        return nil, fmt.Errorf("ping database: %w", err)
    }
    return pool, nil
}
```

## Query Patterns

```go
import (
    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

// QueryRow — single row
func (r *userRepo) FindByID(ctx context.Context, id int64) (*User, error) {
    row := r.pool.QueryRow(ctx,
        `SELECT id, name, email, created_at FROM users WHERE id = $1`,
        id,
    )
    var u User
    if err := row.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt); err != nil {
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, ErrNotFound
        }
        return nil, fmt.Errorf("find user %d: %w", id, err)
    }
    return &u, nil
}

// Query + pgx.CollectRows — multiple rows
func (r *userRepo) FindAll(ctx context.Context) ([]*User, error) {
    rows, err := r.pool.Query(ctx, `SELECT id, name, email, created_at FROM users`)
    if err != nil {
        return nil, fmt.Errorf("find all users: %w", err)
    }
    users, err := pgx.CollectRows(rows, pgx.RowToAddrOfStructByName[User])
    if err != nil {
        return nil, fmt.Errorf("collect users: %w", err)
    }
    return users, nil
}

// Exec — insert / update / delete
func (r *userRepo) Create(ctx context.Context, u *User) error {
    _, err := r.pool.Exec(ctx,
        `INSERT INTO users (name, email) VALUES ($1, $2)`,
        u.Name, u.Email,
    )
    if err != nil {
        return fmt.Errorf("create user: %w", err)
    }
    return nil
}

// Named args for readability
func (r *userRepo) Update(ctx context.Context, u *User) error {
    _, err := r.pool.Exec(ctx,
        `UPDATE users SET name = @name, email = @email WHERE id = @id`,
        pgx.NamedArgs{"name": u.Name, "email": u.Email, "id": u.ID},
    )
    return err
}
```

## Transactions

```go
// Begin a transaction and defer rollback.
// Rollback is a no-op after a successful Commit.
func (r *userRepo) TransferCredits(ctx context.Context, fromID, toID int64, amount int) error {
    tx, err := r.pool.BeginTx(ctx, pgx.TxOptions{})
    if err != nil {
        return fmt.Errorf("begin tx: %w", err)
    }
    defer tx.Rollback(ctx) // no-op after Commit

    _, err = tx.Exec(ctx,
        `UPDATE accounts SET credits = credits - $1 WHERE id = $2`,
        amount, fromID,
    )
    if err != nil {
        return fmt.Errorf("deduct credits: %w", err)
    }

    _, err = tx.Exec(ctx,
        `UPDATE accounts SET credits = credits + $1 WHERE id = $2`,
        amount, toID,
    )
    if err != nil {
        return fmt.Errorf("add credits: %w", err)
    }

    if err := tx.Commit(ctx); err != nil {
        return fmt.Errorf("commit: %w", err)
    }
    return nil
}
```

## Named Args

```go
import "github.com/jackc/pgx/v5"

result, err := pool.Exec(ctx,
    `INSERT INTO products (name, price, stock) VALUES (@name, @price, @stock)`,
    pgx.NamedArgs{
        "name":  "Widget",
        "price": 9.99,
        "stock": 100,
    },
)
```

## Error Handling: Constraint Violations

```go
import (
    "github.com/jackc/pgx/v5/pgconn"
)

const (
    pgUniqueViolation     = "23505"
    pgForeignKeyViolation = "23503"
    pgNotNullViolation    = "23502"
)

func translatePgError(err error) error {
    var pgErr *pgconn.PgError
    if errors.As(err, &pgErr) {
        switch pgErr.Code {
        case pgUniqueViolation:
            return ErrConflict
        case pgForeignKeyViolation:
            return ErrNotFound
        }
    }
    return err
}

func (r *userRepo) Create(ctx context.Context, u *User) error {
    _, err := r.pool.Exec(ctx,
        `INSERT INTO users (email) VALUES ($1)`,
        u.Email,
    )
    if err != nil {
        return translatePgError(err)
    }
    return nil
}
```

## Migration Tools

### goose

```bash
# Install
go install github.com/pressly/goose/v3/cmd/goose@latest

# Create migration
goose -dir migrations create add_users_table sql

# Apply
goose -dir migrations postgres "$DATABASE_URL" up

# Rollback last
goose -dir migrations postgres "$DATABASE_URL" down
```

```sql
-- migrations/001_create_users.sql
-- +goose Up
CREATE TABLE users (
    id         BIGSERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- +goose Down
DROP TABLE users;
```

### golang-migrate

```bash
migrate -path migrations -database "$DATABASE_URL" up
```

## Batch Operations

```go
import "github.com/jackc/pgx/v5"

func (r *userRepo) BulkCreate(ctx context.Context, users []*User) error {
    batch := &pgx.Batch{}
    for _, u := range users {
        batch.Queue(
            `INSERT INTO users (name, email) VALUES ($1, $2)`,
            u.Name, u.Email,
        )
    }

    results := r.pool.SendBatch(ctx, batch)
    defer results.Close()

    for range users {
        if _, err := results.Exec(); err != nil {
            return fmt.Errorf("batch insert: %w", translatePgError(err))
        }
    }
    return nil
}
```

## Repository Pattern

```go
// Interface — defined in the domain layer
type UserRepository interface {
    Find(ctx context.Context, id int64) (*User, error)
    FindAll(ctx context.Context) ([]*User, error)
    Create(ctx context.Context, u *User) error
    Update(ctx context.Context, u *User) error
    Delete(ctx context.Context, id int64) error
}

// Postgres implementation
type postgresUserRepository struct {
    pool *pgxpool.Pool
}

func NewPostgresUserRepository(pool *pgxpool.Pool) UserRepository {
    return &postgresUserRepository{pool: pool}
}

// Compile-time interface check
var _ UserRepository = (*postgresUserRepository)(nil)

func (r *postgresUserRepository) Find(ctx context.Context, id int64) (*User, error) {
    row := r.pool.QueryRow(ctx,
        `SELECT id, name, email, created_at FROM users WHERE id = $1`, id,
    )
    var u User
    if err := row.Scan(&u.ID, &u.Name, &u.Email, &u.CreatedAt); err != nil {
        if errors.Is(err, pgx.ErrNoRows) {
            return nil, ErrNotFound
        }
        return nil, fmt.Errorf("find user %d: %w", id, err)
    }
    return &u, nil
}

func (r *postgresUserRepository) FindAll(ctx context.Context) ([]*User, error) {
    rows, err := r.pool.Query(ctx, `SELECT id, name, email, created_at FROM users`)
    if err != nil {
        return nil, fmt.Errorf("find all users: %w", err)
    }
    return pgx.CollectRows(rows, pgx.RowToAddrOfStructByName[User])
}

func (r *postgresUserRepository) Create(ctx context.Context, u *User) error {
    tag, err := r.pool.Exec(ctx,
        `INSERT INTO users (name, email) VALUES ($1, $2)`,
        u.Name, u.Email,
    )
    if err != nil {
        return translatePgError(err)
    }
    if tag.RowsAffected() == 0 {
        return fmt.Errorf("create user: no rows affected")
    }
    return nil
}

func (r *postgresUserRepository) Update(ctx context.Context, u *User) error {
    tag, err := r.pool.Exec(ctx,
        `UPDATE users SET name = $1, email = $2 WHERE id = $3`,
        u.Name, u.Email, u.ID,
    )
    if err != nil {
        return translatePgError(err)
    }
    if tag.RowsAffected() == 0 {
        return ErrNotFound
    }
    return nil
}

func (r *postgresUserRepository) Delete(ctx context.Context, id int64) error {
    tag, err := r.pool.Exec(ctx,
        `DELETE FROM users WHERE id = $1`, id,
    )
    if err != nil {
        return fmt.Errorf("delete user %d: %w", id, err)
    }
    if tag.RowsAffected() == 0 {
        return ErrNotFound
    }
    return nil
}
```

## Quick Reference

| Operation | API |
|-----------|-----|
| Single row | `pool.QueryRow(ctx, sql, args...)` |
| Multiple rows | `pool.Query(ctx, sql, args...)` + `pgx.CollectRows` |
| Execute (no rows) | `pool.Exec(ctx, sql, args...)` |
| Named args | `pgx.NamedArgs{"key": val}` |
| Transaction | `pool.BeginTx` / `tx.Commit` / `defer tx.Rollback` |
| Batch | `pgx.Batch{}` + `pool.SendBatch` |
| No rows error | `pgx.ErrNoRows` |
| Constraint error | `*pgconn.PgError` with `.Code` |
