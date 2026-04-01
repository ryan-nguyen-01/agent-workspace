---
name: skill-lang-csharp
description: Best practices viết C# hiện đại (.NET 8+) — records, nullable reference types, async/await, LINQ, patterns matching và clean code principles.
---

# Skill: C# (.NET 8+)

## Records (Immutable data)

```csharp
// ✅ Record — immutable value type với value equality
public record User(
    Guid Id,
    string Email,
    string Name,
    DateTime CreatedAt
);

// ✅ Record struct (value type)
public readonly record struct Money(decimal Amount, string Currency);

// ✅ Non-destructive mutation
var updated = user with { Name = "New Name" };

// ✅ Deconstruction
var (id, email, name, _) = user;
```

---

## Nullable Reference Types

```csharp
// Enable in csproj
// <Nullable>enable</Nullable>

// ✅ Explicit nullable
string? name = null;
string nonNullable = "required";  // Compile warning nếu assign null

// ✅ Null coalescing
string display = name ?? "Anonymous";
int length = name?.Length ?? 0;

// ✅ Null-conditional
user?.Profile?.Bio?.Length;

// ✅ Null-forgiving (dùng cẩn thận)
string value = GetValue()!; // Assert not null
```

---

## Pattern Matching

```csharp
// ✅ switch expression (C# 8+)
string Label(Shape shape) => shape switch
{
    Circle { Radius: > 100 } => "Large circle",
    Circle c => $"Circle r={c.Radius}",
    Rectangle { Width: var w, Height: var h } => $"Rect {w}×{h}",
    _ => "Unknown shape",
};

// ✅ Property pattern
if (user is { IsActive: true, Role: "admin" })
{
    // ...
}

// ✅ List pattern (C# 11)
int[] arr = [1, 2, 3];
if (arr is [1, .., 3]) Console.WriteLine("Starts with 1, ends with 3");
```

---

## Async/Await

```csharp
// ✅ Async all the way down
public async Task<User?> GetUserAsync(Guid id, CancellationToken ct = default)
{
    return await _repo.FindByIdAsync(id, ct);
}

// ✅ ConfigureAwait(false) trong library code
await SomeOperationAsync().ConfigureAwait(false);

// ✅ Parallel concurrent
var user = await GetUserAsync(id, ct);
var ordersTask = GetOrdersAsync(id, ct);
var productsTask = GetProductsAsync(ct);
await Task.WhenAll(ordersTask, productsTask);

// ✅ ValueTask cho hot paths (nếu thường synchronous)
public ValueTask<User?> GetFromCacheAsync(string key) { ... }

// ✅ IAsyncEnumerable — async stream
public async IAsyncEnumerable<User> GetAllUsersAsync(
    [EnumeratorCancellation] CancellationToken ct = default)
{
    await foreach (var user in _repo.StreamUsersAsync(ct))
        yield return user;
}
```

---

## LINQ

```csharp
// ✅ Fluent LINQ
var activeAdmins = users
    .Where(u => u.IsActive && u.Role == "admin")
    .OrderBy(u => u.Name)
    .Select(u => new { u.Id, u.Name, u.Email })
    .ToList();

// ✅ GroupBy
var byRole = users
    .GroupBy(u => u.Role)
    .ToDictionary(g => g.Key, g => g.ToList());

// ✅ async LINQ (EF Core)
var users = await context.Users
    .Where(u => u.IsActive)
    .OrderBy(u => u.CreatedAt)
    .Take(20)
    .ToListAsync(ct);
```

---

## Result Pattern

```csharp
// ✅ Result<T> pattern (thay exceptions cho business errors)
public readonly record struct Result<T>
{
    private readonly T? _value;
    private readonly string? _error;

    private Result(T value) { _value = value; IsSuccess = true; }
    private Result(string error) { _error = error; IsSuccess = false; }

    public bool IsSuccess { get; }
    public T Value => IsSuccess ? _value! : throw new InvalidOperationException();
    public string Error => !IsSuccess ? _error! : throw new InvalidOperationException();

    public static Result<T> Ok(T value) => new(value);
    public static Result<T> Fail(string error) => new(error);
}

// Usage
var result = await _service.CreateUserAsync(dto, ct);
if (!result.IsSuccess)
    return BadRequest(result.Error);
return Ok(result.Value);
```

---

## Dependency Injection

```csharp
// ✅ DI registration (Program.cs)
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();

// ✅ Constructor injection (preferred)
public class UserService(
    IUserRepository repo,
    ICacheService cache,
    ILogger<UserService> logger) : IUserService
{
    public async Task<User?> GetByIdAsync(Guid id, CancellationToken ct)
    {
        var cached = await cache.GetAsync<User>($"user:{id}");
        if (cached is not null) return cached;

        var user = await repo.FindByIdAsync(id, ct);
        if (user is not null)
            await cache.SetAsync($"user:{id}", user, TimeSpan.FromMinutes(5));

        return user;
    }
}
```

---

## Exception handling

```csharp
// ✅ Custom exceptions
public class NotFoundException(string message) : Exception(message);
public class ValidationException(IEnumerable<string> errors)
    : Exception(string.Join("; ", errors))
{
    public IEnumerable<string> Errors { get; } = errors;
}

// ✅ Global exception handler (ASP.NET Core)
app.UseExceptionHandler(exceptionApp =>
{
    exceptionApp.Run(async context =>
    {
        var feature = context.Features.Get<IExceptionHandlerFeature>();
        var (status, message) = feature?.Error switch
        {
            NotFoundException e => (404, e.Message),
            ValidationException e => (400, e.Message),
            UnauthorizedAccessException => (401, "Unauthorized"),
            _ => (500, "Internal Server Error"),
        };

        context.Response.StatusCode = status;
        await context.Response.WriteAsJsonAsync(new { error = message });
    });
});
```

---

## Interfaces & Generics

```csharp
public interface IRepository<TEntity, TKey>
    where TEntity : class
{
    Task<TEntity?> FindByIdAsync(TKey id, CancellationToken ct = default);
    Task<TEntity> SaveAsync(TEntity entity, CancellationToken ct = default);
    Task DeleteAsync(TKey id, CancellationToken ct = default);
    IAsyncEnumerable<TEntity> GetAllAsync(CancellationToken ct = default);
}
```

---

## Idioms checklist

- ✅ Prefer `record` cho DTOs và value objects
- ✅ Enable `<Nullable>enable</Nullable>` trong csproj
- ✅ `async/await` phải propagate qua toàn bộ call chain
- ✅ Dùng `CancellationToken` trong mọi async method
- ✅ LINQ thay manual loops
- ✅ `using` statement cho IDisposable
- ✅ `is not null` thay `!= null`
- ✅ Primary constructor (C# 12) cho ngắn gọn
