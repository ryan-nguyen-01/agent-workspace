---
name: skill-framework-spring-boot
description: Best practices xây dựng Spring Boot 3.x applications: layered architecture, dependency injection, JPA, security, validation và exception handling.
---

# Skill: Spring Boot (3.x)

## Layered Architecture

```
src/main/java/com/company/app/
├── controller/       # REST controllers — HTTP layer only
├── service/          # Business logic interfaces + implementations
├── repository/       # Spring Data JPA repositories
├── entity/           # JPA entities
├── dto/              # Request/Response DTOs
├── mapper/           # Entity ↔ DTO mapping (MapStruct)
├── exception/        # Custom exceptions + global handler
├── config/           # Spring configuration classes
└── security/         # Security config, JWT filter
```

## Controller — Thin

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Validated
public class UserController {
    private final UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> findById(
            @PathVariable @NotBlank String id) {
        return ResponseEntity.ok(userService.findById(id));
    }

    @PostMapping
    public ResponseEntity<UserResponse> create(
            @RequestBody @Valid CreateUserRequest request) {
        UserResponse response = userService.create(request);
        URI location = URI.create("/api/v1/users/" + response.id());
        return ResponseEntity.created(location).body(response);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable @NotBlank String id) {
        userService.delete(id);
    }
}
```

## DTO với Java Records

```java
// ✅ Request DTO với validation
public record CreateUserRequest(
    @NotBlank @Email String email,
    @NotBlank @Size(min = 2, max = 100) String name,
    @NotBlank @Size(min = 8) String password
) {}

// ✅ Response DTO — no sensitive fields
public record UserResponse(
    String id,
    String email,
    String name,
    LocalDateTime createdAt
) {}

// ✅ Pagination request
public record PageRequest(
    @PositiveOrZero int page,
    @Positive @Max(100) int size
) {
    public PageRequest() { this(0, 20); }
}
```

## Service Layer

```java
public interface UserService {
    UserResponse findById(String id);
    UserResponse create(CreateUserRequest request);
    void delete(String id);
}

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final UserMapper userMapper;

    @Override
    public UserResponse findById(String id) {
        return userRepository.findById(id)
            .map(userMapper::toResponse)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));
    }

    @Override
    @Transactional  // Overrides readOnly=true
    public UserResponse create(CreateUserRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new ConflictException("Email already registered: " + request.email());
        }
        User user = userMapper.toEntity(request);
        user.setPassword(passwordEncoder.encode(request.password()));
        return userMapper.toResponse(userRepository.save(user));
    }
}
```

## JPA Entity

```java
@Entity
@Table(name = "users")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@EntityListeners(AuditingEntityListener.class)
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String password;

    @CreatedDate
    @Column(updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    // Factory method thay vì public constructor
    public static User create(String email, String name, String hashedPassword) {
        User user = new User();
        user.email = email;
        user.name = name;
        user.password = hashedPassword;
        return user;
    }
}
```

## Global Exception Handler

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(ResourceNotFoundException ex) {
        return ErrorResponse.of(404, ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(MethodArgumentNotValidException ex) {
        List<String> errors = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .toList();
        return ErrorResponse.of(400, "Validation failed", errors);
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleGeneral(Exception ex, HttpServletRequest request) {
        log.error("Unhandled exception at {}: {}", request.getRequestURI(), ex.getMessage(), ex);
        return ErrorResponse.of(500, "Internal server error");
    }
}
```

## Application Properties chuẩn

```yaml
# application.yml
spring:
  datasource:
    url: ${DATABASE_URL}
    hikari:
      maximum-pool-size: 10
      minimum-idle: 2
  jpa:
    hibernate:
      ddl-auto: validate   # production: validate, không phải update
    open-in-view: false    # Tắt OSIV — tránh N+1 lazy loading
  data:
    web:
      pageable:
        default-page-size: 20
        max-page-size: 100

server:
  port: ${PORT:8080}
  error:
    include-message: on-param   # Không expose error messages mặc định
```

## Anti-patterns

```java
// ❌ Logic trong controller
@PostMapping
public User create(@RequestBody Map<String, Object> body) {
    // Không dùng raw Map, không validate, no DTO
}

// ❌ @Transactional trên private method (sẽ bị ignore)
@Transactional
private void internalSave() {}

// ❌ Field injection (khó test)
@Autowired
private UserRepository repo;

// ✅ Constructor injection
private final UserRepository repo;
public UserServiceImpl(UserRepository repo) { this.repo = repo; }
```
