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

### Arrange-Act-Assert with Data Providers
```php
final class UserServiceTest extends TestCase
{
    /**
     * @dataProvider invalidEmailProvider
     */
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
