---
name: skill-lang-kotlin
description: Best practices viết Kotlin hiện đại — coroutines, data classes, sealed classes, extension functions, null safety và idiomatic patterns.
---

# Skill: Kotlin

## Null Safety

```kotlin
// ✅ Nullable types phải explicit
var name: String? = null

// ✅ Safe call operator
val length = name?.length        // null nếu name null
val upper = name?.uppercase()

// ✅ Elvis operator
val display = name ?: "Anonymous"

// ✅ let cho null-safe block
name?.let { n ->
    println("Name: $n")
}

// ✅ Avoid !! — chỉ dùng khi chắc chắn không null
val length = name!!.length  // throws NullPointerException nếu null
```

---

## Data Classes

```kotlin
// ✅ Data class — auto-generate equals/hashCode/toString/copy
data class User(
    val id: String,
    val email: String,
    val name: String,
    val createdAt: Instant = Instant.now(),
)

// ✅ copy() cho immutable updates
val updated = user.copy(name = "New Name")

// ✅ Destructuring
val (id, email, name) = user
```

---

## Sealed Classes (Result pattern)

```kotlin
// ✅ Sealed class cho exhaustive when
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

fun handleResult(result: Result<User>) = when (result) {
    is Result.Success -> println("User: ${result.data.name}")
    is Result.Error -> println("Error: ${result.exception.message}")
    Result.Loading -> println("Loading...")
}

// ✅ Sealed interface (Kotlin 1.5+)
sealed interface ApiResponse {
    data class Ok<T>(val body: T) : ApiResponse
    data class NotFound(val message: String) : ApiResponse
    data class Unauthorized(val reason: String) : ApiResponse
}
```

---

## Coroutines

```kotlin
import kotlinx.coroutines.*

// ✅ suspend functions — non-blocking async
suspend fun fetchUser(id: String): User {
    return withContext(Dispatchers.IO) {
        userRepository.findById(id)
            ?: throw NotFoundException("User $id not found")
    }
}

// ✅ Launch vs Async
// launch — fire and forget
scope.launch {
    sendEmail(user.email)
}

// async/await — concurrent + result
val userDeferred = async { fetchUser(id) }
val ordersDeferred = async { fetchOrders(id) }
val user = userDeferred.await()
val orders = ordersDeferred.await()

// ✅ Flow — async stream
fun getUserUpdates(id: String): Flow<User> = flow {
    while (true) {
        emit(fetchUser(id))
        delay(5000)
    }
}
```

---

## Extension Functions

```kotlin
// ✅ Extension functions — thêm behavior mà không inherit
fun String.isValidEmail(): Boolean =
    matches(Regex("^[A-Za-z0-9+_.-]+@(.+)\$"))

fun List<User>.activeOnly(): List<User> =
    filter { it.isActive }

// ✅ Extension properties
val User.fullName: String
    get() = "$firstName $lastName"
```

---

## Scope Functions

```kotlin
// let — transform hoặc null-safe block
val result = user?.let { u ->
    "${u.name} (${u.email})"
}

// apply — configure object, returns itself
val user = User().apply {
    name = "John"
    email = "john@example.com"
}

// run — transform, returns last expression
val isValid = user.run {
    email.isNotEmpty() && name.isNotEmpty()
}

// also — side effects, returns original
val user = createUser(data).also {
    logger.info("Created user: ${it.id}")
}

// with — multiple operations on object
with(response) {
    addHeader("X-Request-Id", requestId)
    status = 200
}
```

---

## Collections

```kotlin
// ✅ Immutable by default
val users = listOf("Alice", "Bob")
val mutableUsers = mutableListOf("Alice", "Bob")

// ✅ Functional operations
val activeEmails = users
    .filter { it.isActive }
    .map { it.email }
    .distinct()
    .sorted()

// ✅ groupBy
val byRole = users.groupBy { it.role }

// ✅ Sequences cho lazy evaluation (danh sách lớn)
users.asSequence()
    .filter { it.isActive }
    .map { it.email }
    .take(10)
    .toList()
```

---

## Object & Companion Object

```kotlin
// ✅ Singleton
object DatabaseConfig {
    val url: String = System.getenv("DB_URL")
    val poolSize: Int = 10
}

// ✅ Companion object — static members
class UserService(private val repo: UserRepository) {
    companion object {
        private val logger = LoggerFactory.getLogger(UserService::class.java)

        fun create(repo: UserRepository): UserService = UserService(repo)
    }
}
```

---

## Error handling

```kotlin
// ✅ Result<T> (stdlib)
fun parseJson(input: String): Result<Data> = runCatching {
    Json.decodeFromString<Data>(input)
}

val data = parseJson(input)
    .getOrElse { throw BadRequestException("Invalid JSON") }

// ✅ Custom exceptions
class NotFoundException(message: String) : RuntimeException(message)
class ValidationException(val errors: List<String>) : RuntimeException(errors.joinToString())
```

---

## Interfaces & Generics

```kotlin
interface Repository<T, ID> {
    suspend fun findById(id: ID): T?
    suspend fun save(entity: T): T
    suspend fun delete(id: ID)
}

class UserRepository(private val db: Database) : Repository<User, String> {
    override suspend fun findById(id: String): User? =
        db.users.find { it.id == id }

    override suspend fun save(entity: User): User =
        db.users.upsert(entity)

    override suspend fun delete(id: String) {
        db.users.removeIf { it.id == id }
    }
}
```

---

## Idioms checklist

- ✅ Prefer `val` over `var`
- ✅ Dùng data classes cho DTOs và value objects
- ✅ Sealed classes thay enum khi có dữ liệu kèm
- ✅ Extension functions thay utility classes
- ✅ Coroutines thay callbacks/threads
- ✅ `?.` và `?:` thay if-null checks
- ✅ `when` expression thay switch/if chains
