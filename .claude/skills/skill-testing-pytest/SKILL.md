---
name: skill-testing-pytest
description: Best practices viết tests với pytest: fixtures, parametrize, mocking với unittest.mock, async tests và test organization.
---

# Skill: pytest Testing

## Test Structure

```python
# tests/services/test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.user_service import UserService
from app.exceptions import NotFoundError, ConflictError
from tests.factories import build_user, build_create_user_dto

class TestUserService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_repo = MagicMock()
        self.service = UserService(self.mock_repo)

    def test_find_by_id_returns_user_when_found(self):
        user = build_user(id='123')
        self.mock_repo.find_by_id.return_value = user

        result = self.service.find_by_id('123')

        assert result == user
        self.mock_repo.find_by_id.assert_called_once_with('123')

    def test_find_by_id_raises_not_found_when_missing(self):
        self.mock_repo.find_by_id.return_value = None

        with pytest.raises(NotFoundError, match="User '999' not found"):
            self.service.find_by_id('999')
```

## Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base

@pytest.fixture(scope='session')
def engine():
    engine = create_engine('postgresql://test:test@localhost/test_db')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')  # ✅ Function scope = isolated per test
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()  # ✅ Rollback sau mỗi test — không cleanup cần thiết
    connection.close()

@pytest.fixture
def user_service(db_session):
    from app.repositories.user_repo import UserRepository
    repo = UserRepository(db_session)
    return UserService(repo)
```

## Test Factories

```python
# tests/factories.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from faker import Faker

fake = Faker()

def build_user(**overrides):
    defaults = {
        'id': str(uuid.uuid4()),
        'email': fake.email(),
        'name': fake.name(),
        'is_active': True,
        'created_at': datetime.utcnow(),
    }
    return {**defaults, **overrides}

def build_create_user_dto(**overrides):
    defaults = {
        'email': fake.email(),
        'name': fake.name(),
        'password': 'Password123!',
    }
    return {**defaults, **overrides}
```

## Parametrize

```python
@pytest.mark.parametrize('email,expected_error', [
    ('', 'Email is required'),
    ('not-an-email', 'Invalid email format'),
    ('a' * 256 + '@test.com', 'Email too long'),
])
def test_create_user_validates_email(user_service, email, expected_error):
    dto = build_create_user_dto(email=email)

    with pytest.raises(ValidationError, match=expected_error):
        user_service.create(dto)

@pytest.mark.parametrize('role,can_access', [
    ('admin', True),
    ('user', False),
    ('moderator', True),
])
def test_admin_access(role, can_access):
    user = build_user(role=role)
    assert check_admin_access(user) == can_access
```

## Async Tests

```python
import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_async_find_user():
    mock_repo = AsyncMock()
    mock_repo.find_by_id.return_value = build_user()
    service = AsyncUserService(mock_repo)

    result = await service.find_by_id('123')

    assert result is not None
    mock_repo.find_by_id.assert_awaited_once_with('123')

# ✅ Async fixture
@pytest_asyncio.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client
```

## Mocking

```python
# ✅ patch decorator
@patch('app.services.email_service.send_welcome_email')
def test_create_sends_email(mock_send, user_service):
    user_service.create(build_create_user_dto())
    mock_send.assert_called_once()

# ✅ patch context manager
def test_external_api_failure():
    with patch('app.clients.payment_client.charge') as mock_charge:
        mock_charge.side_effect = ConnectionError('API down')

        with pytest.raises(PaymentError):
            service.process_payment(order_id='123', amount=100)

# ✅ MagicMock side_effect cho sequence
mock_repo.find_by_id.side_effect = [None, build_user(), build_user()]
# First call → None, second → user, third → user
```

## HTTP Integration Tests (FastAPI)

```python
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

@pytest.fixture
def client(app):
    return TestClient(app)

def test_create_user_returns_201(client, db_session):
    response = client.post('/api/v1/users', json={
        'email': 'test@test.com',
        'name': 'Test User',
        'password': 'Password123!',
    })

    assert response.status_code == 201
    data = response.json()
    assert data['email'] == 'test@test.com'
    assert 'password' not in data

def test_create_user_409_when_email_exists(client, db_session):
    dto = {'email': 'existing@test.com', 'name': 'User', 'password': 'pass12345'}
    client.post('/api/v1/users', json=dto)  # Create first

    response = client.post('/api/v1/users', json=dto)  # Duplicate

    assert response.status_code == 409
```

## pytest.ini / pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
markers = [
    "integration: marks tests as integration (deselect with '-m not integration')",
    "slow: marks tests as slow",
]
```

## Anti-patterns

```python
# ❌ Test nhiều behaviors — mỗi test 1 behavior
def test_user_service():
    # create, find, delete... ❌

# ❌ Hard-coded test data
user = User(id='abc123', email='john@test.com')  # Non-descriptive, brittle

# ❌ Không cleanup side effects
def test_creates_file():
    service.export('output.csv')
    assert os.path.exists('output.csv')
    # ❌ File còn đó sau test! Dùng tmp_path fixture

# ✅ tmp_path fixture
def test_creates_file(tmp_path):
    output = tmp_path / 'output.csv'
    service.export(str(output))
    assert output.exists()
```
