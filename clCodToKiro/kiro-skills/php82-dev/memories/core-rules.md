# php82-dev — Core Rules

## Context

Use this memory when: php class namespace pdo psr composer phpstan declare strict_types

## Non-Negotiable Rules

```php
declare(strict_types=1); // MANDATORY — every single file, no exceptions
```

### Readonly Classes for Immutable Data

```php
final readonly class ContractPremium
{
    public function __construct(
        private int $contractId,
        private Money $amount,
        private DateTimeImmutable $effectiveDate,
        private Status $status
    ) {}
}
```

### Enums for Type Safety — Never String Constants

```php
enum ImportStatus: string
{
    case PENDING = 'pending';
    case PROCESSING = 'processing';
    case COMPLETED = 'completed';
    case FAILED = 'failed';

    public function isTerminal(): bool
    {
        return match($this) {
            self::COMPLETED, self::FAILED => true,
            default => false,
        };
    }
}
```

### Match Expressions Over Switch

```php
$handler = match($fileType) {
    'csv' => new CsvImporter($logger),
    'xlsx' => new ExcelImporter($logger),
    'xml' => new XmlImporter($logger),
    default => throw new UnsupportedFileTypeException($fileType),
};
```

---

## Quality Checklist (PHP-Specific)

- [ ] `declare(strict_types=1)` present
- [ ] Named SQL parameters (`:param`)
- [ ] Input validated before use
- [ ] Output escaped where displayed
- [ ] I/O operations wrapped in try/catch
- [ ] No hardcoded config values
- [ ] No silent error swallowing
- [ ] Type hints on ALL parameters and return types
- [ ] Typed arrays (`list<User>`, `array<string, int>`) — no bare `array`
- [ ] No `mixed` unless genuinely dynamic
- [ ] PHPStan level 8 compliant (level 9 preferred)
- [ ] No `@phpstan-ignore` without documented justification
- [ ] PHPDoc on public API surface, complex types, and @throws — not on trivial methods

---

## LSP Integration

Kiro's native LSP replaces many code generation scripts:

- **Symbol search**: `code search_symbols <name>` — Find classes, functions, methods
- **Symbol lookup**: `code lookup_symbols <names>` — Get detailed symbol info
- **Pattern search**: `code pattern_search <pattern>` — AST-based code search
- **Find references**: Use LSP find_references tool
- **Rename symbol**: Use LSP rename_symbol tool

## Related Memories

Load additional patterns when needed:
- `php82-dev/patterns/*` — Specific pattern libraries

## Critical Reminders

- Leverage LSP for code navigation and refactoring
- Load pattern memories on-demand, not upfront
- Use `code` tool for semantic understanding, `grep` for text search
