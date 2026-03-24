#!/usr/bin/env python3
"""Generate a PostgreSQL PL/pgSQL function scaffold.

Produces a CREATE OR REPLACE FUNCTION statement with:
  - Typed parameter list (Riviere comma-first style)
  - DECLARE block
  - Exception handler
  - COMMENT ON FUNCTION
  - Optional SECURITY DEFINER with search_path guard
  - RETURNS TABLE support
"""

import sys
import argparse


# ---------------------------------------------------------------------------
# Parameter helpers
# ---------------------------------------------------------------------------

def _parse_params(params_str: str) -> list[tuple[str, str]]:
    """Parse 'p_user_id:bigint,p_amount:numeric' into [(name, type), ...]."""
    result = []
    for part in params_str.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            name, typ = part.split(":", 1)
            result.append((name.strip(), typ.strip()))
        else:
            result.append((part, "text"))
    return result


def _align_params(params: list[tuple[str, str]], indent: str) -> str:
    """Return aligned parameter block, comma-first Riviere style."""
    if not params:
        return "()"

    max_name = max(len(n) for n, _ in params)
    lines = []
    for i, (name, typ) in enumerate(params):
        padding = " " * (max_name - len(name))
        if i == 0:
            prefix = "    "
        else:
            prefix = f"{indent}  , "
        lines.append(f"{prefix}{name}{padding} {typ}")
    return "(\n" + "\n".join(lines) + "\n)"


def _param_type_list(params: list[tuple[str, str]]) -> str:
    """Return bare type list for COMMENT ON FUNCTION signature."""
    return ", ".join(t for _, t in params)


# ---------------------------------------------------------------------------
# Returns clause helpers
# ---------------------------------------------------------------------------

def _build_returns_clause(returns: str, params: list[tuple[str, str]]) -> str:
    """Build the RETURNS clause string."""
    upper = returns.upper()
    if upper.startswith("TABLE"):
        # Expect caller to pass e.g. "TABLE(col1 type1,col2 type2)"
        inner = returns[len("TABLE"):].strip().lstrip("(").rstrip(")")
        if inner:
            cols = _parse_params(inner.replace(",", ","))
            max_name = max(len(n) for n, _ in cols) if cols else 0
            col_lines = []
            for i, (n, t) in enumerate(cols):
                pad = " " * (max_name - len(n))
                if i == 0:
                    col_lines.append(f"    {n}{pad} {t}")
                else:
                    col_lines.append(f"  , {n}{pad} {t}")
            return "RETURNS TABLE (\n" + "\n".join(col_lines) + "\n)"
        return "RETURNS TABLE ()"
    elif upper.startswith("SETOF"):
        return f"RETURNS {returns.upper()}"
    else:
        return f"RETURNS {returns.upper()}"


# ---------------------------------------------------------------------------
# Body builder
# ---------------------------------------------------------------------------

def _declare_block(returns: str) -> tuple[str, str]:
    """Return (declare_vars, return_stmt) based on return type."""
    upper = returns.upper()
    if upper in ("VOID",):
        return ("", "    -- no return value\n")
    elif upper.startswith("TABLE") or upper.startswith("SETOF"):
        return (
            "    -- v_result <type>;\n",
            "    RETURN;\n",
        )
    else:
        return (
            f"    v_result {upper};\n",
            "    RETURN v_result;\n",
        )


def _build_function(
    name:       str,
    params:     list[tuple[str, str]],
    returns:    str,
    security:   str,
    volatile:   str,
) -> str:
    indent       = ""
    param_block  = _align_params(params, indent)
    returns_line = _build_returns_clause(returns, params)
    vol_upper    = volatile.upper()
    sec_upper    = security.upper()

    declare_vars, return_stmt = _declare_block(returns)

    # SECURITY DEFINER guard
    search_path_line = ""
    definer_warning  = ""
    if sec_upper == "DEFINER":
        search_path_line = "SET search_path = pg_catalog, public\n"
        definer_warning  = (
            "-- WARNING: SECURITY DEFINER runs with the function owner's privileges.\n"
            "-- Ensure inputs are validated and search_path is restricted.\n"
        )

    # Build parameter signature for COMMENT
    type_list = _param_type_list(params)

    lines = []

    if definer_warning:
        lines.append(definer_warning)

    lines.append(f"CREATE OR REPLACE FUNCTION {name}{param_block}")
    lines.append(f"{returns_line}")
    lines.append("LANGUAGE plpgsql")
    lines.append(vol_upper)
    lines.append(f"SECURITY {sec_upper}")
    if search_path_line:
        lines.append(search_path_line.rstrip())
    lines.append("AS $$")

    if declare_vars:
        lines.append("DECLARE")
        lines.append(declare_vars.rstrip())

    lines.append("BEGIN")
    lines.append("    -- TODO: implement function logic")
    lines.append("")
    lines.append(return_stmt.rstrip())
    lines.append("")
    lines.append("EXCEPTION")
    lines.append("    WHEN OTHERS THEN")
    lines.append(f"        RAISE WARNING 'Error in {name}: %', SQLERRM;")

    upper_ret = returns.upper()
    if upper_ret == "VOID":
        lines.append("        RETURN;")
    elif upper_ret.startswith("TABLE") or upper_ret.startswith("SETOF"):
        lines.append("        RETURN;")
    else:
        lines.append("        RETURN NULL;")

    lines.append("END;")
    lines.append("$$;")
    lines.append("")
    lines.append(f"COMMENT ON FUNCTION {name}({type_list})")
    lines.append("    IS 'TODO: describe this function';")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a PostgreSQL PL/pgSQL function scaffold."
    )
    parser.add_argument(
        "name",
        help="Function name (e.g. calculate_total)",
    )
    parser.add_argument(
        "--params",
        metavar="NAME:TYPE,...",
        default="",
        help="Comma-separated parameter pairs (e.g. p_user_id:bigint,p_amount:numeric)",
    )
    parser.add_argument(
        "--returns",
        metavar="TYPE",
        default="void",
        help=(
            "Return type: void | boolean | bigint | text | numeric | "
            "TABLE(col type,...) | SETOF type  (default: void)"
        ),
    )
    parser.add_argument(
        "--security",
        choices=["definer", "invoker"],
        default="invoker",
        help="SECURITY DEFINER or SECURITY INVOKER  (default: invoker)",
    )
    parser.add_argument(
        "--volatile",
        choices=["volatile", "stable", "immutable"],
        default="volatile",
        help="Volatility category  (default: volatile)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file (default: stdout)",
    )

    args = parser.parse_args()

    params = _parse_params(args.params) if args.params else []
    sql    = _build_function(
        name=args.name,
        params=params,
        returns=args.returns,
        security=args.security,
        volatile=args.volatile,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(sql)
        print(f"Written: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(sql)


if __name__ == "__main__":
    main()
