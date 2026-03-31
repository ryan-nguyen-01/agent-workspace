---
name: skill-auth-rbac
description: Best practices implement Role-Based Access Control (RBAC) và Permission-Based Access Control: role hierarchy, resource permissions, guards và policy patterns.
---

# Skill: RBAC / PBAC

## Permission Model

```typescript
// ✅ PBAC (Permission-Based) — more granular than pure RBAC
// Format: action:resource hoặc action:resource:scope

const PERMISSIONS = {
  // Users
  'users:read': 'View users',
  'users:create': 'Create users',
  'users:update': 'Update users',
  'users:delete': 'Delete users',
  'users:read:own': 'View own profile only',
  'users:update:own': 'Update own profile only',

  // Posts
  'posts:read': 'View all posts',
  'posts:create': 'Create posts',
  'posts:update': 'Update any post',
  'posts:update:own': 'Update own posts only',
  'posts:delete': 'Delete any post',
  'posts:publish': 'Publish posts',

  // Admin
  'admin:access': 'Access admin panel',
} as const

type Permission = keyof typeof PERMISSIONS

// ✅ Roles với permission sets
const ROLE_PERMISSIONS: Record<string, Permission[]> = {
  super_admin: Object.keys(PERMISSIONS) as Permission[],
  admin: [
    'users:read', 'users:create', 'users:update', 'users:delete',
    'posts:read', 'posts:create', 'posts:update', 'posts:delete', 'posts:publish',
    'admin:access',
  ],
  moderator: [
    'users:read',
    'posts:read', 'posts:update', 'posts:delete', 'posts:publish',
  ],
  editor: [
    'users:read:own', 'users:update:own',
    'posts:read', 'posts:create', 'posts:update:own',
  ],
  viewer: [
    'users:read:own',
    'posts:read',
  ],
}

function getRolePermissions(role: string): Set<Permission> {
  return new Set(ROLE_PERMISSIONS[role] ?? [])
}

function hasPermission(userRoles: string[], permission: Permission): boolean {
  return userRoles.some(role => getRolePermissions(role).has(permission))
}
```

## Access Control Service

```typescript
// services/access-control.service.ts
@Injectable()
export class AccessControlService {
  can(user: AuthUser, permission: Permission, resource?: unknown): boolean {
    // 1. Check direct permission
    if (hasPermission(user.roles, permission)) return true

    // 2. Check scope (own resource)
    const ownPermission = `${permission}:own` as Permission
    if (hasPermission(user.roles, ownPermission) && resource) {
      return this.isOwner(user, resource)
    }

    return false
  }

  private isOwner(user: AuthUser, resource: { userId?: string; authorId?: string }): boolean {
    return resource.userId === user.id || resource.authorId === user.id
  }

  // ✅ Policy-based check
  async canOrThrow(user: AuthUser, permission: Permission, resource?: unknown): Promise<void> {
    if (!this.can(user, permission, resource)) {
      throw new ForbiddenException(
        `Permission denied: requires '${permission}'`
      )
    }
  }
}
```

## Guards — NestJS

```typescript
// guards/permissions.guard.ts
import { SetMetadata, CanActivate, ExecutionContext, Injectable } from '@nestjs/common'
import { Reflector } from '@nestjs/core'

export const RequirePermissions = (...permissions: Permission[]) =>
  SetMetadata('permissions', permissions)

@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private acl: AccessControlService,
  ) {}

  canActivate(context: ExecutionContext): boolean {
    const permissions = this.reflector.getAllAndOverride<Permission[]>('permissions', [
      context.getHandler(),
      context.getClass(),
    ])

    if (!permissions?.length) return true  // No permissions required

    const request = context.switchToHttp().getRequest()
    const user: AuthUser = request.user

    if (!user) return false

    return permissions.every(permission => this.acl.can(user, permission))
  }
}

// Usage in controller
@Controller('users')
@UseGuards(JwtAuthGuard, PermissionsGuard)
export class UserController {
  @Get()
  @RequirePermissions('users:read')
  findAll() { ... }

  @Delete(':id')
  @RequirePermissions('users:delete')
  delete(@Param('id') id: string) { ... }
}
```

## Middleware — Express

```typescript
// middleware/require-permissions.ts
export function requirePermissions(...permissions: Permission[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const user = req.user as AuthUser
    if (!user) {
      return next(new UnauthorizedError('Authentication required'))
    }

    const hasAll = permissions.every(p => hasPermission(user.roles, p))
    if (!hasAll) {
      return next(new ForbiddenError(`Requires permissions: ${permissions.join(', ')}`))
    }

    next()
  }
}

// Usage
router.get('/users', authenticate, requirePermissions('users:read'), handler)
router.delete('/users/:id', authenticate, requirePermissions('users:delete'), handler)
```

## Database Schema

```sql
-- ✅ Flexible permission tables
CREATE TABLE roles (
    id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE permissions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL UNIQUE,  -- 'users:delete'
    description TEXT
);

CREATE TABLE role_permissions (
    role_id       UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- ✅ Query user permissions (for caching in JWT)
SELECT DISTINCT p.name
FROM users u
JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON ur.role_id = r.id
JOIN role_permissions rp ON r.id = rp.role_id
JOIN permissions p ON rp.permission_id = p.id
WHERE u.id = $1;
```

## JWT với Embedded Permissions

```typescript
// ✅ Embed roles (not permissions) in JWT — permissions resolved server-side
interface TokenPayload {
  sub: string
  email: string
  roles: string[]    // ['admin', 'editor']
  // ✅ Don't embed all permissions — can be too large and go stale
}

// ✅ Cache permissions per role (not per user)
const permissionCache = new Map<string, Set<Permission>>()

async function getUserPermissions(roles: string[]): Promise<Set<Permission>> {
  const permissions = new Set<Permission>()
  for (const role of roles) {
    if (!permissionCache.has(role)) {
      const rolePerms = await db.getRolePermissions(role)
      permissionCache.set(role, new Set(rolePerms))
    }
    permissionCache.get(role)!.forEach(p => permissions.add(p))
  }
  return permissions
}
```

## Anti-patterns

```typescript
// ❌ Hardcode role checks (không scalable)
if (user.role === 'admin' || user.role === 'super_admin') { ... }  // ❌
// ✅ Permission-based check
if (acl.can(user, 'users:delete')) { ... }

// ❌ Frontend-only access control (bypass trivial)
{isAdmin && <DeleteButton />}  // ❌ Only UI guard, no API guard!
// ✅ Phải enforce cả ở API

// ❌ Permissions trong JWT payload (stale sau khi role thay đổi)
// ✅ Roles trong JWT, permissions từ DB/cache

// ❌ Over-privileged default role
const DEFAULT_ROLE = 'admin'  // ❌
// ✅ Principle of least privilege
const DEFAULT_ROLE = 'viewer'
```
