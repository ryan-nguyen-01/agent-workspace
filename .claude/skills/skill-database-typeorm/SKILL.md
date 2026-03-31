---
name: skill-database-typeorm
description: Best practices dùng TypeORM với TypeScript: entity design, repositories, migrations, relations và query builder patterns.
---

# Skill: TypeORM

## Entity Design

```typescript
// entities/user.entity.ts
import {
  Entity, PrimaryGeneratedColumn, Column, CreateDateColumn,
  UpdateDateColumn, DeleteDateColumn, Index, OneToMany,
} from 'typeorm'

@Entity('users')
@Index(['email'], { unique: true })
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string

  @Column({ type: 'varchar', length: 255 })
  email: string

  @Column({ type: 'varchar', length: 100 })
  name: string

  @Column({ type: 'varchar', select: false })  // ✅ Không trả về mặc định
  password: string

  @Column({ type: 'boolean', default: true })
  isActive: boolean

  @Column({ type: 'enum', enum: UserRole, default: UserRole.USER })
  role: UserRole

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date

  @DeleteDateColumn({ type: 'timestamptz', nullable: true })  // ✅ Soft delete
  deletedAt: Date | null

  @OneToMany(() => Post, post => post.author)
  posts: Post[]

  // ✅ Factory method thay vì constructor
  static create(email: string, name: string, hashedPassword: string): User {
    const user = new User()
    user.email = email
    user.name = name
    user.password = hashedPassword
    return user
  }
}
```

## DataSource Setup

```typescript
// database/datasource.ts
import { DataSource } from 'typeorm'

export const AppDataSource = new DataSource({
  type: 'postgres',
  url: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: true } : false,
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],
  migrations: [__dirname + '/migrations/*{.ts,.js}'],
  synchronize: false,          // ✅ NEVER true in production
  logging: process.env.NODE_ENV === 'development',
  poolSize: 20,
  connectTimeoutMS: 5000,
  extra: {
    idleTimeoutMillis: 30000,
  },
})

// Initialize
await AppDataSource.initialize()
```

## Repository Pattern

```typescript
// repositories/user.repository.ts
import { Repository, DataSource } from 'typeorm'
import { Injectable } from '@nestjs/common'
import { InjectRepository } from '@nestjs/typeorm'

@Injectable()
export class UserRepository {
  constructor(
    @InjectRepository(User)
    private readonly repo: Repository<User>,
  ) {}

  async findById(id: string): Promise<User | null> {
    return this.repo.findOne({
      where: { id },
      select: {
        id: true, email: true, name: true, role: true, createdAt: true,
      },
    })
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.repo
      .createQueryBuilder('user')
      .addSelect('user.password')  // ✅ Explicitly include password only when needed
      .where('user.email = :email', { email })
      .getOne()
  }

  async findPaginated(page: number, limit: number, filters?: {
    search?: string
    role?: UserRole
    isActive?: boolean
  }): Promise<[User[], number]> {
    const qb = this.repo.createQueryBuilder('user')

    if (filters?.search) {
      qb.andWhere('(user.name ILIKE :search OR user.email ILIKE :search)', {
        search: `%${filters.search}%`,
      })
    }
    if (filters?.role) qb.andWhere('user.role = :role', { role: filters.role })
    if (filters?.isActive !== undefined) {
      qb.andWhere('user.isActive = :isActive', { isActive: filters.isActive })
    }

    return qb
      .orderBy('user.createdAt', 'DESC')
      .skip((page - 1) * limit)
      .take(limit)
      .getManyAndCount()
  }
}
```

## Query Builder

```typescript
// ✅ Complex joins với query builder
const usersWithStats = await AppDataSource
  .createQueryBuilder(User, 'user')
  .leftJoin('user.posts', 'post', 'post.status = :status', { status: 'published' })
  .leftJoin('user.profile', 'profile')
  .select([
    'user.id', 'user.name', 'user.email',
    'profile.bio', 'profile.avatarUrl',
  ])
  .addSelect('COUNT(post.id)', 'postCount')
  .where('user.isActive = :isActive', { isActive: true })
  .groupBy('user.id')
  .addGroupBy('profile.id')
  .orderBy('postCount', 'DESC')
  .limit(10)
  .getRawAndEntities()
```

## Transactions

```typescript
// ✅ Transactions với QueryRunner
async transfer(fromId: string, toId: string, amount: number): Promise<void> {
  const queryRunner = AppDataSource.createQueryRunner()
  await queryRunner.connect()
  await queryRunner.startTransaction()

  try {
    const from = await queryRunner.manager.findOneOrFail(Account, {
      where: { id: fromId },
      lock: { mode: 'pessimistic_write' },  // ✅ Row lock
    })

    if (from.balance < amount) throw new Error('Insufficient balance')

    await queryRunner.manager.decrement(Account, { id: fromId }, 'balance', amount)
    await queryRunner.manager.increment(Account, { id: toId }, 'balance', amount)

    await queryRunner.commitTransaction()
  } catch (err) {
    await queryRunner.rollbackTransaction()
    throw err
  } finally {
    await queryRunner.release()
  }
}
```

## Migrations

```bash
# ✅ Generate migration từ entity changes
npx typeorm migration:generate src/database/migrations/AddUserRole -d src/database/datasource.ts

# Run migrations
npx typeorm migration:run -d src/database/datasource.ts

# Revert last migration
npx typeorm migration:revert -d src/database/datasource.ts
```

## Anti-patterns

```typescript
// ❌ synchronize: true trong production (drop + recreate tables!)
// ✅ Chỉ dùng migrations

// ❌ Eager loading mặc định (N+1)
@OneToMany(() => Post, post => post.author, { eager: true })  // ❌
// ✅ Lazy load hoặc explicit join khi cần

// ❌ Repository trong Service dùng .save() cho updates (re-reads all fields)
await this.repo.save({ id, name: 'new name' })  // Re-fetches toàn bộ entity!
// ✅ .update() cho partial updates
await this.repo.update(id, { name: 'new name' })

// ❌ Không release QueryRunner
const qr = dataSource.createQueryRunner()
await qr.startTransaction()
// ... crash → connection leak!
// ✅ try/finally với qr.release()
```
