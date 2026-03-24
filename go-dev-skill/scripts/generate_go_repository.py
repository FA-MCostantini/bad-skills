#!/usr/bin/env python3
"""Generate a Go 1.22+ repository interface and PostgreSQL implementation using pgx/v5."""

import argparse
import re
import sys
import textwrap


# ---------------------------------------------------------------------------
# Name helpers
# ---------------------------------------------------------------------------

def snake_to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def pascal_to_camel(name: str) -> str:
    if not name:
        return name
    return name[0].lower() + name[1:]


def pascal_to_snake(name: str) -> str:
    """Convert PascalCase / camelCase to snake_case.

    Examples:
        User       → user
        OrderItem  → order_item
        HTTPClient → http_client
    """
    # Insert underscore before uppercase letters that follow a lowercase letter
    # or before a sequence of uppercase letters followed by a lowercase letter.
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s2 = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def to_table_name(pascal: str) -> str:
    """Return the plural snake_case table name for a PascalCase entity name."""
    snake = pascal_to_snake(pascal)
    # Naive pluralisation: append 's' (covers most common cases).
    if snake.endswith("s"):
        return snake + "es"
    if snake.endswith("y") and not snake.endswith("ey"):
        return snake[:-1] + "ies"
    return snake + "s"


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------

def parse_fields(raw: str) -> list[tuple[str, str]]:
    """Parse 'id:int64,name:string,email:string,created_at:time.Time' into
    a list of (go_field_name, go_type) tuples with PascalCase field names."""
    fields: list[tuple[str, str]] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            field_raw, go_type = item.split(":", 1)
        else:
            field_raw, go_type = item, "string"
        fields.append((snake_to_pascal(field_raw.strip()), go_type.strip()))
    return fields


def required_imports(fields: list[tuple[str, str]]) -> list[str]:
    """Return stdlib imports required by the field types."""
    imports: list[str] = ["context", "errors", "fmt"]
    types = {t for _, t in fields}
    if any("time." in t for t in types):
        imports.append("time")
    return imports


def field_scan_vars(fields: list[tuple[str, str]]) -> str:
    """Return '&e.ID, &e.Name, ...' for row.Scan(...)."""
    return ", ".join(f"&e.{name}" for name, _ in fields)


def select_columns(fields: list[tuple[str, str]]) -> str:
    """Return SQL column list derived from field names (snake_case)."""
    return ", ".join(pascal_to_snake(name) for name, _ in fields)


def insert_columns_and_placeholders(fields: list[tuple[str, str]]) -> tuple[str, str]:
    """Return (column_list, placeholder_list) for INSERT, skipping 'id'."""
    non_id = [(name, t) for name, t in fields if name.lower() != "id"]
    cols = ", ".join(pascal_to_snake(n) for n, _ in non_id)
    placeholders = ", ".join(f"${i+1}" for i in range(len(non_id)))
    return cols, placeholders


def insert_args(fields: list[tuple[str, str]]) -> str:
    non_id = [(name, t) for name, t in fields if name.lower() != "id"]
    return ", ".join(f"entity.{name}" for name, _ in non_id)


def update_set_clause(fields: list[tuple[str, str]]) -> str:
    """Return 'name = $1, email = $2, ...' for UPDATE, skipping 'id'."""
    non_id = [(name, t) for name, t in fields if name.lower() != "id"]
    parts = [f"{pascal_to_snake(name)} = ${i+1}" for i, (name, _) in enumerate(non_id)]
    return ", ".join(parts)


def update_args(fields: list[tuple[str, str]]) -> str:
    non_id = [(name, t) for name, t in fields if name.lower() != "id"]
    args = [f"entity.{name}" for name, _ in non_id]
    # id is the last positional arg in UPDATE … WHERE id = $N
    args.append("entity.ID")
    return ", ".join(args)


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def generate_repository(name: str, fields: list[tuple[str, str]]) -> str:
    pascal = snake_to_pascal(name)
    camel = pascal_to_camel(pascal)
    table = to_table_name(pascal)
    lower_name = pascal_to_snake(pascal)

    imports = required_imports(fields)
    stdlib_imports = sorted(i for i in imports if "." not in i or i == "time")

    # Struct fields block
    struct_field_lines = [f"\t{fname}\t{ftype}" for fname, ftype in fields]

    # SELECT columns and scan vars
    sel_cols = select_columns(fields)
    scan_vars = field_scan_vars(fields)

    # INSERT
    ins_cols, ins_placeholders = insert_columns_and_placeholders(fields)
    ins_args = insert_args(fields)
    non_id_count = len([n for n, _ in fields if n.lower() != "id"])

    # UPDATE
    upd_set = update_set_clause(fields)
    upd_args = update_args(fields)
    id_placeholder = f"${non_id_count + 1}"

    lines: list[str] = [
        "package repository",
        "",
        "import (",
        *[f'\t"{imp}"' for imp in stdlib_imports],
        "",
        '\t"github.com/jackc/pgx/v5"',
        '\t"github.com/jackc/pgx/v5/pgxpool"',
        ")",
        "",
        f'var ErrNotFound = errors.New("{lower_name}: not found")',
        "",
        f"// {pascal} is the domain entity.",
        f"type {pascal} struct {{",
        *struct_field_lines,
        "}",
        "",
        f"// {pascal}Repository defines persistence operations for {pascal}.",
        f"type {pascal}Repository interface {{",
        f"\tFind(ctx context.Context, id int64) (*{pascal}, error)",
        f"\tFindAll(ctx context.Context) ([]*{pascal}, error)",
        f"\tCreate(ctx context.Context, entity *{pascal}) error",
        f"\tUpdate(ctx context.Context, entity *{pascal}) error",
        f"\tDelete(ctx context.Context, id int64) error",
        "}",
        "",
        f"// postgres{pascal}Repository is the PostgreSQL implementation of {pascal}Repository.",
        f"type postgres{pascal}Repository struct {{",
        "\tpool *pgxpool.Pool",
        "}",
        "",
        f"// Compile-time interface check.",
        f"var _ {pascal}Repository = (*postgres{pascal}Repository)(nil)",
        "",
        f"// NewPostgres{pascal}Repository creates a new postgres{pascal}Repository.",
        f"func NewPostgres{pascal}Repository(pool *pgxpool.Pool) *postgres{pascal}Repository {{",
        f"\treturn &postgres{pascal}Repository{{pool: pool}}",
        "}",
        "",
    ]

    # Find
    find_stub = textwrap.dedent(f"""\
        func (r *postgres{pascal}Repository) Find(ctx context.Context, id int64) (*{pascal}, error) {{
        \trow := r.pool.QueryRow(ctx,
        \t\t"SELECT {sel_cols} FROM {table} WHERE id = $1", id)

        \tvar e {pascal}
        \terr := row.Scan({scan_vars})
        \tif errors.Is(err, pgx.ErrNoRows) {{
        \t\treturn nil, ErrNotFound
        \t}}
        \tif err != nil {{
        \t\treturn nil, fmt.Errorf("find {lower_name}: %w", err)
        \t}}
        \treturn &e, nil
        }}""")

    # FindAll
    find_all_stub = textwrap.dedent(f"""\
        func (r *postgres{pascal}Repository) FindAll(ctx context.Context) ([]*{pascal}, error) {{
        \trows, err := r.pool.Query(ctx, "SELECT {sel_cols} FROM {table}")
        \tif err != nil {{
        \t\treturn nil, fmt.Errorf("find all {lower_name}: %w", err)
        \t}}
        \tdefer rows.Close()

        \tvar results []*{pascal}
        \tfor rows.Next() {{
        \t\tvar e {pascal}
        \t\tif err := rows.Scan({scan_vars}); err != nil {{
        \t\t\treturn nil, fmt.Errorf("scan {lower_name}: %w", err)
        \t\t}}
        \t\tresults = append(results, &e)
        \t}}
        \tif err := rows.Err(); err != nil {{
        \t\treturn nil, fmt.Errorf("rows {lower_name}: %w", err)
        \t}}
        \treturn results, nil
        }}""")

    # Create
    create_stub = textwrap.dedent(f"""\
        func (r *postgres{pascal}Repository) Create(ctx context.Context, entity *{pascal}) error {{
        \t_, err := r.pool.Exec(ctx,
        \t\t"INSERT INTO {table} ({ins_cols}) VALUES ({ins_placeholders})",
        \t\t{ins_args})
        \tif err != nil {{
        \t\treturn fmt.Errorf("create {lower_name}: %w", err)
        \t}}
        \treturn nil
        }}""")

    # Update
    update_stub = textwrap.dedent(f"""\
        func (r *postgres{pascal}Repository) Update(ctx context.Context, entity *{pascal}) error {{
        \t_, err := r.pool.Exec(ctx,
        \t\t"UPDATE {table} SET {upd_set} WHERE id = {id_placeholder}",
        \t\t{upd_args})
        \tif err != nil {{
        \t\treturn fmt.Errorf("update {lower_name}: %w", err)
        \t}}
        \treturn nil
        }}""")

    # Delete
    delete_stub = textwrap.dedent(f"""\
        func (r *postgres{pascal}Repository) Delete(ctx context.Context, id int64) error {{
        \t_, err := r.pool.Exec(ctx, "DELETE FROM {table} WHERE id = $1", id)
        \tif err != nil {{
        \t\treturn fmt.Errorf("delete {lower_name}: %w", err)
        \t}}
        \treturn nil
        }}""")

    for stub in [find_stub, find_all_stub, create_stub, update_stub, delete_stub]:
        lines.append(stub)
        lines.append("")

    # Suppress unused variable warning for camel (not used in repo impl)
    _ = camel

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Go 1.22+ repository interface and pgx/v5 implementation."
    )
    parser.add_argument("name", help="Entity name (e.g. 'user' → User, 'order_item' → OrderItem)")
    parser.add_argument(
        "-f", "--fields",
        default="id:int64,created_at:time.Time",
        help=(
            "Comma-separated field definitions (e.g. 'id:int64,name:string,email:string,"
            "created_at:time.Time'). Defaults to 'id:int64,created_at:time.Time'."
        ),
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    args = parser.parse_args()

    fields = parse_fields(args.fields)
    code = generate_repository(args.name, fields)

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(code)


if __name__ == "__main__":
    main()
