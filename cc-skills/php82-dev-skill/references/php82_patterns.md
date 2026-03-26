# PHP 8.2 Design Patterns & Best Practices

## Modern PHP Features

### Constructor Property Promotion
```php
declare(strict_types=1);

final readonly class User
{
    public function __construct(
        private int $id,
        private string $email,
        private ?DateTimeImmutable $verifiedAt = null
    ) {
    }
}
```

### Enums for Type Safety
```php
enum Status: string
{
    case PENDING = 'pending';
    case ACTIVE = 'active';
    case SUSPENDED = 'suspended';
    
    public function isActive(): bool
    {
        return $this === self::ACTIVE;
    }
}
```

### Match Expression
```php
$result = match ($status) {
    Status::PENDING => $this->handlePending(),
    Status::ACTIVE => $this->processActive(),
    Status::SUSPENDED => throw new SuspendedException(),
};
```

## SOLID Patterns

### Dependency Injection with Interfaces
```php
interface CacheInterface
{
    public function get(string $key): mixed;
    public function set(string $key, mixed $value, int $ttl): void;
}

final class UserService
{
    public function __construct(
        private readonly UserRepositoryInterface $repository,
        private readonly CacheInterface $cache
    ) {
    }
}
```

### Value Objects
```php
final readonly class Money
{
    private function __construct(
        private int $amount,
        private string $currency
    ) {
        if ($amount < 0) {
            throw new InvalidArgumentException('Amount cannot be negative');
        }
    }
    
    public static function fromCents(int $cents, string $currency): self
    {
        return new self($cents, $currency);
    }
    
    public function add(Money $other): self
    {
        if ($this->currency !== $other->currency) {
            throw new CurrencyMismatchException();
        }
        
        return new self($this->amount + $other->amount, $this->currency);
    }
}
```

## Database Patterns

### Unit of Work with Transaction
```php
final class UnitOfWork
{
    private array $entities = [];
    private array $removed = [];
    
    public function __construct(
        private readonly PDO $connection
    ) {
    }
    
    public function persist(object $entity): void
    {
        $this->entities[spl_object_id($entity)] = $entity;
    }
    
    public function remove(object $entity): void
    {
        $this->removed[spl_object_id($entity)] = $entity;
    }
    
    public function commit(): void
    {
        $this->connection->beginTransaction();
        
        try {
            // Process entities
            foreach ($this->entities as $entity) {
                // Save logic
            }
            
            foreach ($this->removed as $entity) {
                // Delete logic
            }
            
            $this->connection->commit();
            $this->clear();
        } catch (Throwable $e) {
            $this->connection->rollBack();
            throw $e;
        }
    }
    
    private function clear(): void
    {
        $this->entities = [];
        $this->removed = [];
    }
}
```

### Query Builder Pattern
```php
final class QueryBuilder
{
    private ?array $select = null;
    private ?string $from = null;
    private ?array $where = null;
    private ?array $params = null;
    
    public function select(string ...$columns): self
    {
        $this->select = array_merge($this->select, $columns);
        return $this;
    }
    
    public function from(string $table): self
    {
        $this->from = $table;
        return $this;
    }
    
    public function where(string $condition, array $params): self
    {
        $this->where = $condition;
        $this->params = $params;
        return $this;
    }
    
    public function build(): array
    {
        $field = implode(', ', empty($this->select) ?: ['*']);
        $where = $this->where ?? 'true';
        $param = $this->params ?? [];
        $sql = <<<SQL
            SELECT $field FROM $this->from WHERE ($where)
        SQL;

        
        return ['sql' => $sql, 'params' => $param];
    }
}
```

## Error Handling

### Custom Exceptions
```php
final class DomainException extends Exception
{
    public static function invalidOperation(string $reason): self
    {
        return new self("Operation failed: $reason");
    }
}

// Usage
throw DomainException::invalidOperation('Insufficient funds');
```

### Result Pattern (No Exceptions)
```php
final readonly class Result
{
    private function __construct(
        private mixed $value,
        private ?Throwable $error
    ) {
    }
    
    public static function success(mixed $value): self
    {
        return new self($value, null);
    }
    
    public static function failure(Throwable $error): self
    {
        return new self(null, $error);
    }
    
    public function isSuccess(): bool
    {
        return $this->error === null;
    }
    
    public function getValue(): mixed
    {
        if (!$this->isSuccess()) {
            throw new LogicException('Cannot get value from failed result');
        }
        return $this->value;
    }
}
```

## Performance Optimizations

### Generator for Large Datasets
```php
function fetchLargeDataset(PDO $connection): Generator
{
    $stmt = $connection->prepare('SELECT * FROM large_table');
    $stmt->execute();
    
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        yield $row;
    }
}

// Memory efficient iteration
foreach (fetchLargeDataset($pdo) as $row) {
    // Process row
}
```

### Weak References for Caching
```php
final class EntityManager
{
    private WeakMap $entities;
    
    public function __construct()
    {
        $this->entities = new WeakMap();
    }
    
    public function getEntity(int $id): Entity
    {
        // Auto cleanup when entity is no longer referenced
        if (!isset($this->entities[$id])) {
            $this->entities[$id] = $this->loadEntity($id);
        }
        
        return $this->entities[$id];
    }
}
```

## Testing Patterns

### PHPUnit 10+ Testing Patterns
```php
use PHPUnit\Framework\Attributes\CoversClass;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\Attributes\Test;

#[CoversClass(Calculator::class)]
final class CalculatorTest extends TestCase
{
    #[Test]
    public function it_adds_two_numbers(): void
    {
        $calculator = new Calculator();
        self::assertSame(4, $calculator->add(2, 2));
    }

    #[Test]
    #[DataProvider('divisionProvider')]
    public function it_divides(int $a, int $b, float $expected): void
    {
        self::assertSame($expected, (new Calculator())->divide($a, $b));
    }

    public static function divisionProvider(): iterable
    {
        yield 'simple' => [10, 2, 5.0];
        yield 'with remainder' => [7, 2, 3.5];
    }
}
```

### Arrange-Act-Assert with Data Providers (legacy style — prefer attributes above)
```php
#[CoversClass(UserService::class)]
final class UserServiceTest extends TestCase
{
    #[Test]
    #[DataProvider('invalidEmailProvider')]
    public function testInvalidEmail(string $email): void
    {
        // Arrange
        $service = new UserService();

        // Act & Assert
        $this->expectException(InvalidEmailException::class);
        $service->createUser($email);
    }

    public static function invalidEmailProvider(): array
    {
        return [
            ['invalid'],
            ['@example.com'],
            ['user@'],
        ];
    }
}
```

---

## PHP 8.3 Features

### `#[Override]` Attribute
```php
// #[Override] attribute
class ConcreteService implements ServiceInterface
{
    #[\Override]
    public function process(string $input): Result
    {
        // ...
    }
}

// Typed class constants
class Config
{
    public const string VERSION = '1.0.0';
    public const int MAX_RETRIES = 3;
    // Note: const array<string, mixed> DEFAULTS = []; is NOT valid — use PHPDoc
    /** @var array<string, mixed> */
    public const array DEFAULTS = [];
}

// json_validate()
if (json_validate($input)) {
    $data = json_decode($input, true, 512, JSON_THROW_ON_ERROR);
}
```

---

## First-Class Callable Syntax

```php
// Instead of Closure::fromCallable('strlen')
$fn = strlen(...);
$lengths = array_map(strlen(...), $strings);

// Static methods
$validator = InputValidator::email(...);

// Instance methods
$processor = $this->processItem(...);
```

---

## Intersection and DNF Types

```php
function process(Countable&Stringable $value): void { }
function handle((Countable&Stringable)|null $value): void { }
```

---

## Fibers

```php
$fiber = new Fiber(function (): void {
    $value = Fiber::suspend('paused');
    echo "Resumed with: $value";
});
$result = $fiber->start(); // 'paused'
$fiber->resume('hello');   // Resumed with: hello
// Note: For production async, use ReactPHP or Amp v3 which use Fibers internally
```

---

## Advanced Match Expressions

```php
// No-argument match (replaces if/elseif)
$label = match(true) {
    $amount > 10000 => 'high',
    $amount > 1000  => 'medium',
    default         => 'low',
};

// Multiple conditions per arm
$category = match($status) {
    Status::Active, Status::Pending => 'open',
    Status::Closed, Status::Archived => 'closed',
};
```

---

## Expanded Enum Coverage

```php
// Pure enum (no backing type)
enum Permission
{
    case Read;
    case Write;
    case Execute;
}

// Enum implementing interface
enum Status: string implements HasLabel
{
    case Active = 'active';
    case Inactive = 'inactive';

    public function label(): string
    {
        return match($this) {
            self::Active => 'Attivo',
            self::Inactive => 'Inattivo',
        };
    }
}

// Enum with JsonSerializable
enum Priority: int implements \JsonSerializable
{
    case Low = 1;
    case Medium = 2;
    case High = 3;

    public function jsonSerialize(): int
    {
        return $this->value;
    }
}

// from() vs tryFrom()
$status = Status::from('active');      // throws ValueError if invalid
$status = Status::tryFrom('unknown');  // returns null if invalid
$allCases = Status::cases();           // array of all cases
```

---

## Named Arguments Best Practices

```php
// Good: clarifies ambiguous parameter order
$result = array_slice(array: $items, offset: 2, length: 5);

// Good: constructors with many same-type params
new Report(
    startDate: $from,
    endDate: $to,
    format: ReportFormat::PDF,
    includeHeaders: true,
);

// Warning: creates coupling to parameter names — avoid for 3rd-party library calls that may rename params
```

---

## CQRS Pattern

```php
// Command
final readonly class CreateOrderCommand
{
    public function __construct(
        public string $customerId,
        public array $items,
    ) {}
}

// Command Handler Interface
interface CommandHandlerInterface
{
    public function handle(object $command): void;
}

// Command Bus Interface
interface CommandBusInterface
{
    public function dispatch(object $command): void;
}

// Query
final readonly class GetOrderQuery
{
    public function __construct(
        public string $orderId,
    ) {}
}

// Query Handler returns data
interface QueryHandlerInterface
{
    public function handle(object $query): mixed;
}
```

---

## PSR-15 Middleware Pattern

```php
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;
use Psr\Http\Server\MiddlewareInterface;
use Psr\Http\Server\RequestHandlerInterface;

final readonly class AuthenticationMiddleware implements MiddlewareInterface
{
    public function __construct(
        private TokenValidatorInterface $tokenValidator,
        private LoggerInterface $logger,
    ) {}

    public function process(
        ServerRequestInterface $request,
        RequestHandlerInterface $handler,
    ): ResponseInterface {
        $token = $request->getHeaderLine('Authorization');

        if ($token === '') {
            return new JsonResponse(['error' => 'Unauthorized'], 401);
        }

        try {
            $user = $this->tokenValidator->validate($token);
            $request = $request->withAttribute('user', $user);
        } catch (InvalidTokenException $e) {
            $this->logger->warning('Invalid token attempt', ['error' => $e->getMessage()]);
            return new JsonResponse(['error' => 'Invalid token'], 401);
        }

        return $handler->handle($request);
    }
}
```
