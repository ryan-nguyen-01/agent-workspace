---
name: skill-lang-python
description: Best practices viết Python hiện đại (3.11+): type hints, dataclasses, async/await, error handling và clean code patterns.
---

# Skill: Python (3.11+)

## Type Hints — Bắt buộc

```python
# ✅ Luôn annotate function signatures
def find_user(user_id: str) -> User | None:
    return db.users.get(user_id)

# ✅ Python 3.10+ union syntax
def process(value: int | str | None) -> str:
    return str(value) if value is not None else ""

# ✅ TypeAlias cho complex types
from typing import TypeAlias
UserId: TypeAlias = str
UserMap: TypeAlias = dict[UserId, User]
```

## Dataclasses & Pydantic

```python
# ✅ Dataclass cho internal data
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: str
    email: str
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

# ✅ Frozen dataclass cho immutable data
@dataclass(frozen=True)
class UserId:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("UserId cannot be empty")

# ✅ Pydantic cho request/response validation
from pydantic import BaseModel, EmailStr, field_validator

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    password: str

    @field_validator('name')
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be blank')
        return v.strip()
```

## Error Handling

```python
# ✅ Custom exception hierarchy
class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(
            message=f"{resource} with id '{id}' not found",
            code="NOT_FOUND",
            status_code=404
        )

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation failed for '{field}': {message}",
            code="VALIDATION_ERROR",
            status_code=422
        )

# ✅ Contextlib suppress cho expected errors
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove(temp_file)
```

## Async/Await

```python
# ✅ Async functions rõ ràng
async def get_user(user_id: str) -> User:
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise NotFoundError("User", user_id)
    return User(**user)

# ✅ Chạy parallel với asyncio.gather
async def get_user_with_profile(user_id: str) -> tuple[User, Profile]:
    user, profile = await asyncio.gather(
        get_user(user_id),
        get_profile(user_id)
    )
    return user, profile

# ✅ Async context manager
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()
```

## Naming Conventions

```
Modules/files:  snake_case      user_service.py, auth_handler.py
Classes:        PascalCase      UserService, OrderRepository
Functions:      snake_case      find_user_by_id, create_order
Constants:      UPPER_SNAKE     MAX_RETRY_COUNT, DEFAULT_TIMEOUT
Private:        _prefix         _validate_email, _hash_password
Protected:      _prefix         (Python không có true private)
Type aliases:   PascalCase      UserId, UserMap
```

## Context Managers

```python
# ✅ Custom context manager
from contextlib import contextmanager

@contextmanager
def db_transaction():
    tx = db.begin()
    try:
        yield tx
        tx.commit()
    except Exception:
        tx.rollback()
        raise

# Usage
with db_transaction() as tx:
    tx.users.insert(user)
    tx.profiles.insert(profile)
```

## List Comprehensions vs Loops

```python
# ✅ Simple transformation → comprehension
emails = [user.email for user in users if user.is_active]

# ✅ Complex logic → explicit loop (readability first)
results = []
for user in users:
    if await user.has_permission('admin'):
        profile = await fetch_profile(user.id)
        results.append(UserWithProfile(user, profile))

# ❌ Nested comprehensions khó đọc → dùng loop
# [x for xs in matrix for x in xs if x > 0]  # khó đọc
```

## Imports chuẩn

```python
# Thứ tự: stdlib → third-party → local
import os
import sys
from datetime import datetime
from typing import Optional

import fastapi
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth import AuthService
```
