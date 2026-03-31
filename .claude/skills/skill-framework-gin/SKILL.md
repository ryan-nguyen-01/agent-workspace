---
name: skill-framework-gin
description: Best practices xây dựng REST APIs với Gin framework (Go): routing, middleware, validation, error handling và project structure chuẩn.
---

# Skill: Gin (Go)

## Project Structure

```
cmd/
└── server/
    └── main.go
internal/
├── config/
│   └── config.go
├── handler/
│   ├── user_handler.go
│   └── health_handler.go
├── middleware/
│   ├── auth.go
│   ├── logger.go
│   └── recovery.go
├── service/
│   └── user_service.go
├── repository/
│   └── user_repository.go
├── domain/
│   └── user.go
└── dto/
    └── user_dto.go
```

## Router Setup

```go
// cmd/server/main.go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
    "github.com/gin-gonic/gin"
)

func main() {
    cfg := config.Load()

    if cfg.Env == "production" {
        gin.SetMode(gin.ReleaseMode)
    }

    r := gin.New()

    // ✅ Custom middleware (not gin.Default which has basic logger)
    r.Use(middleware.RequestID())
    r.Use(middleware.Logger())
    r.Use(middleware.Recovery())
    r.Use(middleware.CORS(cfg))

    // ✅ Dependency injection
    db := database.Connect(cfg)
    userRepo := repository.NewUserRepository(db)
    userSvc := service.NewUserService(userRepo)
    userHandler := handler.NewUserHandler(userSvc)

    // Routes
    api := r.Group("/api/v1")
    {
        users := api.Group("/users")
        users.GET("", middleware.Auth(cfg), userHandler.List)
        users.GET("/:id", middleware.Auth(cfg), userHandler.GetByID)
        users.POST("", userHandler.Create)
        users.PATCH("/:id", middleware.Auth(cfg), userHandler.Update)
        users.DELETE("/:id", middleware.Auth(cfg), userHandler.Delete)
    }

    // ✅ Graceful shutdown
    srv := &http.Server{Addr: ":" + cfg.Port, Handler: r}

    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatal("Server error:", err)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    srv.Shutdown(ctx)
}
```

## Handler

```go
// internal/handler/user_handler.go
package handler

type UserHandler struct {
    svc service.UserService
}

func NewUserHandler(svc service.UserService) *UserHandler {
    return &UserHandler{svc: svc}
}

func (h *UserHandler) GetByID(c *gin.Context) {
    id := c.Param("id")

    user, err := h.svc.FindByID(c.Request.Context(), id)
    if err != nil {
        handleError(c, err)
        return
    }

    c.JSON(http.StatusOK, toUserResponse(user))
}

func (h *UserHandler) Create(c *gin.Context) {
    var req dto.CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{
            "error": "Validation failed",
            "details": parseValidationErrors(err),
        })
        return
    }

    user, err := h.svc.Create(c.Request.Context(), req)
    if err != nil {
        handleError(c, err)
        return
    }

    c.JSON(http.StatusCreated, toUserResponse(user))
}

func (h *UserHandler) List(c *gin.Context) {
    var query dto.ListUsersQuery
    if err := c.ShouldBindQuery(&query); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    query.SetDefaults()

    result, err := h.svc.List(c.Request.Context(), query)
    if err != nil {
        handleError(c, err)
        return
    }

    c.JSON(http.StatusOK, result)
}
```

## DTOs với Validation

```go
// internal/dto/user_dto.go
package dto

type CreateUserRequest struct {
    Email    string `json:"email"    binding:"required,email,max=255"`
    Name     string `json:"name"     binding:"required,min=2,max=100"`
    Password string `json:"password" binding:"required,min=8"`
}

type UpdateUserRequest struct {
    Name   *string `json:"name"  binding:"omitempty,min=2,max=100"`
    Avatar *string `json:"avatar" binding:"omitempty,url"`
}

type ListUsersQuery struct {
    Page   int    `form:"page"   binding:"omitempty,min=1"`
    Limit  int    `form:"limit"  binding:"omitempty,min=1,max=100"`
    Search string `form:"search" binding:"omitempty,max=200"`
}

func (q *ListUsersQuery) SetDefaults() {
    if q.Page == 0 { q.Page = 1 }
    if q.Limit == 0 { q.Limit = 20 }
}
```

## Middleware

```go
// internal/middleware/auth.go
func Auth(cfg *config.Config) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Missing authorization"})
            return
        }

        token := strings.TrimPrefix(authHeader, "Bearer ")
        claims, err := auth.VerifyToken(token, cfg.JWTSecret)
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
            return
        }

        c.Set("userID", claims.Subject)
        c.Set("userRoles", claims.Roles)
        c.Next()
    }
}

// internal/middleware/logger.go
func Logger() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        requestID := c.GetHeader("X-Request-ID")
        if requestID == "" {
            requestID = uuid.New().String()
        }
        c.Set("requestID", requestID)
        c.Header("X-Request-ID", requestID)

        c.Next()

        log.Printf("[%s] %s %s %d %s",
            requestID,
            c.Request.Method,
            c.Request.URL.Path,
            c.Writer.Status(),
            time.Since(start),
        )
    }
}
```

## Error Handling

```go
// internal/handler/errors.go
func handleError(c *gin.Context, err error) {
    var notFound *domain.NotFoundError
    var conflict *domain.ConflictError
    var validation *domain.ValidationError

    switch {
    case errors.As(err, &notFound):
        c.JSON(http.StatusNotFound, gin.H{"error": err.Error(), "code": "NOT_FOUND"})
    case errors.As(err, &conflict):
        c.JSON(http.StatusConflict, gin.H{"error": err.Error(), "code": "CONFLICT"})
    case errors.As(err, &validation):
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error(), "code": "VALIDATION_ERROR"})
    default:
        log.Printf("Unhandled error: %v", err)
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
    }
}
```

## Anti-patterns

```go
// ❌ Global state (không testable)
var db *sql.DB  // Package-level variable

// ❌ c.JSON sau c.Abort (vẫn tiếp tục)
c.AbortWithStatus(401)
c.JSON(200, data)  // ❌ Vẫn ghi response!
// ✅ c.AbortWithStatusJSON() hoặc return sau Abort

// ❌ Không dùng ShouldBind (panic thay vì error)
c.BindJSON(&req)  // ❌ Gọi c.AbortWithError nếu fail
c.ShouldBindJSON(&req)  // ✅ Trả về error để xử lý

// ❌ Context không được pass xuống service/repo
func (h *UserHandler) Create(c *gin.Context) {
    user, err := h.svc.Create(req)  // ❌ Mất request context!
    user, err := h.svc.Create(c.Request.Context(), req)  // ✅
```
