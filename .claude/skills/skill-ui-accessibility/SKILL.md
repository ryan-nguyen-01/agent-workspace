---
name: skill-ui-accessibility
description: Best practices accessibility (a11y) — WCAG 2.2 compliance, ARIA patterns, keyboard navigation, screen reader support, color contrast, focus management, và testing tools.
---

# Skill: Accessibility (a11y)

## WCAG 2.2 Levels

```yaml
Level_A (minimum):
  - All images have alt text
  - All form inputs have labels
  - Color is not the only means of conveying info
  - Content is keyboard accessible
  - No keyboard traps

Level_AA (target — legal requirement in many countries):
  - Color contrast ≥ 4.5:1 (text), ≥ 3:1 (large text)
  - Text resizable to 200% without loss
  - Focus visible on all interactive elements
  - Skip to main content link
  - Error identification + suggestion
  - Consistent navigation

Level_AAA (ideal):
  - Color contrast ≥ 7:1
  - Sign language for multimedia
  - Extended audio description
```

---

## Semantic HTML

```html
<!-- ❌ Div soup -->
<div class="header">
  <div class="nav">
    <div class="link" onclick="navigate()">Home</div>
  </div>
</div>
<div class="main">
  <div class="article">
    <div class="title">Blog Post</div>
  </div>
</div>

<!-- ✅ Semantic HTML — screen readers understand structure -->
<header>
  <nav aria-label="Main navigation">
    <a href="/">Home</a>
  </nav>
</header>
<main>
  <article>
    <h1>Blog Post</h1>
  </article>
</main>
<footer>
  <p>&copy; 2025 MyApp</p>
</footer>
```

### Landmark Roles

```html
<header>     <!-- banner -->
<nav>        <!-- navigation -->
<main>       <!-- main content (1 per page) -->
<aside>      <!-- complementary -->
<footer>     <!-- contentinfo -->
<section>    <!-- region (with aria-label) -->
<form>       <!-- form -->
<search>     <!-- search (HTML5.2) -->
```

---

## ARIA Patterns

### When to Use ARIA

```yaml
rule: "No ARIA is better than bad ARIA"

order_of_preference:
  1. Use native HTML element (<button>, <input>, <select>, <a>)
  2. If native element exists → DON'T add ARIA
  3. Only use ARIA when no native element fits the pattern
  4. Every ARIA role MUST have expected keyboard interaction

# ❌ Bad — redundant ARIA
<button role="button" aria-label="Submit">Submit</button>

# ✅ Good — native element is enough
<button>Submit</button>

# ✅ Good — ARIA needed for custom component
<div role="tablist" aria-label="Settings tabs">
  <button role="tab" aria-selected="true" aria-controls="panel-1">General</button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">Security</button>
</div>
```

### Common ARIA Patterns

```typescript
// ✅ Modal / Dialog
function Modal({ isOpen, onClose, title, children }) {
  return isOpen ? (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onKeyDown={(e) => e.key === 'Escape' && onClose()}
    >
      <h2 id="modal-title">{title}</h2>
      <div>{children}</div>
      <button onClick={onClose}>Close</button>
    </div>
  ) : null
}

// ✅ Tabs
function Tabs({ tabs, activeIndex, onChange }) {
  return (
    <>
      <div role="tablist" aria-label="Content tabs">
        {tabs.map((tab, i) => (
          <button
            key={i}
            role="tab"
            id={`tab-${i}`}
            aria-selected={i === activeIndex}
            aria-controls={`panel-${i}`}
            tabIndex={i === activeIndex ? 0 : -1}
            onClick={() => onChange(i)}
            onKeyDown={(e) => {
              if (e.key === 'ArrowRight') onChange((i + 1) % tabs.length)
              if (e.key === 'ArrowLeft') onChange((i - 1 + tabs.length) % tabs.length)
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, i) => (
        <div
          key={i}
          role="tabpanel"
          id={`panel-${i}`}
          aria-labelledby={`tab-${i}`}
          hidden={i !== activeIndex}
          tabIndex={0}
        >
          {tab.content}
        </div>
      ))}
    </>
  )
}

// ✅ Toast / Live region
<div role="status" aria-live="polite" aria-atomic="true">
  {toastMessage}
</div>

// ✅ Alert (important, interrupt user)
<div role="alert">
  Payment failed. Please check your card details.
</div>

// ✅ Loading state
<div aria-busy="true" aria-live="polite">
  <span className="sr-only">Loading results...</span>
  <Spinner />
</div>
```

---

## Keyboard Navigation

### Requirements

```yaml
tab_order:
  - Tab moves forward through focusable elements
  - Shift+Tab moves backward
  - Order matches visual layout (CSS order doesn't change tab order)
  - Skip navigation link as first focusable element

interactive_elements:
  button: "Enter or Space to activate"
  link: "Enter to follow"
  checkbox: "Space to toggle"
  radio: "Arrow keys to navigate, Space to select"
  select: "Arrow keys, Enter to open, Escape to close"
  tabs: "Arrow keys to navigate, Enter/Space to activate"
  menu: "Arrow keys, Enter to select, Escape to close"
  modal: "Tab trapped inside, Escape to close"
  combobox: "Type to filter, Arrow keys, Enter to select"
```

### Focus Management

```typescript
// ✅ Focus trap for modals
function useFocusTrap(ref: RefObject<HTMLElement>) {
  useEffect(() => {
    const element = ref.current
    if (!element) return

    const focusableElements = element.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    // Focus first element on mount
    firstElement?.focus()

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement?.focus()
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement?.focus()
        }
      }
    }

    element.addEventListener('keydown', handleKeyDown)
    return () => element.removeEventListener('keydown', handleKeyDown)
  }, [ref])
}

// ✅ Return focus when modal closes
function useReturnFocus() {
  const triggerRef = useRef<HTMLElement | null>(null)

  const saveTrigger = () => {
    triggerRef.current = document.activeElement as HTMLElement
  }

  const returnFocus = () => {
    triggerRef.current?.focus()
  }

  return { saveTrigger, returnFocus }
}

// ✅ Skip to main content
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-white focus:text-black">
  Skip to main content
</a>
<main id="main-content" tabIndex={-1}>
  {/* content */}
</main>
```

---

## Color & Contrast

```yaml
contrast_ratios:
  normal_text: "≥ 4.5:1 (AA) | ≥ 7:1 (AAA)"
  large_text: "≥ 3:1 (AA) | ≥ 4.5:1 (AAA)"
  ui_components: "≥ 3:1 (buttons, inputs, icons)"

  large_text_definition: "≥ 18px bold OR ≥ 24px regular"

rules:
  - "NEVER use color as the only indicator"
  - "Error states: red color + icon + text message"
  - "Links: underline OR different from body text + 3:1 contrast"
  - "Focus indicator: ≥ 3:1 contrast against background"
  - "Disabled states: still readable, just visually muted"

examples:
  # ❌ Color only
  bad: "Required fields are in red"
  
  # ✅ Color + icon + text
  good: "Required fields marked with * and red border + error message below"

tools:
  - "Chrome DevTools → Rendering → Emulate vision deficiencies"
  - "axe DevTools browser extension"
  - "Contrast checker: webaim.org/resources/contrastchecker"
```

---

## Forms

```html
<!-- ✅ Accessible form -->
<form aria-labelledby="form-title" novalidate>
  <h2 id="form-title">Create Account</h2>

  <!-- Label explicitly linked -->
  <div>
    <label for="email">Email address <span aria-hidden="true">*</span></label>
    <input
      id="email"
      type="email"
      required
      aria-required="true"
      aria-describedby="email-hint email-error"
      aria-invalid="true"
    />
    <p id="email-hint" class="hint">We'll never share your email</p>
    <p id="email-error" class="error" role="alert">Please enter a valid email</p>
  </div>

  <!-- Checkbox group -->
  <fieldset>
    <legend>Notification preferences</legend>
    <label><input type="checkbox" name="notify" value="email" /> Email</label>
    <label><input type="checkbox" name="notify" value="sms" /> SMS</label>
  </fieldset>

  <button type="submit">Create Account</button>
</form>
```

### Error Handling

```yaml
requirements:
  - Error identified in text (not just color)
  - Error linked to field via aria-describedby
  - Focus moves to first error on submit
  - Error message suggests how to fix
  - Live region announces errors to screen readers

implementation: |
  function onSubmit() {
    const errors = validate(formData)
    if (errors.length > 0) {
      setErrors(errors)
      // Focus first field with error
      document.getElementById(errors[0].fieldId)?.focus()
      // Announce to screen readers
      announceRef.current.textContent = `${errors.length} errors found. Please fix and try again.`
    }
  }
```

---

## Images & Media

```html
<!-- ✅ Informative image -->
<img src="chart.png" alt="Sales increased 25% from Q1 to Q2 2025" />

<!-- ✅ Decorative image — empty alt -->
<img src="decoration.svg" alt="" />

<!-- ✅ Complex image — longer description -->
<figure>
  <img src="architecture.png" alt="System architecture diagram" aria-describedby="arch-desc" />
  <figcaption id="arch-desc">
    The system consists of an API gateway connecting to three microservices...
  </figcaption>
</figure>

<!-- ✅ Icon button — aria-label -->
<button aria-label="Close dialog">
  <svg aria-hidden="true"><!-- X icon --></svg>
</button>

<!-- ✅ Video with captions -->
<video controls>
  <source src="demo.mp4" type="video/mp4" />
  <track kind="captions" src="captions.vtt" srclang="en" label="English" default />
</video>
```

---

## Screen Reader Only (Visually Hidden)

```css
/* ✅ Visually hidden but accessible to screen readers */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* ✅ Show on focus (skip links) */
.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}
```

---

## Testing

```yaml
automated:
  tools: [axe-core, pa11y, Lighthouse]
  ci_integration: |
    // Jest + axe-core
    import { axe, toHaveNoViolations } from 'jest-axe'
    expect.extend(toHaveNoViolations)

    test('form is accessible', async () => {
      const { container } = render(<LoginForm />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

  playwright: |
    // Playwright accessibility scan
    test('page has no a11y violations', async ({ page }) => {
      await page.goto('/login')
      const results = await new AxeBuilder({ page }).analyze()
      expect(results.violations).toEqual([])
    })

manual:
  keyboard_test: "Tab through entire page — can you reach everything? Can you escape?"
  screen_reader: "Test with VoiceOver (Mac) or NVDA (Windows)"
  zoom_test: "200% zoom — is content still usable?"
  reduced_motion: "prefers-reduced-motion — are animations disabled?"

checklist:
  - "[ ] Every interactive element keyboard accessible"
  - "[ ] Focus visible on all focusable elements"
  - "[ ] Images have appropriate alt text"
  - "[ ] Form inputs have labels"
  - "[ ] Errors announced to screen readers"
  - "[ ] Color contrast meets AA"
  - "[ ] Skip to content link present"
  - "[ ] Headings in logical order (h1 → h2 → h3)"
  - "[ ] Language attribute on <html>"
  - "[ ] Page title descriptive and unique"
```

---

## Anti-patterns

```yaml
div_button:
  bad: "<div onclick='submit()'>Submit</div>"
  fix: "<button type='submit'>Submit</button>"

missing_alt:
  bad: "<img src='logo.png' />"
  fix: "<img src='logo.png' alt='Company Logo' /> or alt='' if decorative"

autoplay_media:
  bad: "<video autoplay> with sound"
  fix: "No autoplay OR muted by default with controls visible"

removing_focus_outline:
  bad: "* { outline: none; }"
  fix: "Custom focus styles: :focus-visible { outline: 2px solid blue; }"

placeholder_as_label:
  bad: "<input placeholder='Email' /> (no <label>)"
  fix: "Always use <label>, placeholder is supplementary"
```
