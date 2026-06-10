# Experience

Store user journeys, user flows, information architecture, wireframes, prototypes, UI specifications,
content rules, and accessibility intent here.

The executable design system belongs in `packages/<project>-design-system`; this directory describes the
experience and design decisions that system implements.

## UI/UX deliverable format (R-019-0a-ui)

For products with a UI, the design is a **viewable static HTML/CSS prototype** the user opens in a
browser to approve before coding:

```text
docs/experience/
├── wireframes/
│   ├── index.html        links every screen — open this to review/approve
│   ├── <screen>.html     one static page per key screen (real layout + states)
│   └── styles.css        real design tokens (color/typography/spacing) + component styles
├── user-flows/<flow>.md  UX flows as Mermaid diagrams
└── ui-specifications/<screen>.md  component hierarchy, states, responsive + accessibility intent
```

Static HTML/CSS only (no backend, no real data). The approved prototype + `styles.css` tokens are the
visual contract the built UI must match; ui-ux-designer produces them.
