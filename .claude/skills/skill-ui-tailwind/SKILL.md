---
name: skill-ui-tailwind
description: Best practices dùng Tailwind CSS v4: utility patterns, responsive design, custom design tokens, dark mode và component organization.
---

# Skill: Tailwind CSS v4

## Config & Design Tokens

```css
/* app.css — Tailwind v4 CSS-first config */
@import "tailwindcss";

@theme {
  --color-primary: oklch(55% 0.2 250);
  --color-primary-foreground: oklch(98% 0 0);
  --color-secondary: oklch(95% 0.01 250);
  --color-destructive: oklch(55% 0.22 25);
  --color-muted: oklch(95% 0.01 250);
  --color-muted-foreground: oklch(50% 0.02 250);
  --color-border: oklch(90% 0.01 250);
  --color-background: oklch(100% 0 0);
  --color-foreground: oklch(15% 0.02 250);

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;

  --shadow-card: 0 1px 3px oklch(0% 0 0 / 0.1);
}
```

## Utility Patterns

```tsx
// ✅ cn() helper để compose classes
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ✅ Variant-based components
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
}

const buttonVariants = {
  base: 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:opacity-50',
  variants: {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    destructive: 'bg-destructive text-white hover:bg-destructive/90',
  },
  sizes: {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4',
    lg: 'h-12 px-6 text-lg',
  },
}

export function Button({ variant = 'primary', size = 'md', className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        buttonVariants.base,
        buttonVariants.variants[variant],
        buttonVariants.sizes[size],
        className,
      )}
      {...props}
    />
  )
}
```

## Responsive Design

```tsx
// ✅ Mobile-first breakpoints
<div className="
  grid
  grid-cols-1
  sm:grid-cols-2
  lg:grid-cols-3
  xl:grid-cols-4
  gap-4
  sm:gap-6
">

// ✅ Responsive typography
<h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">

// ✅ Show/hide at breakpoints
<nav className="hidden md:flex items-center gap-4">
<button className="md:hidden" aria-label="Menu">
```

## Dark Mode

```tsx
// ✅ Dark mode với class strategy (recommended)
// tailwind.config — v4 tự detect từ .dark class

<div className="
  bg-white dark:bg-gray-900
  text-gray-900 dark:text-gray-100
  border border-gray-200 dark:border-gray-700
">

// ✅ Dark mode toggle
function ThemeToggle() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark)
  }, [isDark])

  return (
    <button onClick={() => setIsDark(!isDark)}>
      {isDark ? <SunIcon /> : <MoonIcon />}
    </button>
  )
}
```

## Common Patterns

```tsx
// ✅ Card component
function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={cn(
      'rounded-lg border border-border bg-background p-6 shadow-card',
      className,
    )}>
      {children}
    </div>
  )
}

// ✅ Badge/Tag
function Badge({ variant = 'default', children }: BadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
      {
        'bg-primary/10 text-primary': variant === 'default',
        'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': variant === 'success',
        'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200': variant === 'destructive',
        'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200': variant === 'warning',
      },
    )}>
      {children}
    </span>
  )
}

// ✅ Input với label + error
function FormInput({ label, error, ...props }: InputProps) {
  return (
    <div className="space-y-1">
      <label className="text-sm font-medium text-foreground">{label}</label>
      <input
        className={cn(
          'w-full rounded-md border bg-background px-3 py-2 text-sm',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
          error ? 'border-destructive' : 'border-border',
        )}
        {...props}
      />
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
}
```

## Anti-patterns

```tsx
// ❌ Quá nhiều utility classes trong 1 element (extract component)
<div className="flex items-center justify-between p-4 bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer text-gray-900 font-medium text-sm">

// ✅ Extract thành component với cn()

// ❌ Hardcode colors thay vì dùng design tokens
className="text-blue-600 bg-blue-50"  // ❌ Không consistent
className="text-primary bg-primary/5"  // ✅ Design tokens

// ❌ @apply quá nhiều (mất đi lợi thế của Tailwind)
@apply flex items-center justify-center p-4 bg-primary text-white rounded;  // ❌
// ✅ Chỉ @apply cho base styles, dùng cn() cho components

// ❌ Không dùng twMerge → class conflicts
cn('p-4', 'p-8')  // Không dùng twMerge → cả hai classes exist!
// ✅ twMerge tự resolve → chỉ 'p-8' còn lại
```
