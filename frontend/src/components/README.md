# Global UI components

Reusable, presentational primitives shared across every Mira feature. **Read
this before building any new UI** — if a primitive here (or a composition of a
few) covers what you need, use it instead of writing a bespoke element. New
modules should reach for these first; only add a _new_ global component when a
pattern is genuinely reused across features.

## How to use

Import from the barrel:

```tsx
import { Button, Card, Badge, GlyphTile } from "@/components";
```

- Everything here is a **presentational** component — no data fetching, no
  feature logic. Feature-specific pieces live under `src/features/<feature>/`.
- Colour, type, radius, shadow and motion come from the **design tokens** in
  [`../app/globals.css`](../app/globals.css) (Tailwind `@theme`). Use utilities
  (`bg-card`, `text-ink2`, `rounded-lg`, `shadow-float`, `font-display`,
  `animate-fade-up`) — never hard-code hex values.
- Tone → class mappings live in [`../lib/tones.ts`](../lib/tones.ts). Tailwind
  only sees literal class strings, so tones are full-string lookups (never build
  `bg-${tone}` at runtime — it gets purged).
- `cn(...)` from [`../lib/cn.ts`](../lib/cn.ts) joins conditional class names.

## Catalog

| Component                 | Purpose                                                   | Key props                                                                    |
| ------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `Logo`                    | Mira mark + wordmark (topbar, auth)                       | `size`, `variant` (`solid`/`ghost`), `showTagline`, `onClick`                |
| `Button`                  | Primary action button                                     | `variant` (`primary`/`secondary`/`success`), `size` (`md`/`lg`), `fullWidth` |
| `IconButton`              | Square single-glyph/icon button (back, close, send, home) | `variant` (`card`/`paper`/`ink`/`accent`), `size`, `radius`                  |
| `SegmentedControl`        | Pill toggle for a small mutually-exclusive set            | `options`, `value`, `onChange`, `variant` (`ink`/`card`), `stretch`          |
| `Card`                    | Shared surface (white, hairline border, soft shadow)      | `className` (add radius/padding/hover)                                       |
| `Badge`                   | Status / label pill                                       | `tone`, `mono`, `pulse`, `className`                                         |
| `Avatar`                  | Gradient initials square                                  | `initials`, `gradient` (`good`/`warn`/`bad`/`violet`), `size`, `display`     |
| `GlyphTile`               | Tinted tile stamped with a subject/topic glyph            | `glyph`, `tone` or `toneClassName`, `size`                                   |
| `SearchInput`             | Text input with leading search icon + focus ring          | `value`, `onChange`, `placeholder`, `height`                                 |
| `TextField`               | Labeled form input — inline `error`, `hint`, ARIA wiring  | `label`, `value`, `onChange`, `id`, `error`, `autoComplete`, `trailing`      |
| `Checkbox`                | Accessible controlled checkbox with optional error        | `checked`, `onChange`, `label`, `id`, `error`                                |
| `Modal`                   | Centered overlay dialog (click-outside + Escape close)    | `open`, `onClose`, `title`, `width`                                          |
| `Toast`                   | Fixed top-center transient notification (pair `useToast`) | `message`                                                                    |
| `ProgressBar`             | Track with animated, left-anchored fill                   | `value` (0–1), `fillClassName`, `height`, `delaySec`                         |
| `StatCard`                | Big figure over a caption (KPI tile)                      | `value`, `label`, `size`, `background`, `accent`, `valueClassName`           |
| `EmptyState`              | Dashed-border "no results" placeholder                    | `size` (`sm`/`lg`)                                                           |
| `SearchIcon` / `HomeIcon` | Inline SVG icons                                          | standard SVG props                                                           |

### Examples

```tsx
// Actions
<Button variant="primary" onClick={onStart}>Start a new chat</Button>
<IconButton variant="accent" onClick={onSend} title="Send">↑</IconButton>

// Toggle
<SegmentedControl
  options={[{ value: "student", label: "Student" }, { value: "teacher", label: "Teacher" }]}
  value={role}
  onChange={setRole}
/>

// Identity + status
<Avatar initials="MC" gradient="violet" size={42} />
<GlyphTile glyph="½" tone="green" size={46} />
<Badge tone="amberSolid" pulse>Pending</Badge>

// Metrics
<StatCard value="84%" label="Recent accuracy" valueClassName="text-green" />
<ProgressBar value={0.42} fillClassName="bg-green" />

// Overlay + toast (state from useToast)
<Modal open={open} onClose={close} title="Your profile">…</Modal>
<Toast message={toast.message} />
```

## Supporting modules

- **Tokens** — [`../app/globals.css`](../app/globals.css): colours, fonts,
  radii (`sm/md/lg/xl` = 10/15/22/30px), shadows (`shadow-soft/float/pop`),
  keyframes + `animate-*`.
- **Tones** — [`../lib/tones.ts`](../lib/tones.ts): `Tone`, `Health`,
  `Understanding` types; `glyphTileTone`, `healthChipTone`,
  `understandingChipTone`, `avatarGradient`, `masteryFillClass`,
  `improvementColorClass`.
- **Backdrop** — [`../lib/backdrop.ts`](../lib/backdrop.ts): `MIRA_BACKDROP`, the
  shared paper-with-glows page background.
- **Hooks** — [`../hooks/useResponsive.ts`](../hooks/useResponsive.ts)
  (`mobile`/`tablet`/`desktop` breakpoint) and
  [`../hooks/useToast.ts`](../hooks/useToast.ts) (auto-dismissing toast state).

## Guardrails (enforced by ESLint)

Every file here obeys the repo limits: ≤ **200 lines/file**, ≤ **50
lines/function**, complexity ≤ **10**. When a component grows past a limit,
**decompose** (extract a sub-component or helper) rather than raising the limit.
No `dangerouslySetInnerHTML`; keep components server-safe and add `"use client"`
only when a component needs state/effects/handlers of its own (e.g. `Modal`).
