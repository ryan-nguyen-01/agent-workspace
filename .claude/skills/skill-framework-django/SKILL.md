---
name: skill-framework-django
description: Best practices xây dựng Django/DRF applications: models, serializers, views, permissions, authentication và project structure chuẩn.
---

# Skill: Django + Django REST Framework

## Project Structure

```
project/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── users/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── services.py
│       ├── permissions.py
│       └── tests/
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

## Models

```python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email: str, name: str, password: str) -> 'User':
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        indexes = [models.Index(fields=['email'])]

    def __str__(self) -> str:
        return self.email
```

## Serializers

```python
from rest_framework import serializers
from .models import User

# ✅ Request serializer — validation
class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(min_length=2, max_length=100)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered')
        return value.lower()

# ✅ Response serializer — controlled output
class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'created_at']
        read_only_fields = fields
```

## Views — Class-Based

```python
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import CreateUserSerializer, UserResponseSerializer
from .services import UserService

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id: str) -> Response:
        user = UserService.find_by_id(user_id)
        return Response(UserResponseSerializer(user).data)

    def delete(self, request, user_id: str) -> Response:
        UserService.delete(user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # ✅ Auto 400 on invalid
        user = UserService.create(**serializer.validated_data)
        return Response(
            UserResponseSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
```

## ViewSets (CRUD resources)

```python
from rest_framework import viewsets, mixins
from rest_framework.decorators import action

class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,  # ✅ Không inherit ModelViewSet toàn bộ
):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserResponseSerializer

    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        user = self.get_object()
        UserService.deactivate(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
```

## Service Layer

```python
# services.py
from django.shortcuts import get_object_or_404
from .models import User

class UserService:
    @staticmethod
    def find_by_id(user_id: str) -> User:
        return get_object_or_404(User, id=user_id, is_active=True)

    @staticmethod
    def create(email: str, name: str, password: str) -> User:
        return User.objects.create_user(email=email, name=name, password=password)

    @staticmethod
    def delete(user_id: str) -> None:
        user = get_object_or_404(User, id=user_id)
        user.delete()
```

## Settings chuẩn

```python
# config/settings/base.py
from pathlib import Path
from environs import Env

env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env.str('SECRET_KEY')
DEBUG = env.bool('DEBUG', False)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'corsheaders',
    'apps.users',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}
```

## Exception Handler

```python
# config/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': response.data.get('detail', str(response.data)),
            'status_code': response.status_code,
        }

    return response
```

## Anti-patterns

```python
# ❌ Logic trong view
def create_user(request):
    user = User(email=request.data['email'])
    user.password = request.data['password']  # Không hash!
    user.save()

# ❌ Truy vấn trong loop (N+1)
for user in User.objects.all():
    print(user.profile.bio)  # N+1 query!

# ✅ select_related / prefetch_related
users = User.objects.select_related('profile').all()

# ❌ Dùng ModelSerializer cho input validation
# ModelSerializer expose tất cả fields — dùng Serializer riêng cho input
```
