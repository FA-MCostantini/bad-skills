---
name: php82-dev-skill
description: PHP 8.2+ development specialist for enterprise-grade applications. Use when writing, reviewing, or refactoring PHP code, creating PHP classes, implementing design patterns in PHP, handling PHP error management, or working with PSR standards. Covers strict_types enforcement, readonly classes, enums, match expressions, constructor property promotion, PHPDoc rules, PHPStan level 8/9 compliance, structured error handling with PSR-3 logging, audit trails for financial systems, and OWASP security patterns. Activates autonomously when PHP code context is detected.
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
metadata:
  author: Mattia Costantini
  version: "1.0.0"
  domain: language
  triggers: php class namespace pdo psr composer phpstan declare strict_types
  role: specialist
  scope: implementation
  output-format: code
  autonomy: true
  related-skills: project-dev-skill, ears-doc, postgresql16-dev-skill
---

# PHP 8.2 Development — Enterprise Edition

Specialist skill for writing production-grade PHP 8.2+ code.
Apply the **project-dev-skill** methodology (Critical Analysis, Decision Record, Implementation) before writing any PHP code.

---

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

## Security by Default

Every piece of generated PHP code MUST include these protections without being asked:

### Automatic Protections (always applied)

```php
// EVERY SQL query: prepared statements with named params
$stmt = $pdo->prepare('SELECT * FROM users WHERE email = :email AND status = :status');
$stmt->execute(['email' => $email, 'status' => $status->value]);

// EVERY user input: type-safe validation before use
$id = filter_var($input, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1]]);
if ($id === false) {
    throw new ValidationException('Invalid ID');
}

// EVERY output to HTML: context-aware escaping
echo htmlspecialchars($value, ENT_QUOTES | ENT_HTML5, 'UTF-8');
```

### Security Escalation

When the request involves ANY of these, load `references/security_owasp.md`:
- User authentication or session handling
- File uploads
- External API calls
- Data encryption
- Payment or financial operations
- Role-based access control

---

## Error Handling & Logging (Enterprise)

### Error Handling Rules

- `try/catch` on ALL I/O operations (database, file, network, external API).
- Catch specific exceptions, never bare `catch (\Throwable $e)` unless re-throwing.
- Domain exceptions for business logic errors (named, with context).
- Infrastructure exceptions for technical failures (database, file system).
- NEVER silently swallow errors. Log + rethrow or log + return Result.

### Structured Logging Pattern

Every service MUST support logging. Use PSR-3 LoggerInterface:

```php
declare(strict_types=1);

final class ImportService
{
    public function __construct(
        private readonly PDO $connection,
        private readonly LoggerInterface $logger
    ) {}

    public function importFile(string $filePath): ImportResult
    {
        $this->logger->info('Import started', [
            'file' => $filePath,
            'timestamp' => (new DateTimeImmutable())->format('c'),
        ]);

        try {
            $result = $this->processFile($filePath);

            $this->logger->info('Import completed', [
                'file' => $filePath,
                'rows_processed' => $result->processed,
                'rows_skipped' => $result->skipped,
                'duration_ms' => $result->durationMs,
            ]);

            return $result;
        } catch (FileNotFoundException $e) {
            $this->logger->error('Import file not found', [
                'file' => $filePath,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        } catch (DatabaseException $e) {
            $this->logger->critical('Import database failure', [
                'file' => $filePath,
                'error' => $e->getMessage(),
                'row_number' => $e->getRowNumber(),
            ]);
            throw $e;
        }
    }
}
```

### Audit Trail (Financial Systems)

For operations on financial data (imports, reconciliations, status changes):

```php
// Audit log entry — WHO did WHAT on WHICH record, WHEN, with WHAT result
$this->auditLogger->log(
    action: 'contract_premium_update',
    entityType: 'contract',
    entityId: $contractId,
    operator: $currentUser->getId(),
    previousValue: $oldPremium,
    newValue: $newPremium,
    context: ['source' => 'bper_daily_import', 'batch_id' => $batchId],
);
```

---

## PHPDoc: When and How

**ALWAYS required on:**
- Public methods of non-trivial classes (API surface)
- Interfaces (contract definition)
- Methods where type hints alone are insufficient (`array<string, Money>`, generics)
- `@throws` when callers need to know which exceptions to handle

**NEVER needed on:**
- Private methods with clear names and full type hints
- Getters/setters with no logic
- Constructors where promoted properties are self-explanatory

```php
// BAD — PHPDoc restates type hints (noise)
/**
 * @param int $id The user ID
 * @return User The user
 */
public function findById(int $id): User

// GOOD — PHPDoc adds value (complex types, business context, exceptions)
/**
 * @param array<string, mixed> $filters Column => value pairs for WHERE clause
 * @return Generator<int, ContractPremium> Yields results row by row for memory efficiency
 * @throws DatabaseConnectionException When connection pool is exhausted
 */
public function findByFilters(array $filters): Generator
```

---

## Static Analysis Compliance

All generated PHP code MUST pass:
- **PHPStan level 8** (minimum, mandatory)
- **PHPStan level 9** (max — recommended, use when feasible)

Concrete implications:
- No `@phpstan-ignore` unless absolutely necessary (and documented why)
- No `mixed` type unless genuinely dynamic — prefer union types
- All arrays must be typed: `array<string, int>`, `list<User>`, never bare `array`
- Return types on every method, no implicit `void`
- Null safety: use `?Type` explicitly, check before use
- No `@var` inline type overrides to silence the analyzer — fix the actual type instead

```php
// BAD — bare array, PHPStan cannot verify usage
public function getUsers(): array

// GOOD — PHPStan level 9 compatible
/** @return list<User> */
public function getActiveUsers(): array

// BAD — suppressing analyzer
/** @phpstan-ignore-next-line */
$value = $ambiguousResult;

// GOOD — explicit type narrowing
$value = $ambiguousResult;
assert($value instanceof ExpectedType);
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

## Auto-Loading Rules

| Condition | File to Load |
|-----------|-------------|
| PHP class design, patterns, enums, value objects | `references/php82_patterns.md` |
| Security concern, input handling, auth, upload | `references/security_owasp.md` |

When in doubt, load the reference. Better to have it and not need it.

---

## Available Scripts

**generate_php_class.py** — Create PHP 8.2 classes with constructor promotion
```bash
python3 scripts/generate_php_class.py UserDTO -n App\\DTO -p id:int email:string roles:array
```

**generate_repository.py** — Generate repository pattern implementation
```bash
python3 scripts/generate_repository.py User users -n App\\Repository
```

---

## Critical Reminders

- **NEVER** concatenate SQL strings — no exceptions.
- **NEVER** silently catch and discard exceptions.
- **ALWAYS** validate file uploads (MIME, extension, size).
- **ALWAYS** check `password_needs_rehash()` on login.
- **PREFER** `readonly` classes for DTOs and value objects.
- **PREFER** `WeakMap` for entity caching.
- **PREFER** composition over inheritance.
