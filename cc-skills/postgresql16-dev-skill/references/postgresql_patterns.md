# PostgreSQL 16 Optimization Patterns

## Performance Patterns

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

## Query Optimization Tips

1. **Use EXPLAIN ANALYZE** for execution plans
2. **Avoid SELECT * ** in production code
3. **Use EXISTS instead of COUNT** for existence checks
4. **Prefer JOIN over subqueries** when possible
5. **Use COPY for bulk inserts** instead of multiple INSERTs
6. **Consider materialized views** for expensive aggregations
7. **Use prepared statements** with named parameters
8. **Alert if DELETE without WHERE** in production code

---

## PG16 SQL/JSON Standard Functions

```sql
-- JSON_EXISTS: check if path exists
SELECT *
  FROM orders
 WHERE JSON_EXISTS(data, '$.shipping.tracking_number');

-- JSON_VALUE: extract scalar value
SELECT JSON_VALUE(data, '$.customer.name' RETURNING text) AS customer_name
  FROM orders;

-- JSON_QUERY: extract JSON object/array
SELECT JSON_QUERY(data, '$.items' WITH WRAPPER) AS items
  FROM orders;

-- JSON_TABLE: transform JSON into relational rows
SELECT jt.*
  FROM orders
     , JSON_TABLE(
         data
       , '$.items[*]'
         COLUMNS (
             product_name text PATH '$.name'
           , quantity     int  PATH '$.qty'
           , price        numeric PATH '$.price'
         )
       ) AS jt;

-- IS JSON predicate
SELECT *
  FROM raw_imports
 WHERE payload IS JSON;
```

---

## MERGE Statement

```sql
MERGE INTO inventory AS target
USING incoming_stock AS source
   ON target.product_id = source.product_id
 WHEN MATCHED THEN
      UPDATE SET quantity = target.quantity + source.quantity
               , updated_at = NOW()
 WHEN NOT MATCHED THEN
      INSERT (product_id, quantity, updated_at)
      VALUES (source.product_id, source.quantity, NOW());
```

---

## LATERAL Joins

```sql
-- Top-N per group
SELECT d.name AS department
     , emp.name AS employee
     , emp.salary
  FROM departments d
     , LATERAL (
         SELECT e.name
              , e.salary
           FROM employees e
          WHERE e.department_id = d.id
          ORDER BY e.salary DESC
          LIMIT 3
       ) AS emp;
```

---

## Window Functions — Complete Reference

```sql
-- ROW_NUMBER, RANK, DENSE_RANK
SELECT id
     , name
     , salary
     , ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num
     , RANK()       OVER (ORDER BY salary DESC) AS rank
     , DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
  FROM employees;

-- LAG and LEAD
SELECT date
     , amount
     , LAG(amount, 1)  OVER (ORDER BY date) AS prev_amount
     , LEAD(amount, 1) OVER (ORDER BY date) AS next_amount
  FROM transactions;

-- NTILE for bucketing
SELECT name
     , salary
     , NTILE(4) OVER (ORDER BY salary) AS quartile
  FROM employees;

-- FIRST_VALUE / LAST_VALUE with frame
SELECT id
     , amount
     , FIRST_VALUE(amount) OVER w AS first_amount
     , LAST_VALUE(amount)  OVER w AS last_amount
  FROM transactions
WINDOW w AS (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING);

-- Named WINDOW definition
SELECT id
     , SUM(amount) OVER w AS running_total
     , AVG(amount) OVER w AS running_avg
  FROM transactions
WINDOW w AS (PARTITION BY account_id ORDER BY date);
```

---

## Table Partitioning

```sql
-- Range partition (by date)
CREATE TABLE events (
    id         bigint GENERATED ALWAYS AS IDENTITY
  , event_date date NOT NULL
  , payload    jsonb
) PARTITION BY RANGE (event_date);

CREATE TABLE events_2024_q1 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE events_2024_q2 PARTITION OF events
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- List partition
CREATE TABLE orders (
    id     bigint GENERATED ALWAYS AS IDENTITY
  , region text NOT NULL
  , total  numeric
) PARTITION BY LIST (region);

CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('eu-west', 'eu-east');
CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('us-east', 'us-west');

-- Default partition
CREATE TABLE orders_other PARTITION OF orders DEFAULT;

-- Hash partition
CREATE TABLE sessions (
    id      uuid PRIMARY KEY
  , user_id bigint NOT NULL
) PARTITION BY HASH (user_id);

CREATE TABLE sessions_0 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessions_1 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 1);
```

---

## Full-Text Search

```sql
-- Basic full-text search
SELECT title
     , ts_rank(search_vector, query) AS rank
  FROM articles
     , to_tsquery('english', 'database & performance') AS query
 WHERE search_vector @@ query
 ORDER BY rank DESC;

-- Stored tsvector column with GIN index
ALTER TABLE articles ADD COLUMN search_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
    ) STORED;

CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);
```

---

## Row-Level Security (RLS)

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policy
CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_setting('app.current_tenant_id')::bigint);

-- Role-based read policy
CREATE POLICY read_own ON documents
    FOR SELECT
    USING (owner_id = current_setting('app.current_user_id')::bigint
        OR current_setting('app.current_role') = 'admin');

-- Write policy with WITH CHECK
CREATE POLICY insert_own ON documents
    FOR INSERT
    WITH CHECK (owner_id = current_setting('app.current_user_id')::bigint);

-- Apply RLS to table owners too
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

---

## Index Patterns — Extended

```sql
-- Covering index with INCLUDE (index-only scans)
CREATE INDEX idx_orders_customer_covering
    ON orders (customer_id)
    INCLUDE (status, total, created_at);

-- GIN index for JSONB
CREATE INDEX idx_products_attrs ON products USING GIN (attributes jsonb_path_ops);

-- BRIN index for time-series (very small, ideal for append-only)
CREATE INDEX idx_logs_created ON logs USING BRIN (created_at);

-- ALWAYS use CONCURRENTLY on production tables
CREATE INDEX CONCURRENTLY idx_users_email ON users (lower(email));
```

---

## COPY for Bulk Operations

```sql
-- Import from CSV
COPY products (name, price, category)
FROM '/path/to/data.csv'
WITH (FORMAT CSV, HEADER true, DELIMITER ',');

-- Export to CSV
COPY (SELECT * FROM orders WHERE created_at > '2024-01-01')
TO '/path/to/export.csv'
WITH (FORMAT CSV, HEADER true);

-- From stdin (application use via driver)
COPY products (name, price) FROM STDIN WITH (FORMAT CSV);
```

---

## VACUUM and Maintenance

```sql
-- Analyze specific table
ANALYZE orders;

-- Vacuum and analyze
VACUUM ANALYZE orders;

-- Check for bloat
SELECT relname
     , n_dead_tup
     , n_live_tup
     , round(n_dead_tup::numeric / GREATEST(n_live_tup, 1) * 100, 2) AS dead_pct
  FROM pg_stat_user_tables
 WHERE n_dead_tup > 1000
 ORDER BY n_dead_tup DESC;

-- Rebuild index without locking
REINDEX INDEX CONCURRENTLY idx_orders_customer;

-- Find unused indexes
SELECT schemaname
     , relname
     , indexrelname
     , idx_scan
  FROM pg_stat_user_indexes
 WHERE idx_scan = 0
   AND indexrelname NOT LIKE '%_pkey'
 ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Connection Pooling Notes

```
-- PgBouncer Transaction Mode Caveats:
-- ✗ Prepared statements (use simple protocol or pgbouncer's prepared_statement_count)
-- ✗ SET session variables (use SET LOCAL inside transaction)
-- ✗ Advisory session locks (use pg_advisory_xact_lock instead)
-- ✗ LISTEN/NOTIFY
-- ✓ SET LOCAL works (transaction-scoped)
-- ✓ Temporary tables within transaction
```
