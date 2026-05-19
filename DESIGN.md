---
name: IFMLogiX — Logfi
description: Financial cockpit for FM operations; per-project P&L, cash flow, and risk at a glance.
colors:
  clearance-green: "#059669"
  clearance-green-deep: "#047857"
  clearance-green-soft: "#ecfdf5"
  canvas: "#f8fafc"
  surface: "#ffffff"
  surface-muted: "#f1f5f9"
  ink: "#0f172a"
  ink-strong: "#020617"
  ink-muted: "#475569"
  ink-faint: "#64748b"
  ink-whisper: "#94a3b8"
  border: "#e2e8f0"
  border-strong: "#cbd5e1"
  signal-negative: "#e11d48"
  signal-negative-soft: "#fff1f2"
  signal-warning: "#d97706"
  signal-warning-soft: "#fffbeb"
  signal-info: "#2563eb"
typography:
  display:
    fontFamily: '"DM Sans", "Rubik", system-ui, sans-serif'
    fontSize: "clamp(2.75rem, 5.5vw, 4rem)"
    fontWeight: 700
    lineHeight: 1.0
    letterSpacing: "-0.022em"
  headline:
    fontFamily: '"DM Sans", "Rubik", system-ui, sans-serif'
    fontSize: "clamp(2.25rem, 4.5vw, 3.25rem)"
    fontWeight: 700
    lineHeight: 1.02
    letterSpacing: "-0.018em"
  title:
    fontFamily: '"DM Sans", "Rubik", system-ui, sans-serif'
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  body:
    fontFamily: '"DM Sans", "Rubik", system-ui, sans-serif'
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0"
  label:
    fontFamily: '"DM Sans", "Rubik", system-ui, sans-serif'
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0"
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
  xl: "18px"
  2xl: "22px"
  full: "9999px"
spacing:
  card-pad: "clamp(1.25rem, 2vw, 1.75rem)"
  section-gap: "2rem"
  inset-sm: "0.875rem"
  inset-md: "1.25rem"
components:
  button-primary:
    backgroundColor: "{colors.clearance-green}"
    textColor: "#ffffff"
    rounded: "{rounded.lg}"
    padding: "0.625rem 1.125rem"
  button-primary-hover:
    backgroundColor: "{colors.clearance-green-deep}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "0.625rem 1.125rem"
  button-dark:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "0.625rem 1.125rem"
  button-dark-hover:
    backgroundColor: "{colors.ink-strong}"
  nav-pill-default:
    backgroundColor: "transparent"
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.full}"
    padding: "0.5rem 0.875rem"
  nav-pill-active:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    rounded: "{rounded.full}"
    padding: "0.5rem 0.875rem"
  chip-positive:
    backgroundColor: "{colors.clearance-green-soft}"
    textColor: "{colors.clearance-green}"
    rounded: "{rounded.full}"
    padding: "0.1875rem 0.5rem"
  chip-warning:
    backgroundColor: "{colors.signal-warning-soft}"
    textColor: "{colors.signal-warning}"
    rounded: "{rounded.full}"
    padding: "0.1875rem 0.5rem"
  chip-negative:
    backgroundColor: "{colors.signal-negative-soft}"
    textColor: "{colors.signal-negative}"
    rounded: "{rounded.full}"
    padding: "0.1875rem 0.5rem"
  input-default:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "0.625rem 0.875rem"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.xl}"
    padding: "{spacing.card-pad}"
---

# Design System: IFMLogiX — Logfi

## 1. Overview

**Creative North Star: "The Financial Cockpit"**

Logfi is a financial instrument panel, not a reporting tool. The design draws from aviation and Bloomberg terminal UI: precise, readable under pressure, nothing decorative. A manager glances at this in a daylit office between two back-to-back calls. They need the answer in 10 seconds, not 10 minutes. The system is designed to be scanned, not read.

The palette is deliberately restrained: a near-white canvas, slate-family ink stops, and one accent — Clearance Green — used only when something is confirmed, active, or safe. The ink-on-white surface works naturally in the ambient light of an office. Everything is readable at a glance without eye strain.

Logfi explicitly rejects: the homogeneous "generic SaaS cream" (beige backgrounds, rounded-everything, gradients) that describes 80% of B2B tools; the dense grey-table Excel aesthetic it replaced; over-reliance on teal as a calming brand color (too clinical); and crypto/VC-deck dark-mode energy. The design should not be guessable from its category.

**Key Characteristics:**
- Instrument-panel density: data is the product, chrome is infrastructure
- Typographic hierarchy carries all visual weight — no decorative borders or gradients
- Clearance Green appears on at most 10% of any screen; its scarcity signals meaning
- Financial figures always use tabular numerals; column alignment is structural, not aesthetic
- Layered shadow vocabulary encodes hierarchy: canvas, surface, raised card, float
- RTL (Hebrew) is structural throughout — logical CSS properties only, no physical overrides

## 2. Colors: The Cockpit Palette

A single chromatic voice on a near-neutral field. The canvas is barely-tinted slate; everything else is semantic.

### Primary
- **Clearance Green** (`#059669` / `oklch(60.7% 0.165 165)`): The single brand accent. Used for primary CTAs, active navigation states, positive financial signals (on-target margin, positive P&L), and focus rings. Its rarity is the message: when something is green, it is cleared. Never used decoratively.
- **Clearance Green Deep** (`#047857`): Hover and pressed state for green interactive elements. Never used at rest.
- **Clearance Green Soft** (`#ecfdf5`): Pale emerald, 4% saturation. Chip and badge backgrounds for positive states. The tint that whispers "cleared" without shouting it.

### Neutral
- **Canvas** (`#f8fafc`): The app background. Barely-tinted slate-50 — enough warmth to read as considered, not enough to read as "beige SaaS."
- **Surface** (`#ffffff`): Card and modal background. White against the canvas gives the layering its structure.
- **Surface Muted** (`#f1f5f9`): Table header row fills, hover state backgrounds, secondary panel surfaces. The middle layer between canvas and surface.
- **Ink** (`#0f172a`): Primary text, headings, active nav, data figures. The darkest readable ink stop.
- **Ink Strong** (`#020617`): Near-black. Used for the logo mark and maximum-contrast UI needs only. Not body text.
- **Ink Muted** (`#475569`): Secondary labels, supporting text, metadata. The workhorse shade.
- **Ink Faint** (`#64748b`): Footnotes, tertiary annotations, timestamps. Passes WCAG AA at 4.92:1 on white. The floor for readable text.
- **Ink Whisper** (`#94a3b8`): Placeholders and disabled states only. Decorative — never used for content that needs to be read.
- **Border** (`#e2e8f0`): Card edges, dividers, input strokes. Nearly invisible at rest.
- **Border Strong** (`#cbd5e1`): Emphasis dividers, table footers, active input borders.

### Tertiary: Semantic Signals
- **Signal Negative** (`#e11d48`): Loss, error, critical margin states. Rose-red, not deep red — readable and urgent without being alarming.
- **Signal Warning** (`#d97706`): At-risk projects, watch-state margin. Amber: caution, not crisis.
- **Signal Info** (`#2563eb`): Informational callouts, non-critical alerts.
- Soft variants (`signal-*-soft`): Chip and badge backgrounds for semantic states.

### Named Rules
**The Clearance Green Rule.** Clearance Green (`#059669`) occupies at most 10% of any screen. One primary CTA per view, at most. The active nav pill, the positive state chip. Its rarity is the point: the first green element the eye lands on has earned it.

**The Ink Gradient Rule.** The six ink stops map to content importance — never break the correlation. Ink (`#0f172a`) for primary data; Ink Muted for labels; Ink Faint for annotations; Ink Whisper for decoration only. A fainter ink on a more important label is an error, not a style choice.

**The No-Signal Rule.** Semantic colors (negative/warning/info) are reserved for their domains. Warning amber is never used for brand decoration. Red is never used for anything other than loss or error.

## 3. Typography

**Display/Body Font:** DM Sans (with Rubik as Hebrew fallback, then system-ui)

**Character:** A single-family system: DM Sans for Latin; Rubik for Hebrew glyphs in the same weight and proportion. No display/body split. The hierarchy comes entirely from size and weight contrast, not from mixing typefaces. The effect is cockpit-clean — one voice, different volumes.

### Hierarchy
- **Display** (700, `clamp(2.75rem, 5.5vw, 4rem)`, lh 1.0, ls -0.022em): Hero KPI numbers only. The single most important financial figure on a view. One per screen.
- **Headline** (700, `clamp(2.25rem, 4.5vw, 3.25rem)`, lh 1.02, ls -0.018em): Secondary hero numbers or view titles on large desktop layouts.
- **Title** (600, `1.25rem`, lh 1.25, ls -0.01em): Section headings, card headings, modal titles.
- **Body** (400, `0.9375rem` / 15px, lh 1.55): All prose, labels, table content. Maximum line length: 65ch on text-heavy surfaces.
- **Label** (500, `0.75rem` / 12px, lh 1.2, ls 0): Eyebrow labels, column headers, footnotes, metadata tags.

### Named Rules
**The Tabular First Rule.** Every financial figure uses `font-feature-settings: "lnum" 1, "tnum" 1` (lining, tabular numerals). Proportional numerals in data columns are forbidden — misaligned decimal points break the instrument-panel illusion.

**The Single Voice Rule.** DM Sans and Rubik are the only typefaces. No serif for body, no mono for labels, no decorative script anywhere. Hierarchy comes from scale and weight — not from switching faces.

## 4. Elevation

Logfi uses a four-layer shadow vocabulary. Shadow encodes layer position, not emotional state. Every surface has a fixed layer assignment; nothing floats between layers or skips one.

```
Layer 0 — Canvas:     #f8fafc, no shadow
Layer 1 — Page:       white surface, shadow-sm
Layer 2 — Raised:     card on hover, shadow-md
Layer 3 — Float:      dropdown, modal, tooltip, shadow-lg / shadow-xl
```

### Shadow Vocabulary
- **Flat** (no shadow): Raw canvas and muted surfaces. Table rows, form backgrounds, mobile fullscreen panels.
- **Ambient** (`shadow-sm: 0 1px 2px 0 rgb(15 23 42 / 0.04), 0 1px 3px 0 rgb(15 23 42 / 0.06)`): Cards at rest. The minimal presence of a surface above canvas.
- **Lifted** (`shadow-md: 0 2px 4px -2px rgb(15 23 42 / 0.06), 0 4px 12px -2px rgb(15 23 42 / 0.08)`): Cards on hover, inputs on focus. Responds to interaction.
- **Elevated** (`shadow-lg: 0 10px 30px -10px rgb(15 23 42 / 0.18), 0 4px 12px -4px rgb(15 23 42 / 0.08)`): Dropdowns, alert panels. Floated above the page.
- **Modal** (`shadow-xl: 0 20px 48px -16px rgb(15 23 42 / 0.22), 0 8px 24px -8px rgb(15 23 42 / 0.10)`): Modals, full-screen overlays. The highest layer.

### Named Rules
**The State-Only Lift Rule.** Cards and inputs rest flat (shadow-sm). Shadow-md appears only in response to state: hover lifts a card, focus lifts an input. Never apply shadow-md or above to a resting, non-interactive surface.

**The Layer Stack Rule.** Four layers only. Nothing lives between canvas and card (no "mini-card within a card on hover" patterns). Nested cards are always wrong.

## 5. Components

### Buttons

Tactile and confident. Moderate radius (14px — gently curved, not pill-rounded), decisive weight (600). Three variants with distinct roles; they are not interchangeable.

- **Shape:** Gently curved (14px radius)
- **Primary — Clearance Green:** Background `#059669`, white text, `0.625rem 1.125rem` padding. Used for the single most important CTA in a view (new project, save). At most one per screen.
- **Dark — Ink:** Background `#0f172a`, white text. Confirms modal actions (save, apply). Authoritative without competing with green.
- **Secondary — Ghost:** White background, `#e2e8f0` border, `#0f172a` text. Cancel, dismiss, secondary navigation. Quiet, but sized identically to primary.
- **Hover:** Darkens background by one stop, adds shadow-md.
- **Active:** `scale(0.97)` in 140ms cubic-bezier(0.23, 1, 0.32, 1).
- **Focus visible:** 2px `#059669` outline, 3px offset — consistent with global ring.
- **Icon button:** 40px square, transparent background, `#475569` icon color. Hover: surface-muted background. Used for bell, close, settings entry points.

### Chips / Status Pills

Four semantic variants: positive (green), warning (amber), negative (red), neutral (muted). Full-pill radius (9999px). Font: 0.75rem, weight 600, tabular numerals. Used alongside financial figures to carry the verdict without requiring the reader to interpret the number.

- **Positive:** `#ecfdf5` background, `#059669` text.
- **Warning:** `#fffbeb` background, `#d97706` text.
- **Negative:** `#fff1f2` background, `#e11d48` text.
- **Neutral:** `#f1f5f9` background, `#475569` text.

### Cards

The primary layout unit for isolating data groups. 18px radius, white surface, `border: 1px solid #e2e8f0`, shadow-sm at rest. Padding: `clamp(1.25rem, 2vw, 1.75rem)`. Mini-card variant for dense grids: 14px radius, `1rem 1.125rem` padding, no shadow.

**Nested cards are prohibited.** Never place a card inside a card.

### Inputs and Fields

Stroke style (white background, `#e2e8f0` border, 14px radius). Focus state: border shifts to `#059669`, adds 3px emerald ring at 20% opacity. Error state: border `#e11d48`, ring at 12% opacity. Placeholder text: Ink Whisper (`#94a3b8`). Labels above inputs: Label scale (0.8125rem, 500 weight, `#475569`).

### Navigation

Top bar stays white with no blur (opaque). Nav pills are full-pill radius (9999px): inactive text is Ink Muted, no background; hover adds Surface Muted background; active state inverts to Ink background with white text. The active state is a solid ink pill — confident, unambiguous. Transitions: 140ms ease-out only; no animation on initial render.

### Data Tables

Column headers: Label scale (0.75rem, 600 weight, `#475569`), Surface Muted background. Row height: `0.875rem 1rem` padding. Alternating state on hover: Surface Muted row highlight. Footer rows: `border-top: 2px solid #cbd5e1`, Surface Muted background, weight 700. All numerical cells: tabular-nums, text-align end (logical, RTL-safe).

### KPI Hero Numbers (Signature Component)

The display-scale number that answers the primary question on a view. One per view, full-row card, white surface. Number at display scale (clamp 2.75–4rem, weight 700, ls -0.022em, tabular), colored by financial state (positive/negative). Label at 0.75rem above; footnote at 0.75rem below in Ink Faint. No gradient, no decorative background — the number IS the component.

## 6. Do's and Don'ts

### Do:
- **Do** use tabular numerals (`font-feature-settings: "lnum" 1, "tnum" 1`) on every financial figure, every time.
- **Do** use logical CSS properties (`inset-inline-start`, `padding-inline-end`, `text-align: start`) everywhere. Never use physical `left` / `right` for RTL-sensitive layout.
- **Do** place the single most important number above the fold, at display scale, with its financial verdict (color + pill) immediately adjacent.
- **Do** let shadow encode layer position. Canvas has none; cards have shadow-sm; floated elements have shadow-lg or above.
- **Do** use Clearance Green sparingly. One primary CTA, the active nav state, confirmed signals. Its meaning depends on its rarity.
- **Do** size every interactive element to at least 40px in both dimensions. Touch targets below 44px fail WCAG 2.5.8.
- **Do** add `aria-expanded` to every button that opens a dropdown or panel.
- **Do** use `role="img"` and a computed `aria-label` on every Chart.js canvas.
- **Do** respect `prefers-reduced-motion`. Decorative stagger animations are suppressed; press feedback and focus transitions survive.

### Don't:
- **Don't** use `border-inline-start` (or `border-left` / `border-right`) greater than 1px as a colored stripe on cards, alerts, or toasts. This is the generic SaaS notification pattern Logfi explicitly rejects. Use a tinted background, a full border, or a leading icon instead.
- **Don't** use gradient text (`background-clip: text` with a gradient). Financial figures earn their emphasis through scale and weight.
- **Don't** use glassmorphism (blurred backgrounds, frosted-glass cards) as decoration. The topbar is fully opaque by design.
- **Don't** put more than one primary (green) CTA on a screen. If a second primary action exists, demote it to dark or secondary.
- **Don't** nest cards. A card inside a card is always the wrong structure.
- **Don't** design for dark mode by default or by reflex. Logfi is used in a daylit office. The light theme is a design decision, not a default.
- **Don't** use the generic SaaS cream aesthetic: beige/off-white backgrounds, friendly rounded-everything, gradient accents, neutral-warm color temperature. That is the category-reflex answer and it is prohibited here.
- **Don't** produce anything that reads as Excel or legacy government software: dense grey tables, no hierarchy, no color system. That is what Logfi replaced.
- **Don't** use teal as a personality color. It exists in the palette only as Clearance Green for positive/action states. An interface that reads as "teal-dominant" has failed.
- **Don't** use neon, gradient fills, or dark backgrounds with high-chroma accents. That energy belongs to crypto dashboards, not FM financial cockpits.
- **Don't** use Ink Whisper (`#94a3b8`) for any content that needs to be read. It is for placeholders and disabled states only; it fails WCAG AA for body text.
