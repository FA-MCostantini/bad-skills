#!/usr/bin/env python3
"""Generate PostgreSQL trigger and trigger-function scaffolds.

Supports three trigger archetypes:
  updated_at  – lightweight function that stamps NEW.updated_at = NOW()
  audit       – full audit-log table + SECURITY DEFINER function
  custom      – blank skeleton for arbitrary trigger logic
"""

import sys
import argparse


# ---------------------------------------------------------------------------
# Trigger generators
# ---------------------------------------------------------------------------

def _generate_updated_at(table: str, timing: str, events: list[str], for_each: str) -> str:
    func_name    = "trigger_set_updated_at"
    trigger_name = f"trg_{table}_set_updated_at"
    events_str   = " OR ".join(e.upper() for e in events)

    return f"""\
CREATE OR REPLACE FUNCTION {func_name}()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER {trigger_name}
    {timing.upper()} {events_str} ON {table}
    FOR EACH {for_each.upper()}
    EXECUTE FUNCTION {func_name}();
"""


def _generate_audit(table: str, timing: str, for_each: str) -> str:
    audit_table  = f"{table}_audit"
    func_name    = f"trigger_audit_{table}"
    trigger_name = f"trg_{table}_audit"

    return f"""\
-- Audit table (create if not exists)
CREATE TABLE IF NOT EXISTS {audit_table} (
    audit_id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY
  , operation  text NOT NULL
  , changed_at timestamptz NOT NULL DEFAULT NOW()
  , changed_by text DEFAULT current_setting('app.current_user_id', true)
  , old_data   jsonb
  , new_data   jsonb
);

CREATE OR REPLACE FUNCTION {func_name}()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO {audit_table} (operation, old_data)
        VALUES ('DELETE', to_jsonb(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO {audit_table} (operation, old_data, new_data)
        VALUES ('UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO {audit_table} (operation, new_data)
        VALUES ('INSERT', to_jsonb(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$;

CREATE TRIGGER {trigger_name}
    AFTER INSERT OR UPDATE OR DELETE ON {table}
    FOR EACH {for_each.upper()}
    EXECUTE FUNCTION {func_name}();
"""


def _generate_custom(
    name:     str,
    table:    str,
    timing:   str,
    events:   list[str],
    for_each: str,
) -> str:
    func_name    = f"trigger_{name}"
    trigger_name = f"trg_{table}_{name}"
    events_str   = " OR ".join(e.upper() for e in events)

    # For ROW-level triggers the function must RETURN NEW or OLD.
    # For STATEMENT-level triggers it must RETURN NULL.
    if for_each.upper() == "ROW":
        return_stmt = "    RETURN NEW;"
    else:
        return_stmt = "    RETURN NULL;"

    return f"""\
CREATE OR REPLACE FUNCTION {func_name}()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- TODO: implement trigger logic
    -- TG_OP  holds the operation: INSERT | UPDATE | DELETE | TRUNCATE
    -- NEW    holds the new row  (INSERT, UPDATE)
    -- OLD    holds the old row  (UPDATE, DELETE)
{return_stmt}
END;
$$;

CREATE TRIGGER {trigger_name}
    {timing.upper()} {events_str} ON {table}
    FOR EACH {for_each.upper()}
    EXECUTE FUNCTION {func_name}();
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a PostgreSQL trigger and trigger-function scaffold."
    )
    parser.add_argument(
        "name",
        help="Trigger/function base name (e.g. set_updated_at, audit_changes)",
    )
    parser.add_argument(
        "--table",
        required=True,
        metavar="TABLE",
        help="Target table name",
    )
    parser.add_argument(
        "--timing",
        choices=["BEFORE", "AFTER", "before", "after"],
        default="BEFORE",
        help="Trigger timing: BEFORE | AFTER  (default: BEFORE)",
    )
    parser.add_argument(
        "--events",
        metavar="INSERT,UPDATE,DELETE",
        default="UPDATE",
        help="Comma-separated list of trigger events  (default: UPDATE)",
    )
    parser.add_argument(
        "--for-each",
        dest="for_each",
        choices=["ROW", "STATEMENT", "row", "statement"],
        default="ROW",
        help="FOR EACH ROW | STATEMENT  (default: ROW)",
    )
    parser.add_argument(
        "--type",
        dest="trigger_type",
        choices=["audit", "updated_at", "custom"],
        default="custom",
        help="Trigger archetype: audit | updated_at | custom  (default: custom)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file (default: stdout)",
    )

    args = parser.parse_args()

    events   = [e.strip().upper() for e in args.events.split(",") if e.strip()]
    timing   = args.timing.upper()
    for_each = args.for_each.upper()

    if args.trigger_type == "updated_at":
        sql = _generate_updated_at(args.table, timing, events, for_each)
    elif args.trigger_type == "audit":
        sql = _generate_audit(args.table, timing, for_each)
    else:
        sql = _generate_custom(args.name, args.table, timing, events, for_each)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(sql)
        print(f"Written: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(sql)


if __name__ == "__main__":
    main()
