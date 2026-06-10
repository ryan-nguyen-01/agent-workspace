# Packages

Reusable libraries, contracts, shared types, observability helpers, and the product design system live
here. Packages are not independently deployable unless their component manifest says otherwise.

The shared frontend design system uses `<project>-design-system` and owns design tokens, themes,
shared components, icons, and Storybook stories.

Internal layout follows the Code Layout Standard: `.maestro/engine/docs/code-layout.md` — `src/<area>/` grouped by capability with an `index.*` public API and `tests/`.
