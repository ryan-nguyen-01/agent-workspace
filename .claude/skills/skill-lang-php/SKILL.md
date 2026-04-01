---
name: skill-lang-php
description: Best practices viết PHP 8.3+ hiện đại — types, enums, fibers, match, named arguments, attributes và clean patterns.
---

# Skill: PHP (8.3+)

## Type System

```php
<?php declare(strict_types=1);

// ✅ Typed properties
class User {
    public function __construct(
        public readonly string $id,
        public readonly string $email,
        public string $name,
        public readonly \DateTimeImmutable $createdAt = new \DateTimeImmutable(),
    ) {}
}

// ✅ Union types
function processId(int|string $id): string {
    return (string) $id;
}

// ✅ Intersection types (PHP 8.1+)
function process(Countable&Iterator $collection): void { }

// ✅ Never return type
function redirect(string $url): never {
    header("Location: $url");
    exit();
}

// ✅ Nullable
function find(string $id): ?User {
    return $this->repo->find($id);
}
```

---

## Enums (PHP 8.1+)

```php
// ✅ Backed enum
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';

    public function label(): string {
        return match($this) {
            Status::Active => 'Active',
            Status::Inactive => 'Inactive',
            Status::Pending => 'Pending review',
        };
    }
}

// Usage
$status = Status::from('active');  // throws on invalid
$status = Status::tryFrom('unknown');  // returns null

// ✅ Pure enum
enum Direction { case North, South, East, West; }
```

---

## Match Expression

```php
// ✅ match — strict, exhaustive, no fall-through
$label = match($user->role) {
    'admin' => 'Administrator',
    'editor' => 'Editor',
    'user', 'member' => 'Regular User',  // multiple values
    default => 'Unknown',
};

// ✅ No default needed when exhaustive (enum)
$message = match($status) {
    Status::Active => 'Account is active',
    Status::Inactive => 'Account is disabled',
    Status::Pending => 'Awaiting verification',
};
```

---

## Fibers (PHP 8.1+)

```php
// ✅ Fibers — cooperative multitasking
$fiber = new Fiber(function (): void {
    $value = Fiber::suspend('fiber started');
    echo "Resumed with: $value\n";
});

$result = $fiber->start();      // 'fiber started'
$fiber->resume('hello');        // resumes fiber
```

---

## Named Arguments & Spread

```php
// ✅ Named arguments — order-independent, skip optional
$arr = array_slice(array: $users, offset: 0, length: 10, preserve_keys: true);

htmlspecialchars(string: $input, flags: ENT_QUOTES, encoding: 'UTF-8');

// ✅ Spread operator
function sum(int ...$nums): int { return array_sum($nums); }
$result = sum(...[1, 2, 3]);

// Named + spread
$config = ['length' => 10, 'offset' => 0];
array_slice(array: $arr, ...$config);
```

---

## Attributes (PHP 8.0+)

```php
// ✅ Built-in attributes
#[Override]
public function toArray(): array { ... }

#[Deprecated('Use newMethod() instead')]
public function oldMethod(): void { }

// ✅ Custom attributes
#[Attribute(Attribute::TARGET_CLASS | Attribute::TARGET_METHOD)]
class Route {
    public function __construct(
        public string $path,
        public string $method = 'GET',
    ) {}
}

#[Route('/users', 'GET')]
class UserController { }

// Reading attributes via Reflection
$ref = new ReflectionClass(UserController::class);
$attrs = $ref->getAttributes(Route::class);
foreach ($attrs as $attr) {
    $route = $attr->newInstance();
    echo $route->path; // /users
}
```

---

## Error Handling

```php
// ✅ Custom exceptions
class NotFoundException extends \RuntimeException {
    public function __construct(string $resource, string $id) {
        parent::__construct("$resource '$id' not found");
    }
}

class ValidationException extends \RuntimeException {
    public function __construct(
        private readonly array $errors,
        string $message = 'Validation failed',
    ) {
        parent::__construct($message);
    }

    public function getErrors(): array { return $this->errors; }
}

// ✅ Try-catch specifics
try {
    $user = $this->repo->findOrFail($id);
} catch (NotFoundException $e) {
    throw new HttpException(404, $e->getMessage());
} catch (\PDOException $e) {
    throw new HttpException(500, 'Database error');
}
```

---

## Interfaces & Traits

```php
interface UserRepository {
    public function findById(string $id): ?User;
    public function save(User $user): User;
    public function delete(string $id): void;
}

// ✅ Traits for horizontal reuse
trait HasTimestamps {
    public readonly \DateTimeImmutable $createdAt;
    public \DateTimeImmutable $updatedAt;

    public function touch(): void {
        $this->updatedAt = new \DateTimeImmutable();
    }
}

class Post {
    use HasTimestamps;
}
```

---

## Collections (Laravel-style)

```php
// ✅ Array functions idiomatically
$activeEmails = array_map(
    fn(User $u) => $u->email,
    array_filter($users, fn(User $u) => $u->isActive())
);

// ✅ With Laravel Collection
$activeEmails = collect($users)
    ->filter(fn($u) => $u->isActive())
    ->map(fn($u) => $u->email)
    ->unique()
    ->values()
    ->all();
```

---

## Readonly & First-class Callable

```php
// ✅ Readonly classes (PHP 8.2)
readonly class CreateUserDto {
    public function __construct(
        public string $email,
        public string $name,
        public string $password,
    ) {}
}

// ✅ First-class callable syntax (PHP 8.1)
$strlen = strlen(...);   // Closure from built-in
$handler = [$this, 'handle'](...)  // From method

$lengths = array_map(strlen(...), $strings);
```

---

## Idioms checklist

- ✅ `declare(strict_types=1)` ở đầu file
- ✅ Typed properties + return types cho tất cả functions
- ✅ `match` thay `switch`
- ✅ `readonly` cho immutable properties
- ✅ Enums thay constants cho fixed sets
- ✅ Named arguments cho built-in functions nhiều params
- ✅ `\DateTimeImmutable` thay `\DateTime`
- ✅ Constructor promotion (PHP 8.0+)
