---
name: skill-framework-fastapi
description: Best practices xây dựng FastAPI applications: routing, dependency injection, Pydantic schemas, async database, middleware và error handling.
---

# Skill: FastAPI

## Project Structure

```
app/
├── main.py               # FastAPI app instance, include routers
├── core/
│   ├── config.py         # Settings với pydantic-settings
│   ├── security.py       # Auth utilities
│   └── database.py       # DB session setup
├── api/
│   └── v1/
│       ├── router.py     # Aggregate all routers
│       └── endpoints/
│           ├── users.py
│           └── auth.py
├── models/               # SQLAlchemy ORM models
├── schemas/              # Pydantic request/response schemas
├── services/             # Business logic
└── repositories/         # Data access layer
```

## Router & Endpoints

```python
# ✅ APIRouter với prefix và tags
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    user = await service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return UserResponse.model_validate(user)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.create(body)
```

## Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime
from uuid import UUID

# ✅ Request schema — validation
class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    password: str

    @field_validator('name')
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be blank')
        return v.strip()

    @field_validator('password')
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

# ✅ Response schema — controlled output
class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2
```

## Dependency Injection

```python
# ✅ Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# ✅ Service dependency factory
def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

# ✅ Current user dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = verify_jwt_token(token)
    user = await db.get(User, payload.sub)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

## Exception Handling

```python
# ✅ Custom exception handlers
class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class NotFoundException(AppException):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} '{id}' not found", status_code=404)

# Register trong main.py
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "path": str(request.url)}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )
```

## Config với pydantic-settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 30
    debug: bool = False
    cors_origins: list[str] = []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

# Singleton
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## Middleware

```python
# ✅ Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Anti-patterns

```python
# ❌ Blocking operations trong async endpoint
@router.get("/users")
async def get_users():
    import time
    time.sleep(1)  # BLOCKS event loop!

# ✅ Dùng asyncio.sleep hoặc run_in_executor
await asyncio.sleep(1)  # Non-blocking

# ❌ Global mutable state
users_cache = {}  # Thread-unsafe, sẽ có race condition

# ❌ Không validate input
@router.get("/users/{id}")
async def get_user(id: str):  # Nên dùng UUID type để auto-validate
```
