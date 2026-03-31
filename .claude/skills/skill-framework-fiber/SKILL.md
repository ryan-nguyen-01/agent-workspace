---
name: skill-framework-fiber
description: Best practices xây dựng REST APIs với Fiber framework (Go): routing, middleware, validation, error handling và high-performance patterns.
---

# Skill: Fiber (Go)

## App Setup

```go
// cmd/server/main.go
package main

import (
    "os"
    "os/signal"
    "syscall"
    "github.com/gofiber/fiber/v2"
    "github.com/gofiber/fiber/v2/middleware/compress"
    "github.com/gofiber/fiber/v2/middleware/cors"
    "github.com/gofiber/fiber/v2/middleware/helmet"
    "github.com/gofiber/fiber/v2/middleware/limiter"
    "github.com/gofiber/fiber/v2/middleware/requestid"
)

func main() {
    app := fiber.New(fiber.Config{
        AppName:               "MyService v1.0",
        ReadTimeout:           5 * time.Second,
        WriteTimeout:          10 * time.Second,
        IdleTimeout:           120 * time.Second,
        BodyLimit:             10 * 1024 * 1024,  // 10MB
        ErrorHandler:          customErrorHandler,
        DisableStartupMessage: true,
    })

    // ✅ Middleware
    app.Use(requestid.New())
    app.Use(helmet.New())
    app.Use(compress.New())
    app.Use(cors.New(cors.Config{
        AllowOrigins: os.Getenv("CORS_ORIGINS"),
        AllowHeaders: "Origin, Content-Type, Accept, Authorization",
    }))
    app.Use(limiter.New(limiter.Config{
        Max:        100,
        Expiration: time.Minute,
        KeyGenerator: func(c *fiber.Ctx) string {
            return c.IP()
        },
    }))

    // ✅ Dependency injection
    db := database.Connect(cfg)
    setupRoutes(app, db)

    // ✅ Graceful shutdown
    c := make(chan os.Signal, 1)
    signal.Notify(c, os.Interrupt, syscall.SIGTERM)
    go func() {
        <-c
        app.Shutdown()
    }()

    app.Listen(":" + cfg.Port)
}
```

## Routes & Handlers

```go
// internal/routes/user_routes.go
func SetupUserRoutes(router fiber.Router, h *UserHandler, authMiddleware fiber.Handler) {
    users := router.Group("/users")
    users.Get("/", authMiddleware, h.List)
    users.Get("/:id", authMiddleware, h.GetByID)
    users.Post("/", h.Create)
    users.Patch("/:id", authMiddleware, h.Update)
    users.Delete("/:id", authMiddleware, h.Delete)
}

// internal/handler/user_handler.go
type UserHandler struct {
    svc service.UserService
    v   *validator.Validate
}

func (h *UserHandler) GetByID(c *fiber.Ctx) error {
    id := c.Params("id")

    user, err := h.svc.FindByID(c.Context(), id)
    if err != nil {
        return err  // ✅ Fiber's ErrorHandler handles it
    }

    return c.JSON(toUserResponse(user))
}

func (h *UserHandler) Create(c *fiber.Ctx) error {
    var req dto.CreateUserRequest
    if err := c.BodyParser(&req); err != nil {
        return fiber.NewError(fiber.StatusBadRequest, "Invalid request body")
    }

    if err := h.v.Struct(&req); err != nil {
        return &fiber.Error{
            Code:    fiber.StatusBadRequest,
            Message: parseValidationErrors(err),
        }
    }

    user, err := h.svc.Create(c.Context(), req)
    if err != nil {
        return err
    }

    return c.Status(fiber.StatusCreated).JSON(toUserResponse(user))
}

func (h *UserHandler) List(c *fiber.Ctx) error {
    query := dto.ListQuery{
        Page:   c.QueryInt("page", 1),
        Limit:  c.QueryInt("limit", 20),
        Search: c.Query("search"),
    }

    result, err := h.svc.List(c.Context(), query)
    if err != nil {
        return err
    }

    return c.JSON(result)
}
```

## Custom Error Handler

```go
// internal/handler/error_handler.go
func customErrorHandler(c *fiber.Ctx, err error) error {
    var fiberErr *fiber.Error
    var notFound *domain.NotFoundError
    var conflict *domain.ConflictError

    code := fiber.StatusInternalServerError
    message := "Internal server error"

    switch {
    case errors.As(err, &fiberErr):
        code = fiberErr.Code
        message = fiberErr.Message
    case errors.As(err, &notFound):
        code = fiber.StatusNotFound
        message = err.Error()
    case errors.As(err, &conflict):
        code = fiber.StatusConflict
        message = err.Error()
    default:
        log.Printf("Unhandled error: %v", err)
    }

    return c.Status(code).JSON(fiber.Map{
        "error":     message,
        "requestId": c.Locals("requestid"),
    })
}
```

## Auth Middleware

```go
// internal/middleware/auth.go
func Auth(secret string) fiber.Handler {
    return func(c *fiber.Ctx) error {
        authHeader := c.Get("Authorization")
        if !strings.HasPrefix(authHeader, "Bearer ") {
            return fiber.ErrUnauthorized
        }

        token := strings.TrimPrefix(authHeader, "Bearer ")
        claims, err := verifyToken(token, secret)
        if err != nil {
            return fiber.ErrUnauthorized
        }

        c.Locals("userID", claims.Subject)
        c.Locals("userRoles", claims.Roles)
        return c.Next()
    }
}

// Usage in handler
func (h *UserHandler) Delete(c *fiber.Ctx) error {
    userID := c.Locals("userID").(string)  // ✅ Type-safe local access
    // ...
}
```

## DTOs với go-playground/validator

```go
// internal/dto/user_dto.go
type CreateUserRequest struct {
    Email    string `json:"email"    validate:"required,email,max=255"`
    Name     string `json:"name"     validate:"required,min=2,max=100"`
    Password string `json:"password" validate:"required,min=8"`
}

type UpdateUserRequest struct {
    Name   *string `json:"name"   validate:"omitempty,min=2,max=100"`
    Avatar *string `json:"avatar" validate:"omitempty,url"`
}
```

## Anti-patterns

```go
// ❌ c.SendString() cho JSON responses
c.SendString(`{"error": "not found"}`)  // ❌ No Content-Type header
// ✅
c.Status(404).JSON(fiber.Map{"error": "not found"})

// ❌ panic trong handler (crash toàn bộ server)
func (h *Handler) Get(c *fiber.Ctx) error {
    user := getUser()
    if user == nil { panic("user is nil") }  // ❌
}
// ✅ Return fiber.Error

// ❌ Không dùng c.Context() cho downstream calls
h.svc.FindByID("123")  // ❌ Mất request context, không cancel được
h.svc.FindByID(c.Context(), "123")  // ✅

// ❌ Global validator instance không reuse
func (h *Handler) Create(c *fiber.Ctx) error {
    v := validator.New()  // ❌ Tạo mới mỗi request!
    v.Struct(req)
}
// ✅ validator.New() trong constructor, reuse
```
