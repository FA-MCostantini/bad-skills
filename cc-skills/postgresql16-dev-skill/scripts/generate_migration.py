#!/usr/bin/env python3
"""Generate PostgreSQL migration SQL files.

Produces timestamped migration files with proper structure:
  - BEGIN/COMMIT transaction wrapper
  - Riviere-style SQL formatting (uppercase keywords, comma-first)
  - Rollback section as comments
  - Supports create, alter, drop, and data migration types
"""

import sys
import argparse
from datetime import datetime


# ---------------------------------------------------------------------------
# Migration generators
# ---------------------------------------------------------------------------

def _table_from_name(name: str) -> str:
    """Derive table name from migration name (strip common prefixes/suffixes)."""
    for prefix in ("add_", "create_", "drop_", "alter_", "update_", "remove_"):
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    for suffix in ("_table", "_tables"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name


def _generate_create(name: str, table: str, today: str) -> str:
    return f"""\
-- Migration: {name}
-- Created: {today}
-- Description: TODO: describe this migration

BEGIN;

CREATE TABLE IF NOT EXISTS {table} (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY
  , created_at timestamptz NOT NULL DEFAULT NOW()
  , updated_at timestamptz NOT NULL DEFAULT NOW()
);

-- Create indexes
-- CREATE INDEX CONCURRENTLY idx_{table}_xxx ON {table} (xxx);

COMMIT;

-- Rollback
-- BEGIN;
-- DROP TABLE IF EXISTS {table};
-- COMMIT;
"""


def _generate_alter(name: str, table: str, today: str) -> str:
    return f"""\
-- Migration: {name}
-- Created: {today}
-- Description: TODO: describe this migration

BEGIN;

ALTER TABLE {table}
    ADD COLUMN IF NOT EXISTS new_column text;

-- CREATE INDEX CONCURRENTLY idx_{table}_new_column ON {table} (new_column);

COMMIT;

-- Rollback
-- BEGIN;
-- ALTER TABLE {table} DROP COLUMN IF EXISTS new_column;
-- COMMIT;
"""


def _generate_drop(name: str, table: str, today: str) -> str:
    return f"""\
-- Migration: {name}
-- Created: {today}
-- Description: TODO: describe this migration
--
-- WARNING: This migration drops a table. This operation is IRREVERSIBLE.
-- Ensure you have a recent backup before running this migration.
-- Consider renaming the table first and dropping after a safe period.

BEGIN;

-- Safety check: rename first, then drop after verification
-- ALTER TABLE {table} RENAME TO {table}_deprecated_{today.replace('-', '')};

DROP TABLE IF EXISTS {table};

COMMIT;

-- Rollback (only possible if you renamed instead of dropped)
-- BEGIN;
-- ALTER TABLE {table}_deprecated_{today.replace('-', '')} RENAME TO {table};
-- COMMIT;
"""


def _generate_data(name: str, table: str, today: str) -> str:
    return f"""\
-- Migration: {name}
-- Created: {today}
-- Description: TODO: describe this data migration

BEGIN;

-- INSERT example (use named parameters with your driver or $1/$2 positional)
-- INSERT INTO {table} (
--     column_one
--   , column_two
--   , created_at
-- )
-- VALUES (
--     :param_one
--   , :param_two
--   , NOW()
-- );

-- UPDATE example
-- UPDATE {table}
--    SET column_one = :new_value
--      , updated_at = NOW()
--  WHERE id = :target_id;

-- Verify row count before committing
-- SELECT COUNT(*) FROM {table} WHERE <condition>;

COMMIT;

-- Rollback
-- BEGIN;
-- DELETE FROM {table} WHERE <condition>;
-- COMMIT;
"""


# ---------------------------------------------------------------------------
# Filename generator
# ---------------------------------------------------------------------------

def _make_filename(name: str, timestamp: str) -> str:
    """Generate a timestamped filename like 20260313_120000_add_users_table.sql."""
    return f"{timestamp}_{name}.sql"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a PostgreSQL migration SQL file."
    )
    parser.add_argument(
        "name",
        help="Migration description used in filename (e.g. add_users_table)",
    )
    parser.add_argument(
        "--table",
        metavar="TABLE",
        help="Target table name (derived from migration name if omitted)",
    )
    parser.add_argument(
        "--type",
        dest="migration_type",
        choices=["create", "alter", "drop", "data"],
        default="create",
        help="Migration type: create | alter | drop | data  (default: create)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help=(
            "Output file path.  If omitted, output goes to stdout.  "
            "A timestamp prefix (YYYYMMDD_HHMMSS_<name>.sql) is prepended "
            "when a bare directory is supplied."
        ),
    )

    args = parser.parse_args()

    now       = datetime.now()
    today     = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    table = args.table or _table_from_name(args.name)

    generators = {
        "create": _generate_create,
        "alter":  _generate_alter,
        "drop":   _generate_drop,
        "data":   _generate_data,
    }
    sql = generators[args.migration_type](args.name, table, today)

    # --- write output ---
    if args.output:
        import os
        out_path = args.output
        if os.path.isdir(out_path):
            filename = _make_filename(args.name, timestamp)
            out_path = os.path.join(out_path, filename)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(sql)
        print(f"Written: {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(sql)


if __name__ == "__main__":
    main()
