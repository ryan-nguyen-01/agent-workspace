---
name: skill-lang-go
description: Best practices viết Go idiomatic: error handling, interfaces, goroutines, channels và project structure chuẩn.
---

# Skill: Go

## Error Handling — Idiomatic Go

```go
// ✅ Luôn handle error, không ignore
user, err := userRepo.FindByID(ctx, id)
if err != nil {
    return nil, fmt.Errorf("findUser %s: %w", id, err)
}

// ✅ Sentinel errors cho known cases
var (
    ErrNotFound   = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// ✅ Custom error types với context
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed for %s: %s", e.Field, e.Message)
}

// ✅ errors.Is và errors.As cho error checking
if errors.Is(err, ErrNotFound) {
    return http.StatusNotFound
}

var validErr *ValidationError
if errors.As(err, &validErr) {
    return http.StatusBadRequest
}
```

## Interfaces — Small & Focused

```go
// ✅ Interface nhỏ, single purpose
type UserReader interface {
    FindByID(ctx context.Context, id string) (*User, error)
}

type UserWriter interface {
    Create(ctx context.Context, user *User) error
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id string) error
}

// ✅ Compose interfaces
type UserRepository interface {
    UserReader
    UserWriter
}

// ✅ Định nghĩa interface tại nơi consume, không nơi implement
// package service — define interface để inject dependency
type userRepo interface {
    FindByID(ctx context.Context, id string) (*User, error)
}
```

## Structs & Methods

```go
// ✅ Constructor function
type UserService struct {
    repo   UserRepository
    hasher PasswordHasher
    logger *slog.Logger
}

func NewUserService(repo UserRepository, hasher PasswordHasher, logger *slog.Logger) *UserService {
    if repo == nil {
        panic("repo is required")
    }
    return &UserService{repo: repo, hasher: hasher, logger: logger}
}

// ✅ Method receiver: pointer cho mutation, value cho read-only
func (s *UserService) CreateUser(ctx context.Context, req CreateUserRequest) (*User, error) {
    // mutates nothing but large struct → pointer receiver
}
```

## Goroutines & Channels

```go
// ✅ Goroutine phải có cơ chế stop
func worker(ctx context.Context, jobs <-chan Job) {
    for {
        select {
        case job, ok := <-jobs:
            if !ok {
                return // channel closed
            }
            processJob(job)
        case <-ctx.Done():
            return // context cancelled
        }
    }
}

// ✅ errgroup cho parallel tasks
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(ctx)

g.Go(func() error {
    return fetchUser(ctx, userID)
})
g.Go(func() error {
    return fetchProfile(ctx, userID)
})

if err := g.Wait(); err != nil {
    return err
}
```

## Context

```go
// ✅ Context luôn là parameter đầu tiên
func FindUser(ctx context.Context, id string) (*User, error)

// ✅ Timeout / deadline
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

result, err := externalAPI.Call(ctx, params)

// ✅ Context values chỉ cho request-scoped data
type contextKey string
const userIDKey contextKey = "userID"

func WithUserID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, userIDKey, id)
}
func GetUserID(ctx context.Context) (string, bool) {
    id, ok := ctx.Value(userIDKey).(string)
    return id, ok
}
```

## Project Structure chuẩn

```
myapp/
├── cmd/
│   └── server/main.go      # entry point
├── internal/               # không export ra ngoài module
│   ├── domain/             # business entities
│   ├── service/            # business logic
│   ├── repository/         # data access
│   └── handler/            # HTTP handlers
├── pkg/                    # có thể dùng bởi external packages
│   ├── logger/
│   └── validator/
├── config/
└── go.mod
```

## Naming

```
Packages:   lowercase, short, no underscores  user, auth, order
Interfaces: -er suffix khi có thể             Reader, Writer, Storer
Variables:  camelCase, short in scope         u, usr (loop), user (wider)
Constants:  PascalCase hoặc ALL_CAPS          MaxRetries, DefaultTimeout
Errors:     Err prefix                        ErrNotFound, ErrUnauthorized
```
