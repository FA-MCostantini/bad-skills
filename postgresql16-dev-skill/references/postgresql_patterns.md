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
