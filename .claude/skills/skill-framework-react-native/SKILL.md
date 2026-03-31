---
name: skill-framework-react-native
description: Best practices React Native — project structure, navigation (React Navigation), native modules, platform-specific code, performance optimization, OTA updates, và app store deployment.
---

# Skill: React Native

## Project Structure

```
src/
├── app/                     # Navigation + screens
│   ├── (auth)/              # Auth stack
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/              # Bottom tab navigator
│   │   ├── home.tsx
│   │   ├── search.tsx
│   │   └── profile.tsx
│   └── _layout.tsx          # Root layout (Expo Router)
├── components/
│   ├── ui/                  # Primitives (Button, Input, Card)
│   └── features/            # Feature components
├── hooks/
├── services/                # API clients
├── stores/                  # Zustand / state management
├── utils/
├── constants/               # Colors, dimensions, config
└── types/
```

---

## Navigation (React Navigation / Expo Router)

```typescript
// Expo Router (file-based, recommended for new projects)
// app/_layout.tsx
import { Stack } from 'expo-router'

export default function RootLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="(auth)" />
      <Stack.Screen name="(tabs)" />
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
    </Stack>
  )
}

// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router'
import { Home, Search, User } from 'lucide-react-native'

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#2563eb' }}>
      <Tabs.Screen name="home" options={{ title: 'Home', tabBarIcon: ({ color }) => <Home color={color} /> }} />
      <Tabs.Screen name="search" options={{ title: 'Search', tabBarIcon: ({ color }) => <Search color={color} /> }} />
      <Tabs.Screen name="profile" options={{ title: 'Profile', tabBarIcon: ({ color }) => <User color={color} /> }} />
    </Tabs>
  )
}

// Type-safe navigation
import { useRouter, useLocalSearchParams } from 'expo-router'

function OrderItem({ id }: { id: string }) {
  const router = useRouter()
  return (
    <Pressable onPress={() => router.push(`/orders/${id}`)}>
      <Text>Order #{id}</Text>
    </Pressable>
  )
}
```

---

## Component Patterns

```typescript
// ✅ Platform-specific styles
import { Platform, StyleSheet } from 'react-native'

const styles = StyleSheet.create({
  shadow: {
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4 },
      android: { elevation: 4 },
    }),
  },
})

// ✅ Safe area handling
import { SafeAreaView } from 'react-native-safe-area-context'
import { KeyboardAvoidingView, Platform } from 'react-native'

function ScreenWrapper({ children }: PropsWithChildren) {
  return (
    <SafeAreaView style={{ flex: 1 }} edges={['top']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        {children}
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
}

// ✅ Pressable with feedback
function Button({ title, onPress, variant = 'primary' }: ButtonProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        variant === 'primary' ? styles.primary : styles.secondary,
        pressed && styles.pressed,
      ]}
      android_ripple={{ color: 'rgba(0,0,0,0.1)' }}
    >
      <Text style={styles.buttonText}>{title}</Text>
    </Pressable>
  )
}
```

---

## Performance

```typescript
// ✅ FlatList over ScrollView for large lists
import { FlatList } from 'react-native'

function OrderList({ orders }: { orders: Order[] }) {
  const renderItem = useCallback(({ item }: { item: Order }) => (
    <OrderCard order={item} />
  ), [])

  return (
    <FlatList
      data={orders}
      renderItem={renderItem}
      keyExtractor={(item) => item.id}
      initialNumToRender={10}
      maxToRenderPerBatch={10}
      windowSize={5}
      removeClippedSubviews={true}
      ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
      ListEmptyComponent={<EmptyState />}
    />
  )
}

// ✅ Image optimization
import { Image } from 'expo-image' // or react-native-fast-image

<Image
  source={{ uri: imageUrl }}
  style={{ width: 100, height: 100, borderRadius: 8 }}
  contentFit="cover"
  placeholder={blurhash}           // blur placeholder while loading
  transition={200}                 // fade in
  cachePolicy="memory-disk"
/>

// ✅ Avoid re-renders
const MemoizedCard = React.memo(OrderCard)

// ✅ Heavy computation off main thread
import { InteractionManager } from 'react-native'
useEffect(() => {
  InteractionManager.runAfterInteractions(() => {
    loadHeavyData()
  })
}, [])
```

---

## Native Modules & Storage

```typescript
// Secure storage (tokens, sensitive data)
import * as SecureStore from 'expo-secure-store'

await SecureStore.setItemAsync('auth_token', token)
const token = await SecureStore.getItemAsync('auth_token')

// Async storage (non-sensitive data)
import AsyncStorage from '@react-native-async-storage/async-storage'

await AsyncStorage.setItem('user_preferences', JSON.stringify(prefs))

// Biometric authentication
import * as LocalAuthentication from 'expo-local-authentication'

const hasHardware = await LocalAuthentication.hasHardwareAsync()
const result = await LocalAuthentication.authenticateAsync({
  promptMessage: 'Verify identity',
  fallbackLabel: 'Use passcode',
})
if (result.success) { /* authenticated */ }

// Push notifications
import * as Notifications from 'expo-notifications'

const { status } = await Notifications.requestPermissionsAsync()
const token = (await Notifications.getExpoPushTokenAsync()).data
// Send token to backend for push delivery
```

---

## API & Offline

```typescript
// ✅ TanStack Query for API state
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import NetInfo from '@react-native-community/netinfo'

function useOrders() {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => api.getOrders(),
    staleTime: 5 * 60 * 1000,
  })
}

// ✅ Offline support — persist cache
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister'

const persister = createAsyncStoragePersister({ storage: AsyncStorage })
// Wrap QueryClient with PersistQueryClientProvider

// ✅ Network status hook
function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState(true)
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected ?? false)
    })
    return unsubscribe
  }, [])
  return isConnected
}
```

---

## Deployment

```yaml
expo_eas:
  build: "eas build --platform all --profile production"
  submit: "eas submit --platform all"
  ota_update: "eas update --branch production --message 'Bug fix'"

over_the_air_updates:
  tool: "expo-updates / CodePush"
  benefit: "Push JS bundle updates without App Store review"
  limitation: "Cannot change native code (only JS/assets)"
  strategy:
    critical_fix: "Force update (block app until updated)"
    minor_fix: "Background update (apply on next restart)"

app_store:
  ios: "TestFlight → App Store Review → Release"
  android: "Internal testing → Open testing → Production"
  versioning: "SemVer: major.minor.patch (1.2.3) + buildNumber auto-increment"
```

---

## Anti-patterns

```yaml
inline_styles_everywhere:
  bad: "<View style={{ marginTop: 10, padding: 16, backgroundColor: '#fff' }}>"
  fix: "StyleSheet.create() — cached and optimized by bridge"

scrollview_for_lists:
  bad: "<ScrollView>{items.map(i => <Item />)}</ScrollView>"
  fix: "<FlatList data={items} /> — virtualized, only renders visible items"

console_log_in_prod:
  bad: "console.log() left in production builds"
  fix: "Remove with babel-plugin-transform-remove-console"

storing_tokens_in_asyncstorage:
  bad: "AsyncStorage.setItem('token', jwt) — not encrypted"
  fix: "SecureStore (iOS Keychain / Android Keystore)"
```
