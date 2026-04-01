---
name: skill-framework-expo
description: Best practices Expo (React Native) — project setup, routing với Expo Router, native modules, OTA updates, EAS Build, và production deployment.
---

# Skill: Expo

## Khi nào dùng

- React Native app cần managed workflow (không muốn native config)
- OTA updates, EAS Build/Submit
- Cross-platform: iOS + Android + Web từ 1 codebase

---

## Project structure (Expo Router)

```
app/
  _layout.tsx           # Root layout (Slot, Stack, Tabs)
  (auth)/
    _layout.tsx
    login.tsx
    register.tsx
  (app)/
    _layout.tsx          # Tab navigator
    index.tsx            # Home tab
    profile.tsx
  +not-found.tsx
components/
  ui/                    # Shared UI components
  forms/
hooks/
  useAuth.ts
  useTheme.ts
lib/
  api.ts
  storage.ts
constants/
  Colors.ts
  Layout.ts
assets/
  fonts/
  images/
```

---

## app.json / expo config

```json
{
  "expo": {
    "name": "MyApp",
    "slug": "my-app",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "scheme": "myapp",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain"
    },
    "ios": {
      "bundleIdentifier": "com.myorg.myapp",
      "supportsTablet": false
    },
    "android": {
      "package": "com.myorg.myapp",
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png"
      }
    },
    "plugins": ["expo-router", "expo-secure-store"],
    "experiments": { "typedRoutes": true }
  }
}
```

---

## Expo Router — Navigation

```tsx
// app/_layout.tsx
import { Stack } from "expo-router";
import { GestureHandlerRootView } from "react-native-gesture-handler";

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <Stack>
        <Stack.Screen name="(auth)" options={{ headerShown: false }} />
        <Stack.Screen name="(app)" options={{ headerShown: false }} />
      </Stack>
    </GestureHandlerRootView>
  );
}

// app/(app)/_layout.tsx
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function AppLayout() {
  return (
    <Tabs>
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color }) => (
            <Ionicons name="home" size={24} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}

// Navigation
import { router, useLocalSearchParams } from "expo-router";
router.push("/profile");
router.push({ pathname: "/product/[id]", params: { id: "123" } });
```

---

## Auth pattern với SecureStore

```typescript
import * as SecureStore from "expo-secure-store";

// ✅ Token storage
export const tokenStorage = {
  async get(key: string): Promise<string | null> {
    return SecureStore.getItemAsync(key);
  },
  async set(key: string, value: string): Promise<void> {
    await SecureStore.setItemAsync(key, value, {
      keychainAccessible: SecureStore.WHEN_UNLOCKED,
    });
  },
  async remove(key: string): Promise<void> {
    await SecureStore.deleteItemAsync(key);
  },
};
```

---

## API calls với Axios/fetch

```typescript
import axios from "axios";
import { tokenStorage } from "./storage";

const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL,
  timeout: 10000,
});

api.interceptors.request.use(async (config) => {
  const token = await tokenStorage.get("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      await tokenStorage.remove("access_token");
      router.replace("/(auth)/login");
    }
    return Promise.reject(error);
  },
);
```

---

## EAS Build & Submit

```bash
# eas.json
{
  "cli": { "version": ">= 5.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {}
  },
  "submit": {
    "production": {}
  }
}

# Build
eas build --profile production --platform all

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

---

## OTA Updates (expo-updates)

```typescript
import * as Updates from "expo-updates";

async function checkForUpdates() {
  if (!Updates.isEmbeddedLaunch) return;

  try {
    const update = await Updates.checkForUpdateAsync();
    if (update.isAvailable) {
      await Updates.fetchUpdateAsync();
      await Updates.reloadAsync();
    }
  } catch (e) {
    console.error("Update check failed:", e);
  }
}
```

---

## Performance checklist

- ✅ Dùng `FlashList` thay `FlatList` cho danh sách lớn
- ✅ Image optimization với `expo-image`
- ✅ Lazy load screens với Expo Router dynamic imports
- ✅ Avoid anonymous functions trong render
- ✅ `useMemo`/`useCallback` cho expensive computations

---

## Environment variables

```
# .env
EXPO_PUBLIC_API_URL=https://api.example.com
# Prefix EXPO_PUBLIC_ → available in client code
# Non-prefixed → server/EAS only

# Access
process.env.EXPO_PUBLIC_API_URL
```

---

## Key packages

| Package                        | Purpose                   |
| ------------------------------ | ------------------------- |
| `expo-router`                  | File-based routing        |
| `expo-secure-store`            | Encrypted token storage   |
| `expo-image`                   | Optimized image component |
| `expo-updates`                 | OTA updates               |
| `expo-notifications`           | Push notifications        |
| `expo-camera`                  | Camera access             |
| `@shopify/flash-list`          | High-perf list            |
| `react-native-gesture-handler` | Gesture support           |
| `react-native-reanimated`      | Animations                |
