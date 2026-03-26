#!/usr/bin/env python3
"""Validate SQL files for common anti-patterns and safety issues.

Checks:
  1. String concatenation near WHERE/VALUES  (possible SQL injection)
  2. DELETE without WHERE clause
  3. TRUNCATE  (always flagged as dangerous)
  4. UPDATE without WHERE clause
  5. SELECT *  (suggest explicit column list)
  6. Missing semicolons at statement end
  7. Question-mark placeholders  (use $1/$2 or :named instead)

Exit code 0 if no issues found, 1 if any warnings or errors are reported.
"""

import sys
import re
import argparse


# ---------------------------------------------------------------------------
# Issue dataclass
# ---------------------------------------------------------------------------

class Issue:
    """A single validation finding."""

    LEVELS = ("WARNING", "ERROR")

    def __init__(self, level: str, line: int, message: str) -> None:
        if level not in self.LEVELS:
            raise ValueError(f"Unknown level: {level!r}")
        self.level   = level
        self.line    = line
        self.message = message

    def __str__(self) -> str:
        return f"{self.level}:{self.line}: {self.message}"

    def __lt__(self, other: "Issue") -> bool:
        return (self.line, self.level) < (other.line, other.level)


# ---------------------------------------------------------------------------
# Helper: strip string literals and comments so we only inspect real SQL
# ---------------------------------------------------------------------------

_STR_LITERAL_RE = re.compile(r"'(?:''|[^'])*'", re.DOTALL)
_LINE_COMMENT_RE = re.compile(r"--[^\n]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def _strip_literals_and_comments(sql: str) -> str:
    """Replace string literals and comments with same-length whitespace."""
    def blank(m: re.Match) -> str:
        text = m.group(0)
        # Preserve newlines so line numbers remain accurate
        return re.sub(r"[^\n]", " ", text)

    sql = _BLOCK_COMMENT_RE.sub(blank, sql)
    sql = _LINE_COMMENT_RE.sub(blank, sql)
    sql = _STR_LITERAL_RE.sub(blank, sql)
    return sql


def _line_of_offset(sql: str, offset: int) -> int:
    """Return 1-based line number for a character offset in sql."""
    return sql.count("\n", 0, offset) + 1


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

# 1 – String concatenation near SQL keywords
_CONCAT_NEAR_SQL_RE = re.compile(
    r"(?:"
    r"\|\|[ \t]*\$\w+"          # || $var
    r"|"
    r"'[ \t]*\|\|[ \t]*'"       # ' || '
    r"|"
    r"\+[ \t]*['\"]"            # + '...'  (non-PG but flagged)
    r")",
    re.IGNORECASE,
)

def check_injection(sql_clean: str, sql_orig: str) -> list[Issue]:
    issues = []
    for m in _CONCAT_NEAR_SQL_RE.finditer(sql_clean):
        ln = _line_of_offset(sql_orig, m.start())
        issues.append(Issue(
            "ERROR", ln,
            "String concatenation near SQL context -- possible SQL injection; use parameterised queries",
        ))
    return issues


# 2 – DELETE without WHERE
_DELETE_NO_WHERE_RE = re.compile(
    r"\bDELETE\b\s+\bFROM\b\s+\S+\s*;",
    re.IGNORECASE,
)

def check_delete_no_where(sql_clean: str, sql_orig: str) -> list[Issue]:
    issues = []
    for m in _DELETE_NO_WHERE_RE.finditer(sql_clean):
        ln = _line_of_offset(sql_orig, m.start())
        issues.append(Issue(
            "WARNING", ln,
            "DELETE without WHERE clause detected -- this will delete ALL rows",
        ))
    return issues


# 3 – TRUNCATE (always dangerous)
_TRUNCATE_RE = re.compile(r"\bTRUNCATE\b", re.IGNORECASE)

def check_truncate(sql_clean: str, sql_orig: str) -> list[Issue]:
    issues = []
    for m in _TRUNCATE_RE.finditer(sql_clean):
        ln = _line_of_offset(sql_orig, m.start())
        issues.append(Issue(
            "WARNING", ln,
            "TRUNCATE detected -- irreversibly removes all rows; ensure this is intentional",
        ))
    return issues


# 4 – UPDATE without WHERE
# Match UPDATE <table> SET ... ; with no WHERE in between
_UPDATE_STMT_RE = re.compile(
    r"\bUPDATE\b(?P<body>[^;]+);",
    re.IGNORECASE | re.DOTALL,
)

def check_update_no_where(sql_clean: str, sql_orig: str) -> list[Issue]:
    issues = []
    for m in _UPDATE_STMT_RE.finditer(sql_clean):
        body = m.group("body")
        if not re.search(r"\bWHERE\b", body, re.IGNORECASE):
            ln = _line_of_offset(sql_orig, m.start())
            issues.append(Issue(
                "WARNING", ln,
                "UPDATE without WHERE clause detected -- this will update ALL rows",
            ))
    return issues


# 5 – SELECT *
_SELECT_STAR_RE = re.compile(r"\bSELECT\s+\*", re.IGNORECASE)

def check_select_star(sql_clean: str, sql_orig: str) -> list[Issue]:
    issues = []
    for m in _SELECT_STAR_RE.finditer(sql_clean):
        ln = _line_of_offset(sql_orig, m.start())
        issues.append(Issue(
            "WARNING", ln,
            "SELECT * found -- use an explicit column list for clarity and forward compatibility",
        ))
    return issues


# 6 – Missing semicolons
# Split on semicolons; any non-empty "statement" at the end without one is suspect.
def check_missing_semicolons(sql_clean: str, sql_orig: str) -> list[Issue]:
    issues = []
    # Remove the content of $$ dollar-quoted blocks so we don't false-positive inside functions
    # (simple heuristic: strip $$ ... $$ regions)
    clean = re.sub(r'\$\$.*?\$\$', lambda m: re.sub(r'[^\n]', ' ', m.group(0)),
                   sql_clean, flags=re.DOTALL)

    # Split on semicolons to find potential dangling statements
    parts = re.split(r';', clean)
    # Track cumulative offset
    offset = 0
    for part in parts[:-1]:
        offset += len(part) + 1  # +1 for the semicolon itself

    # The last part: if it contains non-whitespace SQL keywords it is missing a semicolon
    last = parts[-1].strip()
    if last and re.search(
        r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|GRANT|REVOKE)\b',
        last, re.IGNORECASE
    ):
        # Approximate line: count newlines before trailing fragment
        leading = clean[: clean.rfind(parts[-1].lstrip()[:10]) + 1] if parts[-1].strip() else clean
        ln = _line_of_offset(sql_orig, len(sql_orig) - len(sql_orig.rstrip()))
        # Use last line of the file as best approximation
        ln = sql_orig.count("\n") + 1
        issues.append(Issue(
            "WARNING", ln,
            "Statement at end of file may be missing a semicolon",
        ))
    return issues


# 7 – Question-mark placeholders
_QMARK_RE = re.compile(r'\?')

def check_qmark_placeholders(sql_clean: str, sql_orig: str) -> list[Issue]:
    issues = []
    for m in _QMARK_RE.finditer(sql_clean):
        ln = _line_of_offset(sql_orig, m.start())
        issues.append(Issue(
            "WARNING", ln,
            "Question-mark placeholder '?' detected -- use $1/$2 positional or :named parameters for PostgreSQL",
        ))
    return issues


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

_ALL_CHECKS = {
    "check_injection":        check_injection,
    "check_delete_no_where":  check_delete_no_where,
    "check_truncate":         check_truncate,
    "check_update_no_where":  check_update_no_where,
    "check_select_star":      check_select_star,
    "check_missing_semis":    check_missing_semicolons,
    "check_qmark":            check_qmark_placeholders,
}


def run_checks(sql: str, enabled: set[str]) -> list[Issue]:
    """Run the enabled subset of checks and return all issues, sorted by line."""
    sql_clean = _strip_literals_and_comments(sql)
    issues    = []
    for key, fn in _ALL_CHECKS.items():
        if key in enabled:
            issues.extend(fn(sql_clean, sql))
    return sorted(issues)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate SQL for common anti-patterns and safety issues."
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="Input SQL file (default: stdin)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable ALL checks",
    )
    parser.add_argument(
        "--check-injection",
        action="store_true",
        dest="check_injection",
        help="Check for string concatenation that may indicate SQL injection",
    )
    parser.add_argument(
        "--check-delete",
        action="store_true",
        dest="check_delete",
        help="Check for DELETE / TRUNCATE statements without WHERE",
    )
    parser.add_argument(
        "--check-select-star",
        action="store_true",
        dest="check_select_star",
        help="Check for SELECT *",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write report to FILE instead of stdout",
    )

    args = parser.parse_args()

    # --- read input ---
    if args.input:
        with open(args.input, "r", encoding="utf-8") as fh:
            sql = fh.read()
    else:
        sql = sys.stdin.read()

    # --- determine enabled checks ---
    if args.strict:
        enabled = set(_ALL_CHECKS.keys())
    else:
        enabled = {
            # Always-on baseline checks
            "check_delete_no_where",
            "check_truncate",
            "check_update_no_where",
            "check_missing_semis",
            "check_qmark",
        }
        if args.check_injection:
            enabled.add("check_injection")
        if args.check_delete:
            enabled.update({"check_delete_no_where", "check_truncate"})
        if args.check_select_star:
            enabled.add("check_select_star")

    issues = run_checks(sql, enabled)

    # --- build report ---
    if issues:
        report = "\n".join(str(i) for i in issues) + "\n"
    else:
        report = "OK: no issues found.\n"

    # --- write output ---
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"Written: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(report)

    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
