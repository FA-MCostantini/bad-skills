---
name: postgresql16-dev-skill
description: PostgreSQL 16 development specialist for enterprise database operations. Use when writing SQL queries, designing database schemas, creating migrations, optimizing query performance, working with indexes, UPSERT patterns, window functions, CTEs, JSONB operations, locking strategies, or any PostgreSQL-specific task. Covers named parameter binding, Riviere SQL formatting standard, EXPLAIN ANALYZE workflows, and batch operations with UNNEST. Activates autonomously when SQL or database context is detected.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
metadata:
  author: Mattia Costantini
  version: "1.0.0"
  domain: language
  triggers: sql postgresql query database schema migration index upsert insert update delete select
  role: specialist
  scope: implementation
  output-format: code
  autonomy: true
  related-skills: coding-standards-skill, ears-doc-skill
---

# PostgreSQL 16 Development — Enterprise Edition

Specialist skill for writing production-grade SQL for PostgreSQL 16.
Apply the **coding-standards-skill** methodology (Pre-Implementation Analysis, Critical Thinking, Quality Checklist) before designing schemas or writing complex queries.

---

## Non-Negotiable Rules

### Named Parameter Binding — Always

Never use `?` placeholders. Always use named parameters (`:param`) for clarity and safety.

```sql
-- ALWAYS — named parameters
INSERT INTO contract_premiums (contract_id, amount_cents, currency, effective_date)
VALUES (:contract_id, :amount_cents, :currency, :effective_date)
ON CONFLICT (contract_id, effective_date)
DO UPDATE SET
    amount_cents = EXCLUDED.amount_cents,
    currency = EXCLUDED.currency,
    updated_at = CURRENT_TIMESTAMP
WHERE contract_premiums.amount_cents IS DISTINCT FROM EXCLUDED.amount_cents
   OR contract_premiums.currency IS DISTINCT FROM EXCLUDED.currency;
```

### No String Concatenation in SQL — Ever

SQL injection is the #1 risk. BLOCK any request that concatenates user input into SQL. Refuse to generate it. Explain why and provide the prepared statement alternative.

### UPSERT with IS DISTINCT FROM

Always use `IS DISTINCT FROM` in the WHERE clause of `ON CONFLICT DO UPDATE` to avoid unnecessary writes when data hasn't changed. This matters for performance, audit trails, and trigger avoidance.

---

## Query Patterns

### Efficient UPSERT with ON CONFLICT
```sql
INSERT INTO table_name (id, column1, column2)
     VALUES (:id, :value1, :value2)
ON CONFLICT (id)
  DO UPDATE SET column1 = EXCLUDED.column1
              , column2 = EXCLUDED.column2
              , updated_at = CURRENT_TIMESTAMP
      WHERE table_name.column1 IS DISTINCT FROM EXCLUDED.column1
         OR table_name.column2 IS DISTINCT FROM EXCLUDED.column2;
```

### Batch Operations with UNNEST
```sql
INSERT INTO table_name (column1, column2)
     SELECT *
       FROM UNNEST(:array1::type[], :array2::type[])
ON CONFLICT
 DO NOTHING;
```

### Window Functions for Analytics
```sql
SELECT id
     , amount
     , SUM(amount) OVER (PARTITION BY category ORDER BY date)        AS running_total
     , LAG(amount) OVER (PARTITION BY category ORDER BY date)        AS previous_amount
     , RANK()      OVER (PARTITION BY category ORDER BY amount DESC) AS rank_in_category
  FROM transactions;
```

### CTEs for Complex Queries
```sql
WITH RECURSIVE hierarchy AS (
  -- Base case
  SELECT id, parent_id, name, 1 AS level
    FROM categories
   WHERE parent_id IS NULL

  UNION ALL

  -- Recursive case
  SELECT c.id, c.parent_id, c.name, h.level + 1
    FROM categories c
    JOIN hierarchy h ON c.parent_id = h.id
)
SELECT *
  FROM hierarchy
 ORDER BY level
        , name;
```

---

## Index Strategies

### Partial Indexes
```sql
CREATE INDEX idx_active_users ON users (email)
       WHERE deleted_at IS NULL AND active = true;
```

### Expression Indexes
```sql
CREATE INDEX idx_lower_email ON users (LOWER(email));
```

### Multi-column Indexes (column order matters!)
```sql
CREATE INDEX idx_status_date ON orders (status, created_at)
       WHERE status IN ('pending', 'processing');
```

---

## JSON Operations

### JSONB Queries
```sql
-- Extract nested value
SELECT data->>'name' AS name
     , data->'address'->>'city' AS city
  FROM users
 WHERE data @> '{"active": true}'::jsonb;

-- Update JSONB field
UPDATE users
   SET data = jsonb_set( data
                       , '{address,city}'
                       , '"New York"'::jsonb
                       , true)
 WHERE id = :id;
```

---

## Locking Patterns

### Skip Locked for Queue Processing
```sql
SELECT id, payload
  FROM job_queue
 WHERE status = 'pending'
 ORDER BY priority DESC, created_at
 LIMIT 1
   FOR UPDATE SKIP LOCKED;
```

### Advisory Locks
```sql
-- Acquire lock
SELECT pg_advisory_lock(:lock_id);

-- Try to acquire (non-blocking)
SELECT pg_try_advisory_lock(:lock_id);

-- Release
SELECT pg_advisory_unlock(:lock_id);
```

---

## Query Optimization Checklist

1. **Use EXPLAIN ANALYZE** for execution plans — always on complex queries
2. **Avoid SELECT \*** in production code — list columns explicitly
3. **Use EXISTS instead of COUNT** for existence checks
4. **Prefer JOIN over subqueries** when possible
5. **Use COPY for bulk inserts** instead of multiple INSERTs
6. **Consider materialized views** for expensive aggregations
7. **Use prepared statements** with named parameters
8. **Alert if DELETE without WHERE** in production code

---

## Migration Workflow

1. Analyze current schema and data dependencies.
2. Generate migration with proper rollback (`CREATE` / `DROP`, `ADD` / `DROP`).
3. Include data migration if needed (separate step).
4. Add indexes AFTER data migration (avoids slow writes during migration).
5. Test rollback path on a copy of production data.
6. Run `EXPLAIN ANALYZE` on affected queries post-migration.

---

## Auto-Loading Rules

| Condition | File to Load |
|-----------|-------------|
| SQL query, database schema, migration, index, UPSERT, window functions | `references/postgresql_patterns.md` |

When in doubt, load the reference. Better to have it and not need it.

---

## Available Scripts

**format_sql_riviere.py** — Format SQL to Riviere standard
```bash
python3 scripts/format_sql_riviere.py "SELECT * FROM users WHERE active = true"
python3 scripts/format_sql_riviere.py -f query.sql
```

---

## Critical Reminders

- **NEVER** concatenate SQL strings — prepared statements only.
- **ALWAYS** use named parameters (`:param`), never positional (`?`).
- **ALWAYS** use `IS DISTINCT FROM` in UPSERT WHERE clauses.
- **ALWAYS** run `EXPLAIN ANALYZE` before deploying complex queries.
- **PREFER** partial indexes over full-table indexes.
- **PREFER** `EXISTS` over `COUNT(*)` for existence checks.
- **ALERT** on `DELETE` without `WHERE` — confirm intent with user.
