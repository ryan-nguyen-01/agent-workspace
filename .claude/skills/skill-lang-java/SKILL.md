---
name: skill-lang-java
description: Best practices viết Java hiện đại (Java 17+): records, sealed classes, pattern matching, streams, optional và clean code principles.
---

# Skill: Java (17+)

## Modern Java Features

### Records cho immutable data
```java
// ✅ Record thay vì POJO với getter/setter
public record UserDto(
    String id,
    String email,
    String name
) {}

// ✅ Với validation trong compact constructor
public record CreateUserRequest(String email, String name) {
    public CreateUserRequest {
        if (email == null || !email.contains("@"))
            throw new IllegalArgumentException("Invalid email");
        if (name == null || name.isBlank())
            throw new IllegalArgumentException("Name required");
    }
}
```

### Sealed classes cho type hierarchies
```java
// ✅ Sealed + pattern matching
public sealed interface Result<T> permits Result.Success, Result.Failure {
    record Success<T>(T value) implements Result<T> {}
    record Failure<T>(String error, int code) implements Result<T> {}
}

// Usage với pattern matching
String message = switch (result) {
    case Result.Success<User> s -> "Found: " + s.value().name();
    case Result.Failure<User> f -> "Error: " + f.error();
};
```

### Text Blocks
```java
// ✅ Multi-line strings
String query = """
    SELECT u.id, u.email, p.name
    FROM users u
    JOIN profiles p ON u.id = p.user_id
    WHERE u.active = true
    """;
```

## Optional — Dùng đúng cách

```java
// ❌ Sai — Optional như null check
Optional<User> opt = findUser(id);
if (opt.isPresent()) {
    return opt.get();
}

// ✅ Đúng — functional style
return userRepository.findById(id)
    .map(UserMapper::toDto)
    .orElseThrow(() -> new NotFoundException("User", id));

// ❌ Sai — Optional làm field
class User {
    private Optional<String> middleName; // Không làm thế này
}

// ✅ Đúng — Optional chỉ cho return type
public Optional<String> findMiddleName() {
    return Optional.ofNullable(middleName);
}
```

## Streams & Collections

```java
// ✅ Stream pipeline rõ ràng
List<UserDto> activeUsers = users.stream()
    .filter(User::isActive)
    .sorted(Comparator.comparing(User::getCreatedAt).reversed())
    .limit(10)
    .map(userMapper::toDto)
    .toList(); // Java 16+ — immutable list

// ✅ Collectors
Map<Status, List<User>> byStatus = users.stream()
    .collect(Collectors.groupingBy(User::getStatus));

// ✅ Parallel stream chỉ khi có lý do rõ ràng (large dataset, CPU-bound)
long count = largeList.parallelStream()
    .filter(expensivePredicate)
    .count();
```

## Exception Handling

```java
// ✅ Custom exceptions có context
public class ResourceNotFoundException extends RuntimeException {
    private final String resourceType;
    private final Object resourceId;

    public ResourceNotFoundException(String resourceType, Object id) {
        super(String.format("%s not found with id: %s", resourceType, id));
        this.resourceType = resourceType;
        this.resourceId = id;
    }
}

// ✅ Exception chaining — giữ root cause
try {
    return objectMapper.readValue(json, UserDto.class);
} catch (JsonProcessingException e) {
    throw new DataProcessingException("Failed to parse user data", e);
}
```

## Naming Conventions

```
Classes:        PascalCase     UserService, OrderRepository
Interfaces:     PascalCase     UserRepository (không prefix I)
Methods:        camelCase      findUserById, createOrder
Variables:      camelCase      userId, orderList
Constants:      UPPER_SNAKE    MAX_RETRY_COUNT, DEFAULT_TIMEOUT
Packages:       lowercase      com.company.module.submodule
Test classes:   <Name>Test     UserServiceTest
```

## Immutability

```java
// ✅ Final fields
public class UserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository repo, PasswordEncoder encoder) {
        this.userRepository = repo;
        this.passwordEncoder = encoder;
    }
}

// ✅ Unmodifiable collections
private final List<String> ALLOWED_ROLES =
    List.of("ADMIN", "USER", "MODERATOR");
```

## Null Safety

```java
// ✅ Annotations để document nullability
import org.springframework.lang.NonNull;
import org.springframework.lang.Nullable;

public @NonNull User findById(@NonNull String id) { ... }
public @Nullable User findByEmail(@NonNull String email) { ... }

// ✅ Objects.requireNonNull trong constructors
public UserService(@NonNull UserRepository repo) {
    this.userRepository = Objects.requireNonNull(repo, "repo must not be null");
}
```
