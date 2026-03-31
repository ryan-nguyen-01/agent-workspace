---
name: skill-framework-nestjs
description: Best practices xây dựng NestJS applications: module structure, dependency injection, pipes, guards, interceptors, exception filters và performance patterns.
---

# Skill: NestJS

## Module Structure chuẩn

```typescript
// ✅ Feature module — encapsulate everything
@Module({
  imports: [TypeOrmModule.forFeature([User]), JwtModule],
  controllers: [UserController],
  providers: [UserService, UserRepository],
  exports: [UserService],  // chỉ export những gì module khác cần
})
export class UserModule {}
```

## Controller — Thin, chỉ handle HTTP

```typescript
@Controller('users')
@UseGuards(JwtAuthGuard)
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Get(':id')
  @HttpCode(HttpStatus.OK)
  async findOne(@Param('id', ParseUUIDPipe) id: string): Promise<UserResponseDto> {
    return this.userService.findById(id)
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async create(@Body() dto: CreateUserDto): Promise<UserResponseDto> {
    return this.userService.create(dto)
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  async remove(@Param('id', ParseUUIDPipe) id: string): Promise<void> {
    await this.userService.delete(id)
  }
}
```

## DTO Validation với class-validator

```typescript
import { IsEmail, IsString, MinLength, IsOptional, IsEnum } from 'class-validator'
import { Transform, Type } from 'class-transformer'

export class CreateUserDto {
  @IsEmail()
  email: string

  @IsString()
  @MinLength(2)
  @Transform(({ value }) => value?.trim())
  name: string

  @IsString()
  @MinLength(8)
  password: string
}

export class PaginationDto {
  @IsOptional()
  @Type(() => Number)
  @Min(1)
  page?: number = 1

  @IsOptional()
  @Type(() => Number)
  @Max(100)
  limit?: number = 20
}
```

## Service — Business Logic

```typescript
@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    private readonly passwordService: PasswordService,
    private readonly eventEmitter: EventEmitter2,
  ) {}

  async create(dto: CreateUserDto): Promise<UserResponseDto> {
    const exists = await this.userRepository.existsBy({ email: dto.email })
    if (exists) throw new ConflictException('Email already registered')

    const hashedPassword = await this.passwordService.hash(dto.password)
    const user = this.userRepository.create({ ...dto, password: hashedPassword })
    const saved = await this.userRepository.save(user)

    this.eventEmitter.emit('user.created', new UserCreatedEvent(saved))
    return plainToInstance(UserResponseDto, saved)
  }

  async findById(id: string): Promise<UserResponseDto> {
    const user = await this.userRepository.findOneBy({ id })
    if (!user) throw new NotFoundException(`User ${id} not found`)
    return plainToInstance(UserResponseDto, user)
  }
}
```

## Guards

```typescript
// ✅ JWT Guard
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  handleRequest<T>(err: Error, user: T): T {
    if (err || !user) throw err ?? new UnauthorizedException()
    return user
  }
}

// ✅ Role Guard
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const roles = this.reflector.getAllAndOverride<Role[]>('roles', [
      context.getHandler(),
      context.getClass(),
    ])
    if (!roles) return true

    const { user } = context.switchToHttp().getRequest()
    return roles.some(role => user.roles?.includes(role))
  }
}
```

## Exception Filter

```typescript
@Catch()
@Injectable()
export class GlobalExceptionFilter implements ExceptionFilter {
  constructor(private readonly logger: Logger) {}

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp()
    const response = ctx.getResponse<Response>()
    const request = ctx.getRequest<Request>()

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR

    const message = exception instanceof HttpException
      ? exception.message
      : 'Internal server error'

    if (status >= 500) {
      this.logger.error('Unhandled exception', { exception, path: request.url })
    }

    response.status(status).json({
      statusCode: status,
      message,
      timestamp: new Date().toISOString(),
      path: request.url,
    })
  }
}
```

## Interceptors

```typescript
// ✅ Response transform interceptor
@Injectable()
export class TransformInterceptor<T>
  implements NestInterceptor<T, ApiResponse<T>> {

  intercept(context: ExecutionContext, next: CallHandler): Observable<ApiResponse<T>> {
    return next.handle().pipe(
      map(data => ({ success: true, data, timestamp: new Date().toISOString() }))
    )
  }
}

// ✅ Logging interceptor
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const req = context.switchToHttp().getRequest()
    const start = Date.now()

    return next.handle().pipe(
      tap(() => console.log(`${req.method} ${req.url} — ${Date.now() - start}ms`))
    )
  }
}
```

## Config Module

```typescript
// ✅ Typed config với validation
@Injectable()
export class AppConfig {
  constructor(private configService: ConfigService) {}

  get databaseUrl(): string {
    return this.configService.getOrThrow<string>('DATABASE_URL')
  }

  get jwtSecret(): string {
    return this.configService.getOrThrow<string>('JWT_SECRET')
  }

  get port(): number {
    return this.configService.get<number>('PORT', 3000)
  }
}
```

## Anti-patterns

```typescript
// ❌ Logic trong controller
@Get(':id')
async findOne(@Param('id') id: string) {
  const user = await this.db.query('SELECT * FROM users WHERE id = $1', [id])
  return user // Không filter sensitive fields!
}

// ❌ Circular dependencies
// UserModule imports AuthModule, AuthModule imports UserModule → crash

// ❌ Không dùng forwardRef() khi cần circular (dùng event emitter thay thế)
// ❌ Global state trong service (service là singleton — thread-safe issue)
```
