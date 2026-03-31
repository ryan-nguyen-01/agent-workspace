---
name: skill-testing-junit
description: Best practices viết tests với JUnit 5 + Mockito + Spring Boot Test: unit tests, integration tests, mocking và test slices.
---

# Skill: JUnit 5 + Mockito + Spring Boot Test

## Unit Test Structure

```java
// service/UserServiceTest.java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserServiceImpl userService;

    @Test
    @DisplayName("findById: returns user when found")
    void findById_ReturnsUser_WhenExists() {
        // Arrange
        User user = UserFactory.build();
        when(userRepository.findById(user.getId())).thenReturn(Optional.of(user));

        // Act
        UserResponse result = userService.findById(user.getId());

        // Assert
        assertThat(result.id()).isEqualTo(user.getId());
        assertThat(result.email()).isEqualTo(user.getEmail());
        verify(userRepository).findById(user.getId());
    }

    @Test
    @DisplayName("findById: throws ResourceNotFoundException when not found")
    void findById_ThrowsNotFound_WhenMissing() {
        when(userRepository.findById("999")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> userService.findById("999"))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("999");
    }
}
```

## Test Factory / Builder

```java
// tests/UserFactory.java
public class UserFactory {
    private static final Faker faker = new Faker();

    public static User build() {
        return build(user -> {});
    }

    public static User build(Consumer<User> customizer) {
        User user = User.create(
            faker.internet().emailAddress(),
            faker.name().fullName(),
            "$2a$12$hashedpassword"
        );
        customizer.accept(user);
        return user;
    }

    public static CreateUserRequest buildRequest() {
        return new CreateUserRequest(
            faker.internet().emailAddress(),
            faker.name().fullName(),
            "Password123!"
        );
    }
}
```

## Parametrized Tests

```java
@ParameterizedTest
@ValueSource(strings = {"", "  ", "a"})
@DisplayName("create: throws validation error for invalid name")
void create_ThrowsValidation_ForInvalidName(String name) {
    CreateUserRequest request = new CreateUserRequest("test@test.com", name, "password123");

    assertThatThrownBy(() -> userService.create(request))
        .isInstanceOf(ValidationException.class);
}

@ParameterizedTest
@CsvSource({
    "admin, true",
    "user, false",
    "moderator, true",
})
void checkAdminAccess_ReturnsCorrectResult(String role, boolean expected) {
    assertThat(service.canAccessAdmin(role)).isEqualTo(expected);
}

@ParameterizedTest
@MethodSource("invalidEmails")
void create_ThrowsValidation_ForInvalidEmail(String email) {
    assertThatCode(() -> userService.create(new CreateUserRequest(email, "Name", "pass1234")))
        .isInstanceOf(ValidationException.class);
}

static Stream<String> invalidEmails() {
    return Stream.of("", "not-email", "@nodomain", "no@", "a".repeat(256) + "@test.com");
}
```

## Spring Boot Test Slices

```java
// ✅ @WebMvcTest — chỉ test controller layer
@WebMvcTest(UserController.class)
@Import(SecurityConfig.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void create_Returns201_WithValidRequest() throws Exception {
        CreateUserRequest request = UserFactory.buildRequest();
        UserResponse response = new UserResponse("id-123", request.email(), request.name(), LocalDateTime.now());
        when(userService.create(any())).thenReturn(response);

        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.email").value(request.email()))
            .andExpect(jsonPath("$.id").value("id-123"));
    }

    @Test
    void create_Returns400_WhenEmailInvalid() throws Exception {
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email": "not-valid", "name": "Test", "password": "pass12345"}
                """))
            .andExpect(status().isBadRequest());
    }
}

// ✅ @DataJpaTest — chỉ test repository layer
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class UserRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
        .withDatabaseName("testdb");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
    }

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByEmail_ReturnsUser_WhenExists() {
        User user = UserFactory.build();
        userRepository.save(user);

        Optional<User> found = userRepository.findByEmail(user.getEmail());

        assertThat(found).isPresent();
        assertThat(found.get().getEmail()).isEqualTo(user.getEmail());
    }
}
```

## Integration Test

```java
// ✅ Full Spring context với TestContainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class UserIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15");

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createUser_FullFlow_Returns201() {
        CreateUserRequest request = UserFactory.buildRequest();

        ResponseEntity<UserResponse> response = restTemplate.postForEntity(
            "/api/v1/users", request, UserResponse.class
        );

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().email()).isEqualTo(request.email());
    }
}
```

## AssertJ Custom Assertions

```java
// ✅ AssertJ thay vì JUnit assertions — more readable
assertThat(users)
    .hasSize(3)
    .extracting(UserResponse::email)
    .containsExactlyInAnyOrder("a@test.com", "b@test.com", "c@test.com");

assertThat(exception)
    .isInstanceOf(ResourceNotFoundException.class)
    .hasMessage("User 'abc' not found");
```

## Anti-patterns

```java
// ❌ @SpringBootTest cho unit tests (chậm)
@SpringBootTest
class UserServiceTest { ... }  // ❌ Dùng @ExtendWith(MockitoExtension.class)

// ❌ Nhiều assertions ẩn
@Test
void testUser() {
    User u = service.create(req);
    assertEquals("test@test.com", u.getEmail());
    assertTrue(u.isActive());
    assertNotNull(u.getId());  // Không rõ test cái gì
}

// ❌ Test không có @DisplayName — khó đọc khi fail
@Test
void test1() { ... }

// ❌ Shared mutable state giữa tests
static User sharedUser;  // Race condition trong parallel tests
```
