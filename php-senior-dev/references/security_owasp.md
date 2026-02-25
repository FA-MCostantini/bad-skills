# Security Patterns & OWASP Top 10 Mitigation (Enterprise)

## SQL Injection Prevention

### Always Use Prepared Statements
```php
// NEVER — string concatenation
$sql = "SELECT * FROM users WHERE email = '{$_POST['email']}'"; // VULNERABLE!

// ALWAYS — named parameters
$stmt = $pdo->prepare('SELECT * FROM users WHERE email = :email');
$stmt->execute(['email' => $email]);
```

### Parameter Binding with Explicit Types
```php
$stmt = $pdo->prepare(
    'SELECT * FROM orders WHERE user_id = :user_id AND status = :status'
);
$stmt->bindValue(':user_id', $userId, PDO::PARAM_INT);
$stmt->bindValue(':status', $status->value, PDO::PARAM_STR);
$stmt->execute();
```

### Dynamic WHERE Clauses (Safe Pattern)
```php
// When filters are optional, build query safely:
$conditions = ['1=1'];
$params = [];

if ($email !== null) {
    $conditions[] = 'email = :email';
    $params['email'] = $email;
}
if ($status !== null) {
    $conditions[] = 'status = :status';
    $params['status'] = $status->value;
}

$sql = 'SELECT * FROM users WHERE ' . implode(' AND ', $conditions);
$stmt = $pdo->prepare($sql);
$stmt->execute($params);
```

---

## XSS Prevention

### Context-Aware Output Escaping
```php
// HTML context
echo htmlspecialchars($userInput, ENT_QUOTES | ENT_HTML5, 'UTF-8');

// JavaScript context — json_encode with flags
echo '<script>const data = ' . json_encode($userInput, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_THROW_ON_ERROR) . ';</script>';

// URL context
echo '<a href="?param=' . urlencode($userInput) . '">Link</a>';

// CSS context — whitelist only
$safeColor = preg_match('/^#[0-9a-fA-F]{6}$/', $color) ? $color : '#000000';
```

---

## CSRF Protection

### Token Generation and Validation
```php
declare(strict_types=1);

final class CsrfTokenManager
{
    private const TOKEN_LENGTH = 32;

    public function generateToken(): string
    {
        $token = bin2hex(random_bytes(self::TOKEN_LENGTH));
        $_SESSION['csrf_token'] = $token;
        $_SESSION['csrf_token_time'] = time();
        return $token;
    }

    public function validateToken(string $token, int $maxAgeSeconds = 3600): bool
    {
        if (!isset($_SESSION['csrf_token'], $_SESSION['csrf_token_time'])) {
            return false;
        }

        // Check expiration
        if (time() - $_SESSION['csrf_token_time'] > $maxAgeSeconds) {
            unset($_SESSION['csrf_token'], $_SESSION['csrf_token_time']);
            return false;
        }

        $valid = hash_equals($_SESSION['csrf_token'], $token);

        // Single-use: invalidate after validation
        unset($_SESSION['csrf_token'], $_SESSION['csrf_token_time']);

        return $valid;
    }
}
```

---

## Authentication & Session Security

### Secure Password Hashing
```php
// Hashing with Argon2id
$hashedPassword = password_hash($password, PASSWORD_ARGON2ID, [
    'memory_cost' => 65536,
    'time_cost' => 4,
    'threads' => 3,
]);

// Verification with auto-rehash
if (password_verify($password, $hashedPassword)) {
    if (password_needs_rehash($hashedPassword, PASSWORD_ARGON2ID)) {
        $newHash = password_hash($password, PASSWORD_ARGON2ID);
        // Update stored hash in database
    }
    // Regenerate session after login
    session_regenerate_id(true);
}
```

### Session Configuration (Hardened)
```php
// Set BEFORE session_start()
ini_set('session.cookie_httponly', '1');
ini_set('session.cookie_secure', '1');
ini_set('session.cookie_samesite', 'Strict');
ini_set('session.use_strict_mode', '1');
ini_set('session.use_only_cookies', '1');
ini_set('session.gc_maxlifetime', '1800'); // 30 min
ini_set('session.cookie_lifetime', '0');    // Browser session only

session_start();

// After login: regenerate to prevent fixation
session_regenerate_id(true);
```

---

## Input Validation

### Type-Safe Validation with Domain Constraints
```php
declare(strict_types=1);

final class InputValidator
{
    public static function email(mixed $input): string
    {
        if (!is_string($input)) {
            throw new ValidationException('Email must be a string');
        }

        $email = filter_var(trim($input), FILTER_VALIDATE_EMAIL);
        if ($email === false) {
            throw new ValidationException('Invalid email format');
        }

        // Domain-specific: max length check
        if (strlen($email) > 254) {
            throw new ValidationException('Email too long');
        }

        return strtolower($email);
    }

    public static function positiveInt(mixed $input, string $fieldName = 'value'): int
    {
        $value = filter_var($input, FILTER_VALIDATE_INT, [
            'options' => ['min_range' => 1],
        ]);

        if ($value === false) {
            throw new ValidationException("{$fieldName} must be a positive integer");
        }

        return $value;
    }

    public static function boundedString(
        mixed $input,
        int $minLength,
        int $maxLength,
        string $fieldName = 'value'
    ): string {
        if (!is_string($input)) {
            throw new ValidationException("{$fieldName} must be a string");
        }

        $trimmed = trim($input);
        $length = mb_strlen($trimmed, 'UTF-8');

        if ($length < $minLength || $length > $maxLength) {
            throw new ValidationException(
                "{$fieldName} must be between {$minLength} and {$maxLength} characters"
            );
        }

        return $trimmed;
    }

    public static function enum(mixed $input, string $enumClass): \BackedEnum
    {
        if (!is_string($input) && !is_int($input)) {
            throw new ValidationException("Invalid value for {$enumClass}");
        }

        $case = $enumClass::tryFrom($input);
        if ($case === null) {
            $valid = implode(', ', array_map(
                fn(\BackedEnum $c) => $c->value,
                $enumClass::cases()
            ));
            throw new ValidationException(
                "Invalid value '{$input}'. Valid: {$valid}"
            );
        }

        return $case;
    }
}
```

---

## File Upload Security

### Secure File Upload Handler
```php
declare(strict_types=1);

final class SecureFileUploader
{
    /** @var array<string, list<string>> Extension => allowed MIME types */
    private const ALLOWED_TYPES = [
        'csv'  => ['text/csv', 'text/plain', 'application/csv'],
        'xlsx' => ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
        'pdf'  => ['application/pdf'],
        'jpg'  => ['image/jpeg'],
        'png'  => ['image/png'],
    ];

    private const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

    public function __construct(
        private readonly string $uploadDirectory,
        private readonly LoggerInterface $logger
    ) {
        if (!is_dir($this->uploadDirectory)) {
            throw new \RuntimeException("Upload directory does not exist: {$this->uploadDirectory}");
        }
    }

    public function handle(array $file): UploadResult
    {
        // 1. Check upload error
        if ($file['error'] !== UPLOAD_ERR_OK) {
            throw new UploadException("Upload error code: {$file['error']}");
        }

        // 2. Check size
        if ($file['size'] > self::MAX_FILE_SIZE) {
            throw new UploadException('File exceeds maximum allowed size');
        }

        // 3. Validate extension
        $extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        if (!isset(self::ALLOWED_TYPES[$extension])) {
            throw new UploadException("Extension not allowed: {$extension}");
        }

        // 4. Validate MIME type (server-side, not from client)
        $finfo = new \finfo(FILEINFO_MIME_TYPE);
        $detectedMime = $finfo->file($file['tmp_name']);

        if (!in_array($detectedMime, self::ALLOWED_TYPES[$extension], true)) {
            $this->logger->warning('MIME type mismatch on upload', [
                'filename' => $file['name'],
                'extension' => $extension,
                'detected_mime' => $detectedMime,
            ]);
            throw new UploadException('File content does not match extension');
        }

        // 5. Generate safe filename (no user-controlled names in filesystem)
        $safeFilename = bin2hex(random_bytes(16)) . '.' . $extension;
        $destination = $this->uploadDirectory . DIRECTORY_SEPARATOR . $safeFilename;

        // 6. Move (outside web root)
        if (!move_uploaded_file($file['tmp_name'], $destination)) {
            throw new UploadException('Failed to save uploaded file');
        }

        $this->logger->info('File uploaded', [
            'original_name' => $file['name'],
            'safe_name' => $safeFilename,
            'size' => $file['size'],
            'mime' => $detectedMime,
        ]);

        return new UploadResult(
            filename: $safeFilename,
            originalName: $file['name'],
            size: $file['size'],
            mimeType: $detectedMime,
        );
    }
}
```

---

## Rate Limiting

### Token Bucket with Redis
```php
declare(strict_types=1);

final class RateLimiter
{
    public function __construct(
        private readonly \Redis $redis,
        private readonly LoggerInterface $logger,
        private readonly int $maxAttempts = 5,
        private readonly int $windowSeconds = 60
    ) {}

    /**
     * @return bool True if request is allowed
     */
    public function attempt(string $identifier, string $action = 'default'): bool
    {
        $key = "rate_limit:{$action}:{$identifier}";

        $pipe = $this->redis->multi(\Redis::PIPELINE);
        $pipe->incr($key);
        $pipe->expire($key, $this->windowSeconds);
        /** @var array{0: int, 1: bool} $results */
        $results = $pipe->exec();

        $attempts = $results[0];

        if ($attempts > $this->maxAttempts) {
            $this->logger->warning('Rate limit exceeded', [
                'identifier' => $identifier,
                'action' => $action,
                'attempts' => $attempts,
            ]);
            return false;
        }

        return true;
    }

    public function remainingAttempts(string $identifier, string $action = 'default'): int
    {
        $key = "rate_limit:{$action}:{$identifier}";
        $current = (int) $this->redis->get($key);
        return max(0, $this->maxAttempts - $current);
    }
}
```

---

## Encryption (Sodium)

### Data Encryption at Rest
```php
declare(strict_types=1);

final class DataEncryptor
{
    private readonly string $key;

    public function __construct(string $hexKey)
    {
        $this->key = sodium_hex2bin($hexKey);

        if (mb_strlen($this->key, '8bit') !== SODIUM_CRYPTO_SECRETBOX_KEYBYTES) {
            throw new \InvalidArgumentException('Invalid encryption key length');
        }
    }

    public function encrypt(string $plaintext): string
    {
        $nonce = random_bytes(SODIUM_CRYPTO_SECRETBOX_NONCEBYTES);
        $ciphertext = sodium_crypto_secretbox($plaintext, $nonce, $this->key);

        // Prepend nonce to ciphertext for storage
        return sodium_bin2base64(
            $nonce . $ciphertext,
            SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING
        );
    }

    public function decrypt(string $encoded): string
    {
        $decoded = sodium_base642bin($encoded, SODIUM_BASE64_VARIANT_URLSAFE_NO_PADDING);

        $nonce = mb_substr($decoded, 0, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, '8bit');
        $ciphertext = mb_substr($decoded, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES, null, '8bit');

        $plaintext = sodium_crypto_secretbox_open($ciphertext, $nonce, $this->key);

        if ($plaintext === false) {
            throw new DecryptionException('Decryption failed — data may be tampered');
        }

        // Clear sensitive data from memory
        sodium_memzero($decoded);

        return $plaintext;
    }

    public function __destruct()
    {
        sodium_memzero($this->key);
    }
}
```

---

## Security Headers

```php
// Apply on every response
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: strict-origin-when-cross-origin');
header('Permissions-Policy: geolocation=(), microphone=(), camera=()');
header("Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'");
header('Strict-Transport-Security: max-age=31536000; includeSubDomains');
// Note: X-XSS-Protection is deprecated in modern browsers, CSP replaces it
```

---

## Critical Security Checklist

1. **Never trust user input** — Always validate and sanitize server-side.
2. **Prepared statements only** — No string concatenation in SQL, ever.
3. **Context-aware output escaping** — HTML, JS, URL, CSS each need different escaping.
4. **CSRF tokens** — Single-use, time-limited, on all state-changing operations.
5. **HTTPS everywhere** — HSTS header with includeSubDomains.
6. **Hardened sessions** — HttpOnly, Secure, SameSite=Strict, regenerate on login.
7. **Argon2id for passwords** — With `password_needs_rehash()` on every login.
8. **File uploads validated** — MIME detection server-side, safe filenames, outside web root.
9. **Rate limiting** — On authentication, API endpoints, and sensitive operations.
10. **Dependencies updated** — Regular security patches, `composer audit` in CI.
11. **Audit logging** — WHO did WHAT, WHEN, on WHICH record, in financial systems.
12. **Secrets management** — Never hardcode keys/passwords. Use env vars or vault.
