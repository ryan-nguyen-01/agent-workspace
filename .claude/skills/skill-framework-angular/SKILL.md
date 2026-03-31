---
name: skill-framework-angular
description: Best practices xây dựng Angular 17+ applications: standalone components, signals, services, reactive forms, HTTP client và lazy loading.
---

# Skill: Angular 17+ (Standalone + Signals)

## Component — Standalone

```typescript
// users/user-list.component.ts
import { Component, signal, computed, inject, OnInit } from '@angular/core'
import { CommonModule } from '@angular/common'
import { RouterModule } from '@angular/router'
import { UserService } from '../services/user.service'
import { UserCardComponent } from './user-card.component'

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, RouterModule, UserCardComponent],
  template: `
    <div class="user-list">
      @if (isLoading()) {
        <app-loading-spinner />
      } @else if (error()) {
        <app-error-message [error]="error()!" />
      } @else {
        @for (user of users(); track user.id) {
          <app-user-card [user]="user" (delete)="handleDelete($event)" />
        } @empty {
          <p>No users found.</p>
        }
      }
    </div>
  `,
})
export class UserListComponent implements OnInit {
  private userService = inject(UserService)

  // ✅ Signals — reactive state
  users = signal<User[]>([])
  isLoading = signal(false)
  error = signal<string | null>(null)

  activeUsers = computed(() => this.users().filter(u => u.isActive))

  ngOnInit(): void {
    this.loadUsers()
  }

  async loadUsers(): Promise<void> {
    this.isLoading.set(true)
    this.error.set(null)

    try {
      const users = await this.userService.findAll()
      this.users.set(users)
    } catch (err) {
      this.error.set('Failed to load users')
    } finally {
      this.isLoading.set(false)
    }
  }

  handleDelete(userId: string): void {
    this.users.update(users => users.filter(u => u.id !== userId))
  }
}
```

## Service

```typescript
// services/user.service.ts
import { Injectable, inject } from '@angular/core'
import { HttpClient, HttpParams } from '@angular/common/http'
import { Observable, firstValueFrom } from 'rxjs'
import { map, catchError } from 'rxjs/operators'

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient)
  private readonly baseUrl = '/api/v1/users'

  // ✅ Return Observable for streams, Promise for one-shot operations
  findAll(params?: { page?: number; search?: string }): Observable<User[]> {
    let httpParams = new HttpParams()
    if (params?.page) httpParams = httpParams.set('page', params.page)
    if (params?.search) httpParams = httpParams.set('search', params.search)

    return this.http.get<ApiResponse<User[]>>(this.baseUrl, { params: httpParams }).pipe(
      map(res => res.data),
    )
  }

  findById(id: string): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/${id}`)
  }

  create(dto: CreateUserDto): Promise<User> {
    return firstValueFrom(
      this.http.post<User>(this.baseUrl, dto)
    )
  }

  update(id: string, dto: Partial<UpdateUserDto>): Promise<User> {
    return firstValueFrom(
      this.http.patch<User>(`${this.baseUrl}/${id}`, dto)
    )
  }

  delete(id: string): Promise<void> {
    return firstValueFrom(
      this.http.delete<void>(`${this.baseUrl}/${id}`)
    )
  }
}
```

## Reactive Forms

```typescript
// components/create-user-form.component.ts
import { Component, inject, output } from '@angular/core'
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl } from '@angular/forms'

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="handleSubmit()">
      <div>
        <label>Email</label>
        <input type="email" formControlName="email" />
        @if (email.invalid && email.touched) {
          <span class="error">
            @if (email.errors?.['required']) { Email is required }
            @if (email.errors?.['email']) { Invalid email format }
          </span>
        }
      </div>

      <div>
        <label>Name</label>
        <input formControlName="name" />
      </div>

      <button type="submit" [disabled]="form.invalid || isSubmitting()">
        {{ isSubmitting() ? 'Creating...' : 'Create User' }}
      </button>
    </form>
  `,
})
export class CreateUserFormComponent {
  private fb = inject(FormBuilder)
  private userService = inject(UserService)

  created = output<User>()
  isSubmitting = signal(false)

  form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    name: ['', [Validators.required, Validators.minLength(2)]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  })

  get email(): AbstractControl { return this.form.get('email')! }
  get name(): AbstractControl { return this.form.get('name')! }

  async handleSubmit(): Promise<void> {
    if (this.form.invalid) return
    this.isSubmitting.set(true)

    try {
      const user = await this.userService.create(this.form.value as CreateUserDto)
      this.created.emit(user)
      this.form.reset()
    } finally {
      this.isSubmitting.set(false)
    }
  }
}
```

## HTTP Interceptors

```typescript
// interceptors/auth.interceptor.ts
import { HttpInterceptorFn, HttpHandlerFn, HttpRequest } from '@angular/common/http'
import { inject } from '@angular/core'

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
) => {
  const authService = inject(AuthService)
  const token = authService.getToken()

  if (token) {
    const authReq = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    })
    return next(authReq)
  }

  return next(req)
}

// app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http'

export const appConfig = {
  providers: [
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
    provideRouter(routes, withPreloading(PreloadAllModules)),
  ],
}
```

## Routing & Lazy Loading

```typescript
// app.routes.ts
import { Routes } from '@angular/router'
import { authGuard } from './guards/auth.guard'

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'auth',
    loadChildren: () => import('./auth/auth.routes').then(m => m.AUTH_ROUTES),
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadComponent: () => import('./dashboard/dashboard.component').then(m => m.DashboardComponent),
    children: [
      {
        path: 'users',
        loadComponent: () => import('./users/user-list.component').then(m => m.UserListComponent),
      },
    ],
  },
]

// guards/auth.guard.ts
import { inject } from '@angular/core'
import { CanActivateFn, Router } from '@angular/router'

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService)
  const router = inject(Router)

  if (auth.isAuthenticated()) return true
  return router.createUrlTree(['/auth/login'])
}
```

## Anti-patterns

```typescript
// ❌ Không unsubscribe Observable (memory leak)
this.userService.findAll().subscribe(users => this.users = users)  // ❌
// ✅ takeUntilDestroyed
this.userService.findAll().pipe(
  takeUntilDestroyed(this.destroyRef)
).subscribe(users => this.users.set(users))

// ❌ Inject trong constructor (old style)
constructor(private userService: UserService) {}  // ❌ (works but old)
// ✅ inject() function
private userService = inject(UserService)

// ❌ @NgModule và declarations (old style)
// ✅ Standalone components

// ❌ Logic trong template (performance)
<div *ngIf="users.filter(u => u.active).length > 0">  // Runs every change detection!
// ✅ computed signal
activeUsers = computed(() => this.users().filter(u => u.isActive))
```
