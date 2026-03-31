---
name: skill-ui-figma
description: Best practices làm việc với Figma — design-to-code workflow, design tokens extraction, component mapping, Figma API, Auto Layout to CSS, variant to props, và handoff process.
---

# Skill: Figma Integration

## Design-to-Code Workflow

```
Designer (Figma)
  ↓ Figma URL / Export
Agent-Designer (analyze)
  ↓ design specs
Agent-Coder-FE (implement)

Workflow:
1. Nhận Figma URL hoặc screenshot
2. Extract design tokens (colors, typography, spacing)
3. Map Figma components → code components
4. Translate Auto Layout → CSS Flexbox/Grid
5. Convert Figma variants → component props
6. Implement pixel-accurate UI
7. Verify responsive behavior
```

---

## Reading Figma Designs

### Figma URL Parsing

```yaml
url_formats:
  design: "figma.com/design/:fileKey/:fileName?node-id=:nodeId"
  file: "figma.com/file/:fileKey/:fileName?node-id=:nodeId"
  prototype: "figma.com/proto/:fileKey/:fileName?node-id=:nodeId"
  board: "figma.com/board/:fileKey (FigJam)"

extract:
  fileKey: "From URL path segment after /design/ or /file/"
  nodeId: "From query param node-id (convert '-' to ':')"
  branch: "figma.com/design/:fileKey/branch/:branchKey → use branchKey"

example:
  url: "https://www.figma.com/design/abc123/MyApp?node-id=42-1337"
  fileKey: "abc123"
  nodeId: "42:1337"
```

### Inspection Checklist

```yaml
khi_nhận_figma_design:
  1_layout:
    - Auto Layout direction (horizontal/vertical)
    - Padding (top, right, bottom, left)
    - Gap between items
    - Alignment (start, center, end, stretch)
    - Fill container vs hug content vs fixed

  2_typography:
    - Font family + weight
    - Font size + line height
    - Letter spacing
    - Text alignment
    - Text truncation (max lines)

  3_colors:
    - Fill colors (solid, gradient)
    - Stroke/border colors
    - Opacity
    - Color tokens nếu có (từ Figma Styles/Variables)

  4_spacing:
    - Margin/padding values
    - Gap values
    - Width/height constraints (min, max, fixed, fill)

  5_effects:
    - Box shadow (x, y, blur, spread, color)
    - Border radius
    - Backdrop blur

  6_states:
    - Default, hover, active, focus, disabled
    - Figma Interactive Components → map to CSS states

  7_responsive:
    - Desktop, tablet, mobile frames
    - Which elements hide/show
    - Layout changes (sidebar → bottom nav)
    - Text size changes
```

---

## Design Tokens Extraction

### From Figma Variables/Styles

```yaml
figma_variables_to_css:
  colors:
    figma: "Brand/Primary → #2563eb"
    css: "--color-primary: #2563eb;"
    tailwind: "primary: '#2563eb'"

  typography:
    figma: "Heading/H1 → Inter 36px Bold"
    css: |
      --font-h1-size: 2.25rem;
      --font-h1-weight: 700;
      --font-h1-line-height: 1.2;

  spacing:
    figma: "Spacing/lg → 24px"
    css: "--spacing-lg: 1.5rem;"

  radius:
    figma: "Radius/md → 8px"
    css: "--radius-md: 0.5rem;"

  shadows:
    figma: "Shadow/card → 0 4px 6px rgba(0,0,0,0.1)"
    css: "--shadow-card: 0 4px 6px rgba(0,0,0,0.1);"
```

### Mapping to UI Libraries

```yaml
tailwind:
  figma_token: "Primary #2563eb"
  config: |
    // tailwind.config.ts
    theme: {
      extend: {
        colors: {
          primary: {
            DEFAULT: '#2563eb',
            hover: '#1d4ed8',
            light: '#dbeafe',
          },
        },
      },
    }

shadcn:
  figma_token: "Primary #2563eb"
  config: |
    /* globals.css — HSL format */
    :root {
      --primary: 217 91% 60%;
      --primary-foreground: 0 0% 100%;
    }

mui:
  figma_token: "Primary #2563eb"
  config: |
    const theme = createTheme({
      palette: {
        primary: { main: '#2563eb', light: '#dbeafe', dark: '#1d4ed8' },
      },
    })

antd:
  figma_token: "Primary #2563eb"
  config: |
    <ConfigProvider theme={{ token: { colorPrimary: '#2563eb' } }}>
```

---

## Figma Auto Layout → CSS

### Translation Rules

```yaml
auto_layout_to_css:
  direction:
    horizontal: "display: flex; flex-direction: row;"
    vertical: "display: flex; flex-direction: column;"

  gap:
    figma: "Spacing between items: 16"
    css: "gap: 1rem;"

  padding:
    figma: "Padding: 16, 24, 16, 24 (top, right, bottom, left)"
    css: "padding: 1rem 1.5rem;"

  alignment:
    figma_primary: # Main axis
      start: "justify-content: flex-start;"
      center: "justify-content: center;"
      end: "justify-content: flex-end;"
      space_between: "justify-content: space-between;"
    figma_counter: # Cross axis
      start: "align-items: flex-start;"
      center: "align-items: center;"
      end: "align-items: flex-end;"
      stretch: "align-items: stretch;"

  sizing:
    hug_content: "width: auto; (or omit)"
    fill_container: "flex: 1; (or width: 100%)"
    fixed: "width: 300px;"
    min_max: "min-width: 200px; max-width: 600px;"

  wrap:
    figma: "Wrap" toggle
    css: "flex-wrap: wrap;"
```

### Example Translation

```
Figma Frame:
  ├── Auto Layout: Vertical
  ├── Gap: 24
  ├── Padding: 32
  ├── Fill: white
  ├── Radius: 12
  ├── Shadow: 0 4px 6px rgba(0,0,0,0.1)
  └── Children:
      ├── Title (Hug) → <h2>
      ├── Description (Fill, Hug) → <p>
      └── Button Row (Horizontal, Gap 12, Align End)
          ├── Cancel Button
          └── Submit Button
```

```tsx
// ✅ Translated component
function Card({ title, description, onCancel, onSubmit }) {
  return (
    <div className="flex flex-col gap-6 p-8 bg-white rounded-xl shadow-md">
      <h2 className="text-xl font-semibold">{title}</h2>
      <p className="text-gray-600">{description}</p>
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={onCancel}>Cancel</Button>
        <Button onClick={onSubmit}>Submit</Button>
      </div>
    </div>
  )
}
```

---

## Component Mapping

### Figma Components → Code Components

```yaml
mapping_strategy:
  1_identify: "List all Figma components + variants"
  2_categorize:
    primitives: "Button, Input, Badge — map to UI library (shadcn, MUI)"
    composed: "UserCard, SearchBar — custom components using primitives"
    page_specific: "DashboardHeader — single-use feature components"
  3_map_variants:
    figma: "Button variant=Primary/Secondary, size=sm/md/lg, state=default/hover/disabled"
    code: "<Button variant='primary' size='md' disabled={false} />"

variant_to_props:
  figma_variant: "Size=Small, Style=Outlined, State=Disabled"
  react_props: |
    <Button
      size="sm"           // Size variant
      variant="outline"   // Style variant
      disabled            // State variant
    />

  figma_boolean: "Has Icon=true"
  react_props: |
    <Button icon={<SearchIcon />}>Search</Button>

  figma_instance_swap: "Icon=ArrowRight"
  react_props: |
    <Button rightIcon={<ArrowRight />}>Next</Button>
```

### Component Inventory Template

```yaml
# Từ Figma, tạo inventory cho FE dev

primitives_from_library:
  - name: Button
    figma: "Components/Button"
    code: "<Button variant size onClick />"
    variants: [primary, secondary, outline, ghost, destructive]
    sizes: [sm, md, lg]
    ui_lib: shadcn

  - name: Input
    figma: "Components/Input"
    code: "<Input type placeholder disabled />"
    states: [default, focus, error, disabled]
    ui_lib: shadcn

composed_custom:
  - name: UserAvatar
    figma: "Components/UserAvatar"
    code: "<UserAvatar user size showStatus />"
    contains: [Avatar, StatusBadge, Tooltip]
    props:
      user: "{ name, avatarUrl, status }"
      size: "sm | md | lg"
      showStatus: boolean

  - name: SearchBar
    figma: "Components/SearchBar"
    code: "<SearchBar value onChange onSubmit />"
    contains: [Input, SearchIcon, Kbd shortcut hint]
```

---

## Responsive Design from Figma

```yaml
figma_frames:
  desktop: "1440px (or 1280px)"
  tablet: "768px"
  mobile: "375px"

translation:
  breakpoints: |
    // Tailwind (mobile-first)
    <div className="
      flex flex-col        /* mobile: stack */
      md:flex-row          /* tablet+: side by side */
      lg:max-w-6xl         /* desktop: max width */
    ">

  hidden_elements: |
    // Sidebar hidden on mobile, visible on desktop
    <aside className="hidden lg:block w-64">
      <Sidebar />
    </aside>
    // Bottom nav visible on mobile only
    <nav className="fixed bottom-0 lg:hidden">
      <BottomTabs />
    </nav>

  grid_changes: |
    // Stats: 1 col mobile → 2 col tablet → 4 col desktop
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard />
      <StatCard />
      <StatCard />
      <StatCard />
    </div>
```

---

## Handoff Checklist

```yaml
designer_provides:
  required:
    - "[ ] Figma link with correct page/frame selected"
    - "[ ] Design tokens defined (colors, typography, spacing)"
    - "[ ] All component states (default, hover, active, disabled, error)"
    - "[ ] Responsive variants (desktop, tablet, mobile)"
    - "[ ] Real content (not Lorem Ipsum for key flows)"
  
  nice_to_have:
    - "[ ] Component documentation (usage guidelines)"
    - "[ ] Interaction specs (animations, transitions)"
    - "[ ] Edge cases (empty state, error state, loading)"
    - "[ ] Dark mode variants"

developer_checks:
  before_coding:
    - "[ ] Extract all design tokens"
    - "[ ] Map Figma components to UI library components"
    - "[ ] Identify custom components needed"
    - "[ ] Note responsive breakpoints"
    - "[ ] Clarify ambiguous specs with designer"

  after_coding:
    - "[ ] Visual comparison: code vs Figma"
    - "[ ] Responsive test: all breakpoints"
    - "[ ] Interaction states: all hover/focus/active"
    - "[ ] Accessibility: keyboard nav, contrast, screen reader"
```

---

## Figma MCP Integration

```yaml
khi_có_figma_url:
  1. "Parse URL → extract fileKey + nodeId"
  2. "Call Figma MCP get_design_context → returns code + screenshot + hints"
  3. "Analyze response:"
  4. "  - Code Connect snippets → use mapped codebase component directly"
  5. "  - Component documentation links → follow for usage context"
  6. "  - Design annotations → follow designer notes"
  7. "  - Design tokens as CSS vars → map to project token system"
  8. "  - Raw hex colors → map to existing theme tokens"
  9. "Adapt output to project stack, components, conventions"

important:
  - "Output from Figma MCP is REFERENCE — not final code"
  - "Always check project for existing components that match"
  - "Reuse project tokens/components instead of generating new ones"
```

---

## Anti-patterns

```yaml
pixel_perfect_obsession:
  bad: "Spend hours matching every pixel — 1px off"
  fix: "Match design intent and proportions, not individual pixels. Use design tokens."

hardcoded_values:
  bad: "color: #2563eb; font-size: 14px; padding: 16px;"
  fix: "Use tokens: text-primary, text-sm, p-4"

ignoring_states:
  bad: "Only implement default state from Figma"
  fix: "Ask designer for all states: hover, focus, disabled, error, loading, empty"

screenshot_coding:
  bad: "Code from screenshot without inspecting Figma properties"
  fix: "Always inspect Auto Layout, spacing, tokens in Figma"

no_component_reuse:
  bad: "Create new component for every Figma frame"
  fix: "Map to existing UI library components first, only create custom when needed"
```
