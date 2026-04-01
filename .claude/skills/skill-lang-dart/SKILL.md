---
name: skill-lang-dart
description: Best practices viết Dart hiện đại — null safety, async/await, streams, collections, patterns và idiomatic code cho Flutter/server.
---

# Skill: Dart

## Null Safety

```dart
// ✅ Non-nullable by default (Dart 2.12+)
String name = 'Alice';      // non-nullable
String? nullable = null;    // nullable

// ✅ Null-aware operators
String display = nullable ?? 'Anonymous';  // null coalescing
int? length = nullable?.length;            // safe call
String upper = nullable!.toUpperCase();    // force (use sparingly)

// ✅ Late initialization
late final String config;
void init() {
  config = loadConfig();  // assigned before use
}

// ✅ if-null assignment
nullable ??= 'default';
```

---

## Classes & Constructors

```dart
// ✅ Class with named constructor
class User {
  final String id;
  final String email;
  String name;
  final DateTime createdAt;

  // ✅ Initializing formals
  const User({
    required this.id,
    required this.email,
    required this.name,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  // ✅ Named constructors
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      name: json['name'] as String,
    );
  }

  // ✅ copyWith
  User copyWith({String? name, String? email}) {
    return User(
      id: id,
      email: email ?? this.email,
      name: name ?? this.name,
      createdAt: createdAt,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'name': name,
    'createdAt': createdAt.toIso8601String(),
  };
}
```

---

## Enums (Enhanced — Dart 2.17+)

```dart
// ✅ Enhanced enums with members
enum Status {
  active('Active'),
  inactive('Inactive'),
  pending('Pending review');

  const Status(this.label);
  final String label;

  bool get isActive => this == Status.active;
}

// Usage
final status = Status.active;
print(status.label);  // Active
print(status.isActive);  // true
```

---

## Async / Await

```dart
// ✅ Future — single async value
Future<User?> fetchUser(String id) async {
  final response = await http.get(Uri.parse('/users/$id'));
  if (response.statusCode == 404) return null;
  return User.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
}

// ✅ Parallel
final userFuture = fetchUser(id);
final ordersFuture = fetchOrders(id);
final [user, orders] = await Future.wait([userFuture, ordersFuture]);

// ✅ Error handling
try {
  final user = await fetchUser(id);
  if (user == null) throw NotFoundException('User $id not found');
} on SocketException {
  throw NetworkException('No network connection');
} on TimeoutException {
  throw NetworkException('Request timed out');
}
```

---

## Streams

```dart
// ✅ Stream — async sequence
Stream<User> watchUsers() async* {
  while (true) {
    yield await fetchActiveUsers();
    await Future.delayed(const Duration(seconds: 5));
  }
}

// ✅ Using streams
final subscription = watchUsers().listen(
  (user) => print('User updated: ${user.name}'),
  onError: (e) => print('Error: $e'),
  onDone: () => print('Done'),
);

// ✅ StreamController
final controller = StreamController<String>.broadcast();
controller.sink.add('event');
controller.stream.listen((e) => print(e));
await controller.close();

// ✅ Stream transformations
watchUsers()
  .where((u) => u.isActive)
  .map((u) => u.email)
  .distinct()
  .listen(print);
```

---

## Collections

```dart
// ✅ Collection if/for literals
final items = [
  'always',
  if (isLoggedIn) 'profile',
  if (isAdmin) ...<String>['admin-panel', 'settings'],
  for (final tag in tags) 'tag:$tag',
];

// ✅ Spread
final combined = [...list1, ...list2, ...?nullableList];

// ✅ Map operations
final emails = users.map((u) => u.email).toList();
final admins = users.where((u) => u.role == 'admin').toList();
final byId = {for (final u in users) u.id: u};
final total = prices.fold(0.0, (sum, p) => sum + p);

// ✅ Records (Dart 3.0+)
(String, int) pair = ('hello', 42);
final (name, age) = pair;

({String name, int age}) person = (name: 'Alice', age: 30);
```

---

## Pattern Matching (Dart 3.0+)

```dart
// ✅ switch expression
String describe(Object obj) => switch (obj) {
  int n when n < 0 => 'negative int',
  int n => 'int: $n',
  String s => 'string: $s',
  [int x, int y] => 'point: ($x, $y)',
  _ => 'other',
};

// ✅ Destructuring in switch
switch (shape) {
  case Circle(radius: final r):
    print('Circle with radius $r');
  case Rectangle(width: final w, height: final h):
    print('Rectangle ${w}x$h');
}
```

---

## Extensions

```dart
// ✅ Extension methods
extension StringExtensions on String {
  bool get isValidEmail =>
      RegExp(r'^[\w.-]+@[\w-]+\.[a-zA-Z]{2,}$').hasMatch(this);

  String capitalize() =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';
}

extension ListExtensions<T> on List<T> {
  List<T> uniqueBy<K>(K Function(T) key) {
    final seen = <K>{};
    return where((e) => seen.add(key(e))).toList();
  }
}

// Usage
'user@example.com'.isValidEmail  // true
'hello'.capitalize()  // Hello
```

---

## Error handling

```dart
// ✅ Custom exceptions
class NotFoundException implements Exception {
  const NotFoundException(this.message);
  final String message;

  @override
  String toString() => 'NotFoundException: $message';
}

// ✅ Result type pattern
sealed class Result<T> {
  const Result();
}

class Success<T> extends Result<T> {
  const Success(this.data);
  final T data;
}

class Failure<T> extends Result<T> {
  const Failure(this.error);
  final Object error;
}

// Usage with pattern matching
final result = await fetchUser(id);
switch (result) {
  case Success(data: final user):
    print(user.name);
  case Failure(error: final e):
    print('Error: $e');
}
```

---

## Idioms checklist

- ✅ Sound null safety — avoid `!` unless certain
- ✅ `const` constructors cho immutable objects
- ✅ `factory` constructors cho JSON deserialization
- ✅ `copyWith` pattern cho immutable updates
- ✅ Enhanced enums (Dart 2.17+) với members
- ✅ Sealed classes (Dart 3+) cho exhaustive patterns
- ✅ Collection literals (if/for) thay imperative loops
- ✅ Extensions để add behavior on existing types
