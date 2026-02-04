# XTools Design System v2.0

## Overview

A comprehensive design system for XTools featuring a **Dark Neon** aesthetic with cyberpunk influences. The system prioritizes readability, accessibility, and visual impact through carefully chosen color contrasts and purposeful animations.

---

## Philosophy

- **Dark First**: Designed for dark mode as the primary experience
- **Neon Accents**: Strategic use of vibrant pink/magenta for emphasis
- **Cyberpunk Aesthetic**: Clean lines, subtle glows, high contrast
- **Motion Purposeful**: Animations guide attention and provide feedback
- **Developer Friendly**: Easy-to-use CSS variables and utility classes

---

## Architecture

### CSS Architecture

```
┌─────────────────────────────────────────┐
│     1. design-system.css                │
│     - CSS Variables (tokens)            │
│     - Base utilities                    │
│     - Keyframe animations               │
├─────────────────────────────────────────┤
│     2. animations.css                   │
│     - Complex animations                │
│     - Component interactions            │
│     - Scroll behaviors                  │
├─────────────────────────────────────────┤
│     3. style.css                        │
│     - Component styles                  │
│     - Page layouts                      │
│     - Custom overrides                  │
└─────────────────────────────────────────┘
```

### Token Structure

```
Colors
├── Primitive (pink-400, purple-500, etc.)
├── Semantic (bg-primary, text-secondary, etc.)
└── Component-specific (btn-primary-bg, etc.)

Spacing
├── Primitive (space-1, space-2, etc.)
└── Semantic (section-padding, card-gap, etc.)
```

---

## Color System

### Primary Palette

```
PINK (Primary)
50  #FCE5FF   Background tints
100 #F5B8FF   Light accents  
200 #ED8AFF   Hover highlights
300 #E55CFF   Hover states
400 #CB3CFF   ████████ PRIMARY
500 #B020E6   Active states
600 #8A17B3   Shadows
700 #641080   Deep shadows
800 #3E084D   Near-black
900 #18031A   Background
```

### Accent Palettes

```
PURPLE (Secondary)
400 #8951FF   ████████ SECONDARY
500 #7F25FB   Gradient end

CYAN (Tertiary)  
400 #21C3FC   ████████ INFO/ACCENT

BLUE
400 #0E43FB   Deep accent

ORANGE
400 #FDB52A   Warning/Highlight

GREEN
400 #34D399   Success

RED  
400 #EF4444   Error
```

### Neutral Palette (Dark)

```
100 #FFFFFF   ████████ TEXT PRIMARY
200 #D9E1FA   Text light
300 #D1DBF9   Subtle text
400 #AEB9E1   ████████ TEXT SECONDARY
500 #7E89AC   ████████ TEXT MUTED
600 #0B1739   ████████ SURFACE ELEVATED
700 #0A1330   ████████ SURFACE SECONDARY
800 #081028   ████████ BACKGROUND PRIMARY
900 #040814   Deepest background
```

### Usage Patterns

```css
/* Background hierarchy */
--bg-primary: #081028      /* Page background */
--bg-secondary: #0A1330    /* Cards, panels */
--bg-tertiary: #0B1739     /* Inputs, code blocks */

/* Text hierarchy */
--text-primary: #FFFFFF    /* Headings, important text */
--text-secondary: #AEB9E1  /* Body text, labels */
--text-muted: #7E89AC      /* Placeholders, hints */

/* Interactive hierarchy */
--interactive-primary: #CB3CFF      /* Primary actions */
--interactive-primary-hover: #E55CFF /* Hover state */
--interactive-secondary: #8951FF    /* Secondary actions */
```

---

## Typography System

### Font Stack

```css
/* Primary - Clean, modern sans-serif */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Monospace - Code, technical content */
--font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
```

### Type Scale

| Token | Size | Line Height | Letter Spacing | Usage |
|-------|------|-------------|----------------|-------|
| text-xs | 12px | 16px | 0.05em | Captions, badges |
| text-sm | 14px | 20px | 0 | Secondary text |
| text-base | 16px | 24px | 0 | Body text |
| text-lg | 18px | 28px | -0.01em | Lead paragraphs |
| text-xl | 20px | 28px | -0.02em | H4 |
| text-2xl | 24px | 32px | -0.02em | H3 |
| text-3xl | 30px | 36px | -0.02em | H2 |
| text-4xl | 36px | 40px | -0.03em | H1 |
| text-5xl | 48px | 48px | -0.03em | Display |

### Typography Patterns

```css
/* Heading styles */
h1, h2, h3 {
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-primary);
}

/* Body text */
body {
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    color: var(--text-secondary);
}

/* Monospace for code */
code, pre {
    font-family: var(--font-mono);
    font-size: 0.9em;
}
```

---

## Spacing System

### Spacing Scale

Based on 4px base unit:

| Token | Value | Common Use |
|-------|-------|------------|
| space-1 | 4px | Icon padding, tight gaps |
| space-2 | 8px | Small gaps, inline spacing |
| space-3 | 12px | Compact padding |
| space-4 | 16px | Default padding |
| space-5 | 20px | Medium gaps |
| space-6 | 24px | Section gaps |
| space-8 | 32px | Large sections |
| space-10 | 40px | Major sections |
| space-12 | 48px | Page sections |
| space-16 | 64px | Hero spacing |

### Layout Patterns

```css
/* Container padding */
.container {
    padding: var(--space-6) var(--space-8);
}

/* Card padding */
.card {
    padding: var(--space-6);
}

/* Section spacing */
.section {
    margin-bottom: var(--space-12);
}

/* Grid gaps */
.grid {
    gap: var(--space-4);
}
```

---

## Border & Radius

### Border Widths

| Token | Value | Usage |
|-------|-------|-------|
| border-0 | 0 | No border |
| border-1 | 0.6px | Subtle borders (cards) |
| border-2 | 1px | Standard borders |
| border-3 | 2px | Emphasis borders |
| border-4 | 4px | Thick borders |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| radius-sm | 8px | Small elements, tags |
| radius-md | 12px | Cards, buttons |
| radius-lg | 16px | Large cards, modals |
| radius-xl | 20px | Feature cards |
| radius-full | 9999px | Pills, badges |

### Border Colors

```css
--border-default: #343B4F;     /* Standard borders */
--border-hover: #8951FF;        /* Hover state */
--border-focus: #CB3CFF;        /* Focus state */
--border-subtle: rgba(52, 59, 79, 0.5);  /* Very subtle */
```

---

## Shadow System

### Elevation Shadows

```css
--shadow-xs:  0 1px 2px 0 rgba(0, 0, 0, 0.4);
--shadow-sm:  0 1px 3px 0 rgba(0, 0, 0, 0.5);
--shadow-md:  0 4px 6px -1px rgba(0, 0, 0, 0.5);
--shadow-lg:  0 10px 15px -3px rgba(0, 0, 0, 0.5);
--shadow-xl:  0 20px 25px -5px rgba(0, 0, 0, 0.5);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
```

### Glow Shadows (Neon Effect)

```css
--shadow-glow-pink-sm: 0 0 10px rgba(203, 60, 255, 0.4);
--shadow-glow-pink-md: 0 0 20px rgba(203, 60, 255, 0.4);
--shadow-glow-pink-lg: 0 0 40px rgba(203, 60, 255, 0.4);

--shadow-glow-purple-md: 0 0 20px rgba(137, 81, 255, 0.4);
--shadow-glow-cyan-md: 0 0 20px rgba(33, 195, 252, 0.4);
```

### Usage Guidelines

- **Cards**: `shadow-card` (subtle) + `shadow-glow-pink-md` on hover
- **Buttons**: `shadow-glow-pink-sm` default, intensify on hover
- **Modals**: `shadow-xl` for elevation
- **Dropdowns**: `shadow-lg`

---

## Gradient System

### Primary Gradients

```css
/* Main gradient - Pink to Purple */
--gradient-primary: linear-gradient(128.49deg, #CB3CFF 19.86%, #7F25FB 68.34%);

/* Hover variant - Brighter */
--gradient-primary-hover: linear-gradient(128.49deg, #E55CFF 19.86%, #9C52FF 68.34%);

/* Active variant - Darker */
--gradient-primary-active: linear-gradient(128.49deg, #B020E6 19.86%, #6619CC 68.34%);
```

### Accent Gradients

```css
--gradient-purple: linear-gradient(135deg, #8951FF 0%, #7F25FB 100%);
--gradient-cyan: linear-gradient(135deg, #21C3FC 0%, #0E43FB 100%);
--gradient-warm: linear-gradient(135deg, #FDB52A 0%, #CB3CFF 100%);
--gradient-spectrum: linear-gradient(135deg, #CB3CFF 0%, #8951FF 33%, #21C3FC 66%, #0E43FB 100%);
```

### Background Gradients

```css
--gradient-bg-subtle: linear-gradient(180deg, #0A1330 0%, #081028 100%);
--gradient-glass: linear-gradient(135deg, rgba(203, 60, 255, 0.1) 0%, rgba(137, 81, 255, 0.1) 100%);
```

---

## Animation System

### Timing Functions

```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
```

### Durations

```css
--duration-instant: 0ms;
--duration-fast: 100ms;      /* Micro-interactions */
--duration-normal: 200ms;    /* Standard transitions */
--duration-slow: 300ms;      /* Page transitions */
--duration-slower: 500ms;    /* Complex animations */
--duration-slowest: 1000ms;  /* Ambient animations */
```

### Animation Categories

#### 1. Entrance Animations
- `fadeIn` - Opacity 0 to 1
- `fadeInUp` - Fade + slide up 20px
- `scaleIn` - Scale 0.9 to 1
- `popIn` - Bounce entrance

#### 2. Exit Animations
- `fadeOut` - Opacity 1 to 0
- `scaleOut` - Scale 1 to 0.9

#### 3. Continuous Animations
- `glow` - Pulsing box-shadow
- `text-glow` - Pulsing text-shadow
- `pulse` - Opacity oscillation
- `spin` - 360° rotation

#### 4. Interaction Animations
- `hover-lift` - translateY(-2px)
- `hover-scale` - scale(1.02)
- `hover-glow` - Box-shadow glow

### Performance Best Practices

```css
/* GPU acceleration */
.gpu-accelerated {
    transform: translateZ(0);
    will-change: transform, opacity;
}

/* Reduce motion support */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Component Patterns

### Button States

```
Default:    gradient-primary + shadow-glow-pink-sm
Hover:      gradient-primary-hover + shadow-glow-pink-md
Active:     gradient-primary-active + scale(0.98)
Disabled:   opacity 0.5, no shadow
Focus:      ring 3px rgba(203, 60, 255, 0.3)
```

### Input States

```
Default:    bg-tertiary + border-default
Hover:      border-hover
Focus:      border-focus + shadow-focus
Disabled:   opacity 0.5
Error:      border-error + shadow-error
```

### Card States

```
Default:    bg-secondary + border-default + shadow-card
Hover:      border-primary + shadow-glow-pink-md + lift
Active:     scale(0.99)
```

---

## Accessibility

### Color Contrast

- **Text Primary (#FFF) on BG (#081028)**: 16.9:1 ✅
- **Text Secondary (#AEB9E1) on BG**: 8.9:1 ✅
- **Primary (#CB3CFF) on BG**: 7.2:1 ✅
- **Minimum required**: 4.5:1 for normal text

### Focus Indicators

```css
:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px rgba(203, 60, 255, 0.3);
}
```

### Motion Preferences

Always respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
    /* Disable or simplify animations */
}
```

---

## Implementation Guide

### Step 1: Import Design System

```html
<link rel="stylesheet" href="/static/css/design-system.css">
```

### Step 2: Use Semantic Variables

```css
.my-component {
    background: var(--bg-secondary);
    color: var(--text-primary);
    padding: var(--space-4);
    border-radius: var(--radius-md);
}
```

### Step 3: Add Interactions

```css
.my-component {
    transition: all var(--duration-normal) var(--ease-out);
}

.my-component:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-glow-pink-md);
}
```

### Step 4: Test Accessibility

- Check contrast ratios
- Test keyboard navigation
- Verify reduced motion support

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-XX-XX | Initial light theme |
| 2.0 | 2026-02-04 | Dark Neon redesign |

---

## Resources

- **Color Palette**: Based on cyberpunk/neon aesthetic
- **Typography**: Inter font family
- **Icons**: Font Awesome 6
- **Inspiration**: Synthwave, cyberpunk UI, neon noir

---

**Maintainers:** XTools Team  
**License:** MIT
