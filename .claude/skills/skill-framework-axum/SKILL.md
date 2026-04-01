---
name: skill-framework-axum
description: Best practices xây dựng REST APIs với Axum (Rust) — routing, extractors, middleware, state, error handling và production patterns.
---

# Skill: Axum

## Khi nào dùng

- REST API Rust cần hiệu năng cao, memory safety
- Integration với Tokio async ecosystem
- Muốn type-safe routing + extractors

---

## Project structure

```
src/
  main.rs
  app.rs              # Router setup, state wiring
  routes/
    mod.rs
    users.rs
    auth.rs
  handlers/
    user_handler.rs
  services/
    user_service.rs
  repositories/
    user_repo.rs
  models/
    user.rs
  errors.rs           # AppError type
  state.rs            # AppState
```

---

## App setup

```rust
use axum::{Router, middleware};
use std::sync::Arc;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();

    let state = Arc::new(AppState::new().await?);

    let app = Router::new()
        .merge(routes::users::router())
        .merge(routes::auth::router())
        .layer(middleware::from_fn(tracing_middleware))
        .with_state(state);

    let listener = TcpListener::bind("0.0.0.0:3000").await?;
    tracing::info!("Listening on {}", listener.local_addr()?);
    axum::serve(listener, app).await?;

    Ok(())
}
```

---

## State

```rust
// state.rs
use sqlx::PgPool;
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub db: PgPool,
    pub config: Arc<Config>,
}

impl AppState {
    pub async fn new() -> anyhow::Result<Self> {
        let db = PgPool::connect(&std::env::var("DATABASE_URL")?).await?;
        sqlx::migrate!().run(&db).await?;

        Ok(Self {
            db,
            config: Arc::new(Config::from_env()?),
        })
    }
}
```

---

## Routes & Handlers

```rust
// routes/users.rs
use axum::{Router, routing::{get, post}, extract::{State, Path, Json}, http::StatusCode};
use std::sync::Arc;

pub fn router() -> Router<Arc<AppState>> {
    Router::new()
        .route("/users", post(create_user))
        .route("/users/:id", get(get_user))
        .route("/users/:id", put(update_user).delete(delete_user))
}

async fn get_user(
    State(state): State<Arc<AppState>>,
    Path(id): Path<uuid::Uuid>,
) -> Result<Json<UserResponse>, AppError> {
    let user = state.db
        .get_user(id)
        .await?
        .ok_or(AppError::NotFound(format!("User {id}")))?;

    Ok(Json(UserResponse::from(user)))
}

async fn create_user(
    State(state): State<Arc<AppState>>,
    Json(body): Json<CreateUserRequest>,
) -> Result<(StatusCode, Json<UserResponse>), AppError> {
    body.validate()?;
    let user = state.db.create_user(body).await?;
    Ok((StatusCode::CREATED, Json(UserResponse::from(user))))
}
```

---

## Error handling

```rust
// errors.rs
use axum::{response::{IntoResponse, Response}, http::StatusCode, Json};
use serde_json::json;

#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Validation error: {0}")]
    Validation(String),

    #[error("Unauthorized")]
    Unauthorized,

    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("Internal error: {0}")]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            AppError::NotFound(msg) => (StatusCode::NOT_FOUND, msg.clone()),
            AppError::Validation(msg) => (StatusCode::BAD_REQUEST, msg.clone()),
            AppError::Unauthorized => (StatusCode::UNAUTHORIZED, "Unauthorized".into()),
            AppError::Database(e) => {
                tracing::error!("DB error: {e}");
                (StatusCode::INTERNAL_SERVER_ERROR, "Database error".into())
            }
            AppError::Internal(e) => {
                tracing::error!("Internal error: {e}");
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error".into())
            }
        };

        (status, Json(json!({ "error": message }))).into_response()
    }
}
```

---

## Middleware

```rust
use axum::{middleware::Next, extract::Request, response::Response};

// Auth middleware
pub async fn auth_middleware(
    State(state): State<Arc<AppState>>,
    mut request: Request,
    next: Next,
) -> Result<Response, AppError> {
    let token = request
        .headers()
        .get("Authorization")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .ok_or(AppError::Unauthorized)?;

    let claims = verify_jwt(token, &state.config.jwt_secret)
        .map_err(|_| AppError::Unauthorized)?;

    request.extensions_mut().insert(claims);
    Ok(next.run(request).await)
}

// Apply to route group
let protected = Router::new()
    .route("/me", get(get_me))
    .layer(middleware::from_fn_with_state(state.clone(), auth_middleware));
```

---

## Validation

```rust
use serde::Deserialize;
use validator::Validate;

#[derive(Debug, Deserialize, Validate)]
pub struct CreateUserRequest {
    #[validate(email)]
    pub email: String,

    #[validate(length(min = 1, max = 100))]
    pub name: String,

    #[validate(length(min = 8))]
    pub password: String,
}

impl CreateUserRequest {
    pub fn validate(&self) -> Result<(), AppError> {
        Validate::validate(self)
            .map_err(|e| AppError::Validation(e.to_string()))
    }
}
```

---

## Key dependencies (Cargo.toml)

```toml
[dependencies]
axum = { version = "0.7", features = ["macros"] }
tokio = { version = "1", features = ["full"] }
tower = "0.4"
tower-http = { version = "0.5", features = ["cors", "trace", "compression-gzip"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio", "uuid", "chrono"] }
uuid = { version = "1", features = ["v4", "serde"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
thiserror = "1"
anyhow = "1"
validator = { version = "0.18", features = ["derive"] }
jsonwebtoken = "9"
```

---

## Testing

```rust
#[cfg(test)]
mod tests {
    use axum::http::{Request, StatusCode};
    use tower::ServiceExt;

    #[tokio::test]
    async fn test_create_user() {
        let app = build_test_app().await;

        let response = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/users")
                    .header("Content-Type", "application/json")
                    .body(r#"{"email":"test@test.com","name":"Test","password":"secret123"}"#.into())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::CREATED);
    }
}
```

---

## Performance checklist

- ✅ Dùng `Arc<AppState>` — clone cheap, share state
- ✅ Connection pooling với `sqlx::PgPool`
- ✅ `tower-http` compression + trace layers
- ✅ Avoid blocking in async context — dùng `tokio::task::spawn_blocking`
- ✅ Stream large responses thay vì buffer toàn bộ
