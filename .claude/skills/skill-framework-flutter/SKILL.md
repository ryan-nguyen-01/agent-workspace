---
name: skill-framework-flutter
description: Best practices Flutter/Dart — project structure, state management (Riverpod, BLoC), navigation (GoRouter), platform channels, performance, và app deployment.
---

# Skill: Flutter

## Project Structure

```
lib/
├── app/                     # App config, theme, routes
│   ├── app.dart
│   ├── routes.dart
│   └── theme.dart
├── features/                # Feature-first organization
│   ├── auth/
│   │   ├── data/            # Repository, data sources
│   │   ├── domain/          # Models, interfaces
│   │   └── presentation/    # Screens, widgets, controllers
│   ├── home/
│   └── orders/
├── shared/
│   ├── widgets/             # Reusable UI components
│   ├── services/            # API client, storage, etc.
│   ├── providers/           # Riverpod providers
│   └── utils/
└── main.dart
```

---

## State Management (Riverpod — Recommended)

```dart
// providers/auth_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_provider.g.dart';

@riverpod
class Auth extends _$Auth {
  @override
  AsyncValue<User?> build() => const AsyncValue.data(null);

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final user = await ref.read(authRepositoryProvider).login(email, password);
      return user;
    });
  }

  Future<void> logout() async {
    await ref.read(authRepositoryProvider).logout();
    state = const AsyncValue.data(null);
  }
}

// Usage in widget
class LoginScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    return authState.when(
      data: (user) => user != null ? const HomeScreen() : const LoginForm(),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => ErrorWidget(error.toString()),
    );
  }
}
```

---

## Navigation (GoRouter)

```dart
final router = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    final isLoggedIn = /* check auth */;
    final isAuthRoute = state.matchedLocation.startsWith('/auth');

    if (!isLoggedIn && !isAuthRoute) return '/auth/login';
    if (isLoggedIn && isAuthRoute) return '/';
    return null;
  },
  routes: [
    ShellRoute(
      builder: (context, state, child) => ScaffoldWithNavBar(child: child),
      routes: [
        GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
        GoRoute(path: '/orders', builder: (_, __) => const OrdersScreen()),
        GoRoute(
          path: '/orders/:id',
          builder: (_, state) => OrderDetailScreen(id: state.pathParameters['id']!),
        ),
        GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
      ],
    ),
    GoRoute(path: '/auth/login', builder: (_, __) => const LoginScreen()),
  ],
);
```

---

## Widget Patterns

```dart
// ✅ Reusable styled button
class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final bool isLoading;
  final ButtonVariant variant;

  const AppButton({
    required this.label,
    required this.onPressed,
    this.isLoading = false,
    this.variant = ButtonVariant.primary,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: _getStyle(context),
        child: isLoading
            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
            : Text(label),
      ),
    );
  }
}

// ✅ Platform-adaptive widget
Widget buildAdaptive(BuildContext context) {
  return Platform.isIOS
      ? CupertinoAlertDialog(title: Text('Confirm'), actions: [...])
      : AlertDialog(title: Text('Confirm'), actions: [...]);
}
```

---

## API & Data Layer

```dart
// Repository pattern
abstract class OrderRepository {
  Future<List<Order>> getOrders({int page = 1});
  Future<Order> getOrderById(String id);
  Future<Order> createOrder(CreateOrderDto dto);
}

class OrderRepositoryImpl implements OrderRepository {
  final Dio _dio;
  final OrderLocalDataSource _local;

  OrderRepositoryImpl(this._dio, this._local);

  @override
  Future<List<Order>> getOrders({int page = 1}) async {
    try {
      final response = await _dio.get('/orders', queryParameters: {'page': page});
      final orders = (response.data['data'] as List).map((e) => Order.fromJson(e)).toList();
      await _local.cacheOrders(orders);
      return orders;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionError) {
        return _local.getCachedOrders();
      }
      rethrow;
    }
  }
}

// Dio setup with interceptors
final dio = Dio(BaseOptions(baseUrl: 'https://api.myapp.com/v1'))
  ..interceptors.addAll([
    AuthInterceptor(tokenStorage),
    LogInterceptor(requestBody: true, responseBody: true),
    RetryInterceptor(retries: 3),
  ]);
```

---

## Performance

```dart
// ✅ const constructors (avoid rebuilds)
const SizedBox(height: 16) // ✅ compile-time constant
SizedBox(height: 16)       // ❌ new instance every build

// ✅ ListView.builder for large lists (virtualized)
ListView.builder(
  itemCount: orders.length,
  itemBuilder: (context, index) => OrderCard(order: orders[index]),
)

// ✅ RepaintBoundary for complex widgets
RepaintBoundary(child: ComplexChart(data: chartData))

// ✅ Cached network images
CachedNetworkImage(
  imageUrl: user.avatarUrl,
  placeholder: (_, __) => const CircularProgressIndicator(),
  errorWidget: (_, __, ___) => const Icon(Icons.person),
)

// ✅ Isolates for heavy computation
final result = await compute(parseJsonInBackground, jsonString);
```

---

## Secure Storage & Platform Channels

```dart
// Secure storage
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const storage = FlutterSecureStorage();
await storage.write(key: 'token', value: accessToken);
final token = await storage.read(key: 'token');

// Biometric auth
import 'package:local_auth/local_auth.dart';

final localAuth = LocalAuthentication();
final didAuth = await localAuth.authenticate(
  localizedReason: 'Verify your identity',
  options: const AuthenticationOptions(biometricOnly: true),
);

// Platform channel (native code integration)
const platform = MethodChannel('com.myapp/native');
final batteryLevel = await platform.invokeMethod<int>('getBatteryLevel');
```

---

## Deployment

```yaml
android:
  signing: "keystore file (NEVER commit to git)"
  build: "flutter build appbundle --release"
  store: "Google Play Console → Internal → Open → Production"

ios:
  signing: "Apple Developer certificate + provisioning profile"
  build: "flutter build ipa --release"
  store: "Transporter → App Store Connect → TestFlight → Review"

ci_cd:
  tool: "Codemagic, GitHub Actions, Fastlane"
  steps: [lint, test, build, sign, deploy]
```

---

## Anti-patterns

```yaml
setState_everywhere:
  bad: "setState() in every widget for shared state"
  fix: "Use Riverpod/BLoC for shared state, setState only for local UI state"

god_widget:
  bad: "Single widget with 500+ lines, all logic inline"
  fix: "Split into smaller widgets, extract logic to controllers/providers"

no_const:
  bad: "Widget without const → rebuilds every time parent rebuilds"
  fix: "Add const to widget constructors, use const wherever possible"
```
