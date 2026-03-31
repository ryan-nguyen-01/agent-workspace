---
name: skill-lang-rust
description: Best practices viết Rust: ownership, error handling với thiserror/anyhow, async với Tokio, structs/traits và project structure.
---

# Skill: Rust

## Error Handling

```rust
// ✅ thiserror cho library/domain errors
use thiserror::Error;

#[derive(Debug, Error)]
pub enum UserError {
    #[error("User '{0}' not found")]
    NotFound(String),

    #[error("Email '{0}' already exists")]
    EmailConflict(String),

    #[error("Invalid password: {0}")]
    InvalidPassword(String),

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}

// ✅ anyhow cho application/binary error handling
use anyhow::{Context, Result};

async fn run() -> Result<()> {
    let config = Config::from_env()
        .context("Failed to load configuration")?;

    let db = connect(&config.database_url).await
        .context("Failed to connect to database")?;

    serve(db).await
        .context("Server error")?;

    Ok(())
}

// ✅ ? operator + From trait
async fn find_user(id: &str, pool: &PgPool) -> Result<User, UserError> {
    sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_optional(pool)
        .await?  // sqlx::Error → UserError::Database (via From)
        .ok_or_else(|| UserError::NotFound(id.to_string()))
}
```

## Structs & Traits

```rust
// ✅ Builder pattern cho complex structs
#[derive(Debug, Clone)]
pub struct User {
    pub id: Uuid,
    pub email: String,
    pub name: String,
    pub role: Role,
    pub created_at: DateTime<Utc>,
}

impl User {
    pub fn new(email: impl Into<String>, name: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4(),
            email: email.into(),
            name: name.into(),
            role: Role::User,
            created_at: Utc::now(),
        }
    }
}

// ✅ Traits for abstraction
#[async_trait::async_trait]
pub trait UserRepository: Send + Sync {
    async fn find_by_id(&self, id: Uuid) -> Result<Option<User>, UserError>;
    async fn find_by_email(&self, email: &str) -> Result<Option<User>, UserError>;
    async fn create(&self, user: User) -> Result<User, UserError>;
    async fn delete(&self, id: Uuid) -> Result<(), UserError>;
}

// ✅ Newtype pattern cho type safety
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(Uuid);

impl UserId {
    pub fn new() -> Self { Self(Uuid::new_v4()) }
    pub fn inner(&self) -> Uuid { self.0 }
}

impl From<Uuid> for UserId {
    fn from(id: Uuid) -> Self { Self(id) }
}
```

## Async với Tokio

```rust
// ✅ Axum web server
use axum::{Router, routing::get, extract::State, Json};
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub db: Arc<PgPool>,
    pub config: Arc<Config>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let config = Config::from_env()?;
    let pool = PgPoolOptions::new()
        .max_connections(20)
        .connect(&config.database_url)
        .await?;

    let state = AppState {
        db: Arc::new(pool),
        config: Arc::new(config),
    };

    let app = Router::new()
        .route("/api/v1/users", get(list_users).post(create_user))
        .route("/api/v1/users/:id", get(get_user).delete(delete_user))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    axum::serve(listener, app).await?;
    Ok(())
}

// ✅ Handler
async fn get_user(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<Json<UserResponse>, AppError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_optional(&*state.db)
        .await
        .map_err(AppError::Database)?
        .ok_or(AppError::NotFound)?;

    Ok(Json(UserResponse::from(user)))
}

// ✅ Parallel async tasks
use tokio::join;

let (users, total) = join!(
    user_repo.find_paginated(page, limit),
    user_repo.count()
);
```

## Ownership & Borrowing Patterns

```rust
// ✅ Return references với explicit lifetimes
pub struct Cache<'a> {
    data: &'a HashMap<String, String>,
}

impl<'a> Cache<'a> {
    pub fn get(&self, key: &str) -> Option<&str> {
        self.data.get(key).map(|s| s.as_str())
    }
}

// ✅ Clone only when necessary
fn process(user: &User) -> String {  // Borrow, không clone
    format!("Processing {}", user.name)
}

fn take_ownership(user: User) -> User {  // Move
    User { name: user.name.to_uppercase(), ..user }
}

// ✅ Cow<str> cho flexible string ownership
use std::borrow::Cow;

fn normalize_email(email: &str) -> Cow<str> {
    if email.chars().all(|c| c.is_lowercase()) {
        Cow::Borrowed(email)  // No allocation needed
    } else {
        Cow::Owned(email.to_lowercase())  // Allocate only when needed
    }
}
```

## Project Structure

```
my-service/
├── src/
│   ├── main.rs           # Entry point
│   ├── config.rs         # Configuration
│   ├── error.rs          # AppError types
│   ├── domain/
│   │   ├── mod.rs
│   │   ├── user.rs       # User entity + business logic
│   │   └── repository.rs # Repository traits
│   ├── infrastructure/
│   │   ├── db/
│   │   │   └── user_repo.rs  # Concrete DB implementations
│   │   └── http/
│   │       ├── handlers/
│   │       └── middleware/
│   └── application/
│       └── user_service.rs
├── migrations/
├── tests/
│   └── integration/
└── Cargo.toml
```

## Anti-patterns

```rust
// ❌ .unwrap() / .expect() trong production code
let user = find_user(id).unwrap();  // Panic!
// ✅ Propagate với ?

// ❌ Clone để tránh borrow checker
let name = user.name.clone();  // Không cần nếu chỉ đọc
fn process(name: &str) { ... }
process(&user.name);  // ✅ Borrow thay vì clone

// ❌ String allocation không cần thiết
fn greet(name: String) -> String {  // Takes ownership
    format!("Hello, {name}")
}
// ✅
fn greet(name: &str) -> String {  // Borrow
    format!("Hello, {name}")
}

// ❌ Mutex trong async context (dùng tokio::sync::Mutex)
use std::sync::Mutex;
let data = Arc::new(Mutex::new(vec![]));  // Can deadlock with .await!
// ✅
use tokio::sync::Mutex;
```
