---
name: skill-database-sqlalchemy
description: Best practices dùng SQLAlchemy 2.x với Python: models, sessions, relationships, migrations với Alembic và async patterns.
---

# Skill: SQLAlchemy 2.x

## Model Design

```python
# models/user.py
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Enum, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import uuid

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now(), nullable=False
    )

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    __table_args__ = (
        Index('ix_users_email', 'email', unique=True),
        Index('ix_users_created_at', 'created_at'),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    posts: Mapped[List['Post']] = relationship(
        'Post', back_populates='author', lazy='select'
    )

    @classmethod
    def create(cls, email: str, name: str, hashed_password: str) -> 'User':
        return cls(email=email.lower(), name=name, password=hashed_password)

    def __repr__(self) -> str:
        return f'<User id={self.id} email={self.email}>'
```

## Session Management

```python
# database/session.py
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,      # ✅ Verify connections before use
    pool_recycle=3600,        # Recycle connections every hour
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # ✅ Avoid lazy loading after commit
    autocommit=False,
    autoflush=False,
)

@asynccontextmanager
async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# FastAPI dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Repository Pattern

```python
# repositories/user_repository.py
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def find_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
    ) -> tuple[list[User], int]:
        base_query = (
            select(User)
            .where(User.deleted_at.is_(None))
        )

        if search:
            base_query = base_query.where(
                or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                )
            )

        # Total count
        count_result = await self.session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar_one()

        # Paginated results
        result = await self.session.execute(
            base_query
            .order_by(User.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        users = result.scalars().all()

        return list(users), total

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()  # ✅ Flush để get ID trước commit
        await self.session.refresh(user)
        return user

    # ✅ Load relations explicitly
    async def find_with_posts(self, user_id: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.posts))  # ✅ Eager load posts
        )
        return result.scalar_one_or_none()
```

## Transactions

```python
# ✅ Transaction trong service layer
async def transfer_funds(
    session: AsyncSession,
    from_id: str,
    to_id: str,
    amount: float,
) -> None:
    async with session.begin():  # ✅ Context manager handles commit/rollback
        from_account = await session.get(Account, from_id, with_for_update=True)
        to_account = await session.get(Account, to_id, with_for_update=True)

        if not from_account or not to_account:
            raise ValueError('Account not found')
        if from_account.balance < amount:
            raise ValueError('Insufficient balance')

        from_account.balance -= amount
        to_account.balance += amount
        # Commit happens automatically at end of `async with session.begin()`
```

## Alembic Migrations

```python
# alembic/env.py — Auto-generate migrations từ models
from app.models import Base

target_metadata = Base.metadata

# Generate migration
# alembic revision --autogenerate -m "add_user_table"
# alembic upgrade head
# alembic downgrade -1
```

## Anti-patterns

```python
# ❌ Lazy loading trong async context (DetachedInstanceError)
user = await session.get(User, user_id)
await session.close()
user.posts  # ❌ Lazy load sau khi session đóng!
# ✅ Dùng selectinload() trước khi dùng

# ❌ expire_on_commit=True (default) → lazy load sau commit
await session.commit()
print(user.email)  # ❌ Trigger lazy load!
# ✅ expire_on_commit=False trong session config

# ❌ Tạo engine mới mỗi request
engine = create_engine(url)  # Trong mỗi route handler!
# ✅ Singleton engine

# ❌ Session.add() rồi không flush/commit
session.add(user)
return user  # ID chưa được generate!
# ✅ await session.flush() để get DB-generated values
```
