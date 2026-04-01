---
name: skill-lang-swift
description: Best practices viết Swift hiện đại — optionals, async/await, actors, protocols, generics, error handling và idiomatic patterns.
---

# Skill: Swift

## Optionals

```swift
// ✅ Optional binding
var name: String? = "Alice"

// if let
if let unwrapped = name {
    print("Name: \(unwrapped)")
}

// guard let — early return pattern (preferred)
func greet(_ name: String?) {
    guard let name else { return }  // Swift 5.7+ shorthand
    print("Hello, \(name)")
}

// ✅ Optional chaining
let count = user?.profile?.bio?.count

// ✅ Nil coalescing
let display = name ?? "Anonymous"

// ✅ Avoid force unwrap !
// let name = optional!  ← Crash nếu nil
```

---

## Structs vs Classes

```swift
// ✅ Struct — value type, immutable by default, preferred for data
struct User {
    let id: UUID
    let email: String
    var name: String
    let createdAt: Date
}

// ✅ Class — reference type, dùng khi cần identity/inheritance
class UserSession {
    var currentUser: User?
    weak var delegate: SessionDelegate?
}

// ✅ Immutable by default
let user = User(id: UUID(), email: "a@b.com", name: "Alice", createdAt: .now)
// user.name = "Bob"  ← Compile error (let binding)

var mutableUser = user
mutableUser.name = "Bob"  // ✅ Copy semantics
```

---

## Enums

```swift
// ✅ Enum với associated values
enum NetworkError: Error {
    case notFound(String)
    case unauthorized
    case serverError(statusCode: Int, message: String)
    case decodingFailed(Error)
}

// ✅ Exhaustive switch
func handle(_ error: NetworkError) -> String {
    switch error {
    case .notFound(let resource): return "\(resource) not found"
    case .unauthorized: return "Please log in"
    case .serverError(let code, let msg): return "Server error \(code): \(msg)"
    case .decodingFailed: return "Invalid response format"
    }
}

// ✅ Enum với computed properties
enum Status: String, CaseIterable {
    case active, inactive, pending

    var displayName: String {
        rawValue.capitalized
    }
}
```

---

## Protocols

```swift
// ✅ Protocol-Oriented Programming
protocol UserRepository {
    func findById(_ id: UUID) async throws -> User?
    func save(_ user: User) async throws -> User
    func delete(_ id: UUID) async throws
}

// Protocol extension — default implementation
extension UserRepository {
    func findByIdOrThrow(_ id: UUID) async throws -> User {
        guard let user = try await findById(id) else {
            throw NetworkError.notFound("User \(id)")
        }
        return user
    }
}

// ✅ Conformance
struct PostgresUserRepository: UserRepository {
    func findById(_ id: UUID) async throws -> User? { ... }
    func save(_ user: User) async throws -> User { ... }
    func delete(_ id: UUID) async throws { ... }
}
```

---

## Async/Await & Concurrency

```swift
// ✅ async/await
func fetchUser(id: UUID) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw NetworkError.serverError(statusCode: 404, message: "Not found")
    }

    return try JSONDecoder().decode(User.self, from: data)
}

// ✅ Parallel concurrent tasks
async let user = fetchUser(id: userId)
async let orders = fetchOrders(userId: userId)
let (resolvedUser, resolvedOrders) = try await (user, orders)

// ✅ Task group
let results = try await withThrowingTaskGroup(of: User.self) { group in
    for id in ids {
        group.addTask { try await fetchUser(id: id) }
    }

    var users: [User] = []
    for try await user in group { users.append(user) }
    return users
}
```

---

## Actors (Swift 5.5+)

```swift
// ✅ Actor — thread-safe reference type
actor UserCache {
    private var cache: [UUID: User] = [:]

    func get(_ id: UUID) -> User? {
        cache[id]
    }

    func set(_ user: User) {
        cache[user.id] = user
    }

    func invalidate(_ id: UUID) {
        cache.removeValue(forKey: id)
    }
}

// ✅ MainActor — UI updates
@MainActor
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        users = try await userService.fetchAll()
    }
}
```

---

## Generics

```swift
// ✅ Generic functions
func decode<T: Decodable>(_ type: T.Type, from data: Data) throws -> T {
    try JSONDecoder().decode(T.self, from: data)
}

// ✅ Generic types
struct Page<T> {
    let items: [T]
    let total: Int
    let page: Int
    let perPage: Int

    var hasNext: Bool { page * perPage < total }
}

// ✅ Constraints
func max<T: Comparable>(_ a: T, _ b: T) -> T { a > b ? a : b }
```

---

## Error handling

```swift
// ✅ throws/try/catch
func validateEmail(_ email: String) throws -> String {
    let regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/
    guard email.range(of: regex, options: .caseInsensitive) != nil else {
        throw ValidationError.invalidEmail(email)
    }
    return email.lowercased()
}

// ✅ Result type
func fetchUser(id: UUID) -> Result<User, NetworkError> {
    // ...
}

let result = fetchUser(id: uuid)
switch result {
case .success(let user): print(user.name)
case .failure(let error): print(error)
}

// ✅ try? — convert to Optional
let user = try? fetchUser(id: uuid)
```

---

## Property Wrappers

```swift
// ✅ Common wrappers
@State private var isLoading = false         // SwiftUI local state
@Binding var selectedTab: Int                // Pass state down
@ObservedObject var viewModel: ViewModel     // External observable
@StateObject var vm = ViewModel()            // Owned observable
@Published var users: [User] = []            // Broadcast changes
@AppStorage("theme") var theme = "light"     // UserDefaults binding
@Environment(\.dismiss) var dismiss           // Environment value
```

---

## Idioms checklist

- ✅ Prefer `struct` over `class` for data
- ✅ `guard let` thay `if let` khi cần early return
- ✅ Avoid force unwrap `!` — dùng optional binding
- ✅ Protocol over inheritance
- ✅ `async/await` thay completion handlers
- ✅ `actor` cho shared mutable state
- ✅ `Codable` cho JSON serialization
