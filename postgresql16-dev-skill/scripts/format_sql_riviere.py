#!/usr/bin/env python3
"""Format SQL statements according to the Riviere standard.

Riviere standard rules:
  1. Keywords uppercase
  2. Comma-first style in SELECT column lists
  3. Clause keywords (SELECT, FROM, WHERE, JOIN, etc.) on new lines
  4. Consistent 4-space indentation for continuation lines
  5. Semicolon at end of each statement
"""

import sys
import re
import argparse


# ---------------------------------------------------------------------------
# Token types
# ---------------------------------------------------------------------------
TOK_STRING   = "STRING"    # single-quoted string literal
TOK_COMMENT  = "COMMENT"   # -- line comment or /* block comment */
TOK_IDENT    = "IDENT"     # identifier or keyword
TOK_NUMBER   = "NUMBER"    # numeric literal
TOK_OP       = "OP"        # operator / punctuation
TOK_WS       = "WS"        # whitespace (normalised away)
TOK_SEMI     = "SEMI"      # statement terminator ;

# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------
_TOKEN_RE = re.compile(
    r"(--[^\n]*)"                          # line comment
    r"|(\/\*.*?\*\/)"                      # block comment (non-greedy)
    r"|('(?:''|[^'])*')"                   # single-quoted string
    r'|("(?:""|[^"])*")'                   # double-quoted identifier
    r"|(\b\d+(?:\.\d+)?\b)"               # number
    r"|([;\(\),])"                         # punctuation
    r"|([^\s;()',\"]+)"                    # identifier / keyword / operator
    r"|(\s+)",                             # whitespace
    re.DOTALL,
)

def tokenise(sql: str) -> list[tuple[str, str]]:
    """Return list of (type, value) tuples."""
    tokens = []
    for m in _TOKEN_RE.finditer(sql):
        line_cmt, blk_cmt, sq_str, dq_id, num, punct, word, ws = m.groups()
        if line_cmt is not None:
            tokens.append((TOK_COMMENT, line_cmt))
        elif blk_cmt is not None:
            tokens.append((TOK_COMMENT, blk_cmt))
        elif sq_str is not None:
            tokens.append((TOK_STRING, sq_str))
        elif dq_id is not None:
            tokens.append((TOK_IDENT, dq_id))          # preserve quoting
        elif num is not None:
            tokens.append((TOK_NUMBER, num))
        elif punct == ";":
            tokens.append((TOK_SEMI, punct))
        elif punct is not None:
            tokens.append((TOK_OP, punct))
        elif word is not None:
            tokens.append((TOK_IDENT, word))
        # whitespace silently dropped – we rebuild whitespace ourselves
    return tokens


# ---------------------------------------------------------------------------
# Keyword tables
# ---------------------------------------------------------------------------
SQL_KEYWORDS = {
    "SELECT", "DISTINCT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER",
    "OUTER", "FULL", "CROSS", "NATURAL", "ON", "USING", "AND", "OR", "NOT",
    "IN", "IS", "NULL", "BETWEEN", "LIKE", "ILIKE", "SIMILAR", "AS",
    "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET",
    "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE",
    "WITH", "RECURSIVE", "UNION", "EXCEPT", "INTERSECT", "ALL",
    "CASE", "WHEN", "THEN", "ELSE", "END",
    "RETURNING", "CONFLICT", "DO", "NOTHING", "EXCLUDED",
    "OVER", "PARTITION", "WINDOW", "ROWS", "RANGE", "GROUPS",
    "UNBOUNDED", "PRECEDING", "FOLLOWING", "CURRENT", "ROW",
    "LATERAL", "EXISTS", "SOME", "ANY",
    "CREATE", "TABLE", "INDEX", "DROP", "ALTER", "ADD", "COLUMN",
    "CONSTRAINT", "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "CASCADE",
    "RESTRICT", "DEFAULT", "UNIQUE", "CHECK", "TEMP", "TEMPORARY",
    "IF", "ONLY", "CONCURRENTLY", "STORED",
    "MERGE", "MATCHED", "INCLUDE",
    "ENABLE", "DISABLE", "FORCE",
    "SECURITY", "DEFINER", "INVOKER",
    "LANGUAGE", "VOLATILE", "STABLE", "IMMUTABLE", "FUNCTION",
    "PROCEDURE", "TRIGGER", "BEFORE", "AFTER", "INSTEAD", "OF",
    "EACH", "STATEMENT", "EXECUTE", "PROCEDURE", "BEGIN", "END",
    "ANALYZE", "ANALYSE", "EXPLAIN", "VERBOSE",
    "VACUUM", "REINDEX", "COPY", "FORMAT", "HEADER",
    "CAST", "EXTRACT", "EPOCH", "YEAR", "MONTH", "DAY",
    "HOUR", "MINUTE", "SECOND", "TIMEZONE",
    "INTERSECT", "EXCEPT",
    "TRUE", "FALSE",
    "ASC", "DESC", "NULLS", "FIRST", "LAST",
    "FILTER", "WITHIN", "GENERATED", "ALWAYS", "IDENTITY",
    "SEQUENCE", "OWNED", "BIGINT", "INTEGER", "INT", "TEXT", "BOOLEAN",
    "BOOL", "NUMERIC", "REAL", "FLOAT", "DOUBLE", "PRECISION", "DATE",
    "TIME", "TIMESTAMP", "TIMESTAMPTZ", "INTERVAL", "UUID", "JSONB",
    "JSON", "BYTEA", "CHAR", "VARCHAR", "SERIAL", "BIGSERIAL",
    "COALESCE", "GREATEST", "LEAST", "NULLIF",
    "ARRAY", "UNNEST",
    "POLICY", "LEVEL", "ISOLATION", "TRANSACTION", "COMMIT", "ROLLBACK",
    "SAVEPOINT", "RELEASE",
}

# Multi-word clause starters (in priority order, longest first)
_CLAUSE_PATTERNS = [
    "ON CONFLICT DO UPDATE",
    "ON CONFLICT DO NOTHING",
    "ON CONFLICT",
    "WHEN NOT MATCHED",
    "WHEN MATCHED",
    "ORDER BY",
    "GROUP BY",
    "PARTITION BY",
    "INSERT INTO",
    "DELETE FROM",
    "MERGE INTO",
    "LEFT OUTER JOIN",
    "RIGHT OUTER JOIN",
    "FULL OUTER JOIN",
    "LEFT JOIN",
    "RIGHT JOIN",
    "INNER JOIN",
    "CROSS JOIN",
    "NATURAL JOIN",
    "LATERAL JOIN",
    "JOIN",
    "UNION ALL",
    "UNION",
    "EXCEPT ALL",
    "EXCEPT",
    "INTERSECT ALL",
    "INTERSECT",
    "WITH RECURSIVE",
    "WITH",
    "SELECT",
    "DISTINCT",
    "FROM",
    "WHERE",
    "HAVING",
    "LIMIT",
    "OFFSET",
    "UPDATE",
    "SET",
    "VALUES",
    "RETURNING",
    "USING",
    "ON",
    "DO UPDATE",
    "DO NOTHING",
]

# Clauses that start a new top-level line (reset indent)
_NEWLINE_CLAUSES = {
    "SELECT", "FROM", "WHERE", "HAVING", "LIMIT", "OFFSET",
    "ORDER BY", "GROUP BY",
    "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "CROSS JOIN", "NATURAL JOIN",
    "FULL OUTER JOIN", "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "LATERAL JOIN",
    "JOIN",
    "INSERT INTO", "DELETE FROM", "UPDATE", "SET", "VALUES", "RETURNING",
    "ON CONFLICT", "ON CONFLICT DO UPDATE", "ON CONFLICT DO NOTHING",
    "WITH", "WITH RECURSIVE",
    "UNION", "UNION ALL", "EXCEPT", "EXCEPT ALL", "INTERSECT", "INTERSECT ALL",
    "MERGE INTO", "USING", "WHEN MATCHED", "WHEN NOT MATCHED",
    "ON",
}


# ---------------------------------------------------------------------------
# Reconstruct flat token stream to string pieces
# ---------------------------------------------------------------------------

def _upcase_keywords(tokens: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Return tokens with SQL keyword identifiers uppercased."""
    result = []
    for typ, val in tokens:
        if typ == TOK_IDENT and not val.startswith('"'):
            upper = val.upper()
            result.append((typ, upper if upper in SQL_KEYWORDS else val))
        else:
            result.append((typ, val))
    return result


def _tokens_to_flat(tokens: list[tuple[str, str]]) -> str:
    """Join tokens with single spaces (except no space before/after certain chars)."""
    parts = []
    prev_typ = None
    prev_val = None
    for typ, val in tokens:
        if not parts:
            parts.append(val)
        else:
            # No space before closing paren or comma or semicolon
            if val in (",", ")", ";"):
                parts.append(val)
            # No space after opening paren
            elif prev_val == "(":
                parts.append(val)
            # No space before ::cast
            elif val.startswith("::"):
                parts.append(val)
            # No space after ::
            elif prev_val and prev_val.startswith("::"):
                parts.append(val)
            else:
                parts.append(" " + val)
        prev_typ = typ
        prev_val = val
    return "".join(parts)


# ---------------------------------------------------------------------------
# Core formatter
# ---------------------------------------------------------------------------

def _split_select_columns(col_str: str) -> list[str]:
    """Split a comma-separated SELECT column list respecting parentheses."""
    columns = []
    depth = 0
    current = []
    for ch in col_str:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            columns.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        columns.append("".join(current).strip())
    return [c for c in columns if c]


def _clause_keyword_width(clause: str) -> int:
    """Length of right-aligned keyword prefix (e.g. 'SELECT' -> 6)."""
    return len(clause.split()[0])


def _format_statement(raw_sql: str) -> str:
    """Format a single SQL statement (no trailing semicolon expected)."""
    raw_sql = raw_sql.strip()
    if not raw_sql:
        return ""

    # --- tokenise and uppercase keywords ---
    tokens = tokenise(raw_sql)
    tokens = _upcase_keywords(tokens)

    # --- rebuild flat normalised SQL (preserve strings & comments) ---
    flat = _tokens_to_flat(tokens)

    # --- split into clause segments ---
    # We scan through the flat string and find clause boundaries.
    # Each segment: (clause_keyword, body_text)
    segments = _split_into_clauses(flat)

    if not segments:
        return raw_sql + ";"

    return _render_segments(segments) + ";"


def _split_into_clauses(sql: str) -> list[tuple[str, str]]:
    """Split flat SQL into (clause_name, clause_body) pairs."""
    # We'll do a token-aware scan to find clause keywords at depth 0
    tokens = tokenise(sql)
    tokens = _upcase_keywords(tokens)

    # Build a list of (position_in_token_list, clause_name)
    # Only match at paren depth 0
    depth = 0
    clause_starts = []  # (token_index, clause_name)
    i = 0
    n = len(tokens)

    while i < n:
        typ, val = tokens[i]
        if typ == TOK_OP and val == "(":
            depth += 1
            i += 1
            continue
        if typ == TOK_OP and val == ")":
            depth -= 1
            i += 1
            continue
        if typ in (TOK_STRING, TOK_COMMENT):
            i += 1
            continue

        if depth == 0 and typ == TOK_IDENT:
            # Try to match multi-word clause
            matched = _match_clause(tokens, i, n)
            if matched:
                clause_starts.append((i, matched))
                i += len(matched.split())
                continue
        i += 1

    if not clause_starts:
        # No recognisable clauses — return as-is
        return [("", sql)]

    # Build segments
    segments = []
    token_flat = [(t, v) for t, v in tokens]

    def toks_to_str(toks):
        return _tokens_to_flat(toks)

    for idx, (tok_i, clause_name) in enumerate(clause_starts):
        # Body starts after the clause keyword tokens
        body_start = tok_i + len(clause_name.split())
        if idx + 1 < len(clause_starts):
            body_end = clause_starts[idx + 1][0]
        else:
            body_end = n

        body_tokens = [tokens[k] for k in range(body_start, body_end)]
        body = toks_to_str(body_tokens).strip()

        # Prepend any text before first clause as a preamble
        if idx == 0 and tok_i > 0:
            pre_tokens = [tokens[k] for k in range(0, tok_i)]
            pre = toks_to_str(pre_tokens).strip()
            if pre:
                segments.append(("", pre))

        segments.append((clause_name, body))

    return segments


def _match_clause(tokens, i, n):
    """Try to match a multi-word clause at position i. Return matched string or None."""
    for clause in _CLAUSE_PATTERNS:
        words = clause.split()
        if i + len(words) > n:
            continue
        match = True
        for j, w in enumerate(words):
            typ, val = tokens[i + j]
            if typ != TOK_IDENT or val.upper() != w:
                match = False
                break
        if match:
            return clause
    return None


def _render_segments(segments: list[tuple[str, str]]) -> str:
    """Render clause segments into formatted SQL."""
    lines = []

    for clause, body in segments:
        if not clause:
            # Preamble (e.g. CTE "WITH x AS (...)")
            if body:
                lines.append(body)
            continue

        if clause in _NEWLINE_CLAUSES or clause not in {"AND", "OR"}:
            # Right-align the keyword in a fixed-width prefix area
            # Riviere style: keyword is right-aligned to column 6 (or clause length)
            kw_width = max(6, len(clause))
            padding = " " * (kw_width - len(clause))

            if clause == "SELECT":
                # Comma-first column list
                col_part = _format_select_columns(body, kw_width)
                lines.append(f"{padding}{clause}{col_part}")
            elif clause in ("WHERE", "HAVING", "ON"):
                # AND/OR conditions on separate lines, right-aligned
                cond_part = _format_conditions(body, kw_width)
                lines.append(f"{padding}{clause}{cond_part}")
            elif clause in ("ORDER BY", "GROUP BY", "PARTITION BY"):
                # Comma-separated list, each on new line
                col_part = _format_list_cols(body, kw_width)
                lines.append(f"{padding}{clause}{col_part}")
            elif clause == "SET":
                # assignment list, comma-first
                assign_part = _format_set_assignments(body, kw_width)
                lines.append(f"{padding}{clause}{assign_part}")
            elif clause == "VALUES":
                # Keep VALUES inline
                lines.append(f"{padding}{clause} {body}" if body else f"{padding}{clause}")
            else:
                lines.append(f"{padding}{clause} {body}".rstrip() if body else f"{padding}{clause}")
        else:
            lines.append(f"   {clause} {body}")

    return "\n".join(lines)


def _format_select_columns(body: str, kw_width: int) -> str:
    """Format SELECT column list comma-first."""
    body = body.strip()
    if not body:
        return ""

    columns = _split_select_columns(body)
    if len(columns) == 1:
        return f" {columns[0]}"

    indent = " " * kw_width
    # First column: space after SELECT
    result = f" {columns[0]}"
    for col in columns[1:]:
        result += f"\n{indent} , {col}"
    return result


def _format_conditions(body: str, kw_width: int) -> str:
    """Format WHERE/HAVING/ON conditions splitting on top-level AND/OR."""
    body = body.strip()
    if not body:
        return ""

    # Split on top-level AND / OR
    parts = _split_on_boolean(body)
    if len(parts) == 1:
        return f" {parts[0][1]}" if parts[0][0] is None else f" {parts[0][0]} {parts[0][1]}"

    indent = " " * kw_width
    lines_out = []
    for op, expr in parts:
        if op is None:
            lines_out.append(f" {expr}")
        else:
            lines_out.append(f"\n{indent}   {op} {expr}")

    return "".join(lines_out)


def _split_on_boolean(expr: str) -> list[tuple]:
    """Split expression on top-level AND/OR. Returns list of (op_or_None, expr)."""
    tokens = tokenise(expr)
    tokens = _upcase_keywords(tokens)
    depth = 0
    parts = []
    current = []
    current_op = None

    for typ, val in tokens:
        if typ == TOK_OP and val == "(":
            depth += 1
            current.append((typ, val))
        elif typ == TOK_OP and val == ")":
            depth -= 1
            current.append((typ, val))
        elif depth == 0 and typ == TOK_IDENT and val in ("AND", "OR"):
            parts.append((current_op, _tokens_to_flat(current).strip()))
            current = []
            current_op = val
        else:
            current.append((typ, val))

    if current:
        parts.append((current_op, _tokens_to_flat(current).strip()))

    return parts


def _format_list_cols(body: str, kw_width: int) -> str:
    """Format comma-separated list (ORDER BY, GROUP BY) comma-first."""
    body = body.strip()
    if not body:
        return ""

    columns = _split_select_columns(body)
    if len(columns) == 1:
        return f" {columns[0]}"

    indent = " " * kw_width
    result = f" {columns[0]}"
    for col in columns[1:]:
        result += f"\n{indent}        , {col}"
    return result


def _format_set_assignments(body: str, kw_width: int) -> str:
    """Format SET assignment list comma-first."""
    body = body.strip()
    if not body:
        return ""

    assignments = _split_select_columns(body)
    if len(assignments) == 1:
        return f" {assignments[0]}"

    indent = " " * kw_width
    result = f" {assignments[0]}"
    for a in assignments[1:]:
        result += f"\n{indent}   , {a}"
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def format_sql(sql: str) -> str:
    """Format one or more SQL statements according to Riviere standard."""
    # Split on semicolons while preserving string literals
    statements = _split_statements(sql)
    formatted = []
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            formatted.append(_format_statement(stmt))
    return "\n\n".join(formatted)


def _split_statements(sql: str) -> list[str]:
    """Split SQL text into individual statements on top-level semicolons."""
    tokens = tokenise(sql)
    statements = []
    current = []
    depth = 0

    for typ, val in tokens:
        if typ == TOK_OP and val == "(":
            depth += 1
            current.append((typ, val))
        elif typ == TOK_OP and val == ")":
            depth -= 1
            current.append((typ, val))
        elif typ == TOK_SEMI and depth == 0:
            statements.append(_tokens_to_flat(current))
            current = []
        else:
            current.append((typ, val))

    if current:
        remaining = _tokens_to_flat(current).strip()
        if remaining:
            statements.append(remaining)

    return statements


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Format SQL according to the Riviere standard (comma-first, uppercase keywords)."
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="Input SQL file (default: stdin)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: exit with code 1 if formatting differs (useful in CI)",
    )
    # Legacy positional / flag kept for backward compatibility
    parser.add_argument(
        "sql_positional",
        nargs="?",
        metavar="SQL",
        help="SQL string to format (positional, use --input for files)",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        dest="legacy_file",
        help="Read SQL from file (legacy flag, prefer --input)",
    )

    args = parser.parse_args()

    # --- read input ---
    if args.legacy_file:
        with open(args.legacy_file, "r", encoding="utf-8") as fh:
            original = fh.read()
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as fh:
            original = fh.read()
    elif args.sql_positional:
        original = args.sql_positional
    else:
        original = sys.stdin.read()

    formatted = format_sql(original)

    if args.check:
        if formatted.rstrip() != original.rstrip():
            print("SQL formatting differs from Riviere standard.", file=sys.stderr)
            sys.exit(1)
        print("SQL is correctly formatted.")
        sys.exit(0)

    # --- write output ---
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(formatted + "\n")
    else:
        print(formatted)


if __name__ == "__main__":
    main()
