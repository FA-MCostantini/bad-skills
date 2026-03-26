#!/usr/bin/env python3
"""Generate PostgreSQL Row-Level Security (RLS) policy statements.

Produces ENABLE ROW LEVEL SECURITY plus one CREATE POLICY per operation
(SELECT, INSERT, UPDATE, DELETE) for tenant-isolation and/or owner-based access.
"""

import sys
import argparse


# ---------------------------------------------------------------------------
# Policy builders
# ---------------------------------------------------------------------------

def _tenant_expr(tenant_col: str, setting: str) -> str:
    """Return the USING / WITH CHECK expression for tenant isolation."""
    return f"{tenant_col} = current_setting('{setting}')::bigint"


def _owner_expr(owner_col: str) -> str:
    """Return the USING / WITH CHECK expression for owner-based access."""
    return f"{owner_col} = current_setting('app.current_user_id')::bigint"


def _combine(tenant_expr: str | None, owner_expr: str | None) -> str:
    """Combine tenant and owner expressions with OR."""
    parts = [e for e in (tenant_expr, owner_expr) if e]
    if len(parts) == 1:
        return parts[0]
    return "(\n        " + "\n     OR ".join(parts) + "\n    )"


def _build_policies(
    table:         str,
    tenant_col:    str | None,
    owner_col:     str | None,
    setting:       str,
    force:         bool,
) -> str:
    lines = []

    lines.append(f"-- Enable Row-Level Security")
    lines.append(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
    lines.append("")

    t_expr = _tenant_expr(tenant_col, setting) if tenant_col else None
    o_expr = _owner_expr(owner_col)             if owner_col  else None

    if t_expr is None and o_expr is None:
        lines.append("-- WARNING: no --tenant-column or --owner-column supplied.")
        lines.append("-- Add at least one to generate meaningful policies.")
        lines.append("")
    else:
        using_expr      = _combine(t_expr, o_expr)
        check_expr      = using_expr
        policy_suffix   = "tenant_isolation" if tenant_col else "owner_access"

        # SELECT
        lines.append(f"-- {policy_suffix.replace('_', ' ').title()} policy (all operations)")
        lines.append(f"CREATE POLICY {policy_suffix}_select ON {table}")
        lines.append(f"    FOR SELECT")
        lines.append(f"    USING ({using_expr});")
        lines.append("")

        # INSERT
        lines.append(f"CREATE POLICY {policy_suffix}_insert ON {table}")
        lines.append(f"    FOR INSERT")
        lines.append(f"    WITH CHECK ({check_expr});")
        lines.append("")

        # UPDATE
        lines.append(f"CREATE POLICY {policy_suffix}_update ON {table}")
        lines.append(f"    FOR UPDATE")
        lines.append(f"    USING ({using_expr})")
        lines.append(f"    WITH CHECK ({check_expr});")
        lines.append("")

        # DELETE
        lines.append(f"CREATE POLICY {policy_suffix}_delete ON {table}")
        lines.append(f"    FOR DELETE")
        lines.append(f"    USING ({using_expr});")
        lines.append("")

    if force:
        lines.append("-- Force RLS for table owners too")
        lines.append(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
        lines.append("")

    # Handy test snippet
    setting_example = setting
    lines.append(f"-- Test: SET LOCAL {setting_example} = '1'; SELECT * FROM {table};")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate PostgreSQL Row-Level Security (RLS) policies."
    )
    parser.add_argument(
        "--table",
        required=True,
        metavar="TABLE",
        help="Target table name",
    )
    parser.add_argument(
        "--tenant-column",
        metavar="COLUMN",
        default=None,
        help="Column used for tenant isolation (e.g. tenant_id)",
    )
    parser.add_argument(
        "--owner-column",
        metavar="COLUMN",
        default=None,
        help="Column used for owner-based access (e.g. owner_id)",
    )
    parser.add_argument(
        "--setting",
        metavar="SETTING",
        default="app.current_tenant_id",
        help="App setting name for tenant ID  (default: app.current_tenant_id)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Add FORCE ROW LEVEL SECURITY (applies RLS to table owner too)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file (default: stdout)",
    )

    args = parser.parse_args()

    sql = _build_policies(
        table=args.table,
        tenant_col=args.tenant_column,
        owner_col=args.owner_column,
        setting=args.setting,
        force=args.force,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(sql)
        print(f"Written: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(sql)


if __name__ == "__main__":
    main()
