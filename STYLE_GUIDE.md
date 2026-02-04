# XTools Style Guide

> **Dark Neon Theme** - A cyberpunk-inspired design system with pink/magenta accents

---

## Table of Contents

1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Spacing](#spacing)
4. [Components](#components)
5. [Animations](#animations)
6. [Usage Examples](#usage-examples)

---

## Color Palette

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Pink 400 | `#CB3CFF` | Primary accent, buttons, highlights |
| Pink 300 | `#E55CFF` | Hover states |
| Pink 500 | `#B020E6` | Active states |

### Accent Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Purple 400 | `#8951FF` | Secondary accent |
| Purple 500 | `#7F25FB` | Gradient end |
| Cyan 400 | `#21C3FC` | Links, info states |
| Blue 400 | `#0E43FB` | Deep accents |
| Orange 400 | `#FDB52A` | Warnings, highlights |

### Neutral Colors (Dark Theme)

| Color | Hex | Usage |
|-------|-----|-------|
| Neutral 800 | `#081028` | Main background |
| Neutral 700 | `#0A1330` | Card backgrounds |
| Neutral 600 | `#0B1739` | Elevated surfaces |
| Neutral 500 | `#7E89AC` | Muted text |
| Neutral 400 | `#AEB9E1` | Secondary text |
| Neutral 100 | `#FFFFFF` | Primary text |

### Semantic Colors

```css
--bg-primary: #081028;      /* Main background */
--bg-secondary: #0A1330;    /* Cards */
--bg-tertiary: #0B1739;     /* Elevated */
--text-primary: #FFFFFF;    /* Headings */
--text-secondary: #AEB9E1;  /* Body text */
--text-muted: #7E89AC;      /* Captions */
--border-default: #343B4F;  /* Borders */
```

---

## Typography

### Font Stack

```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Type Scale

| Size | Value | Usage |
|------|-------|-------|
| text-xs | 0.75rem | Tags, captions |
| text-sm | 0.875rem | Secondary text |
| text-base | 1rem | Body text |
| text-lg | 1.125rem | Lead text |
| text-xl | 1.25rem | Small headings |
| text-2xl | 1.5rem | H4 |
| text-3xl | 1.875rem | H3 |
| text-4xl | 2.25rem | H2 |
| text-5xl | 3rem | H1 |

### Font Weights

```css
--font-normal: 400;     /* Body text */
--font-medium: 500;     /* UI elements */
--font-semibold: 600;   /* Subheadings */
--font-bold: 700;       /* Headings */
--font-extrabold: 800;  /* Display text */
```

---

## Spacing

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 0.25rem (4px) | Tight gaps |
| space-2 | 0.5rem (8px) | Component padding |
| space-3 | 0.75rem (12px) | Small gaps |
| space-4 | 1rem (16px) | Default gaps |
| space-6 | 1.5rem (24px) | Section gaps |
| space-8 | 2rem (32px) | Large gaps |
| space-12 | 3rem (48px) | Section padding |
| space-16 | 4rem (64px) | Large sections |

---

## Components

### Buttons

#### Primary Button

```html
<button class="btn btn-primary">Click Me</button>
```

**CSS:**
```css
.btn-primary {
    background: linear-gradient(128.49deg, #CB3CFF 19.86%, #7F25FB 68.34%);
    color: white;
    box-shadow: 0 0 20px rgba(203, 60, 255, 0.3);
}
```

#### Secondary Button

```html
<button class="btn btn-secondary">Cancel</button>
```

**CSS:**
```css
.btn-secondary {
    background: #0B1739;
    border: 0.6px solid #343B4F;
    color: #FFFFFF;
}
```

### Cards

#### Standard Card

```html
<div class="card">
    <div class="card-header">Title</div>
    <div class="card-body">Content</div>
</div>
```

**CSS:**
```css
.card {
    background: #0B1739;
    border: 0.6px solid #343B4F;
    border-radius: 12px;
    box-shadow: 1px 1px 1px rgba(16, 25, 52, 0.4);
    padding: 1.5rem;
}
```

#### Card with Hover Glow

```html
<div class="card card-glow">
    <div class="card-body">Hover me!</div>
</div>
```

### Form Elements

#### Input Field

```html
<div class="form-group">
    <label class="form-label">Email</label>
    <input type="email" class="form-control" placeholder="Enter email...">
</div>
```

**CSS:**
```css
.form-control {
    background: #0B1739;
    border: 0.6px solid #343B4F;
    border-radius: 12px;
    color: #FFFFFF;
    padding: 0.875rem 1rem;
}

.form-control:focus {
    border-color: #CB3CFF;
    box-shadow: 0 0 0 3px rgba(203, 60, 255, 0.15);
}
```

### Badges

```html
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
```

---

## Animations

### Utility Classes

| Class | Effect | Duration |
|-------|--------|----------|
| `.animate-fade-in` | Fade in | 300ms |
| `.animate-fade-in-up` | Fade in + slide up | 300ms |
| `.animate-scale-in` | Scale from 0.9 | 300ms |
| `.animate-pop-in` | Bounce pop | 500ms |
| `.animate-glow` | Pulsing glow | 2s infinite |
| `.animate-pulse` | Opacity pulse | 2s infinite |
| `.animate-spin` | 360° rotation | 1s infinite |

### Hover Effects

```html
<!-- Lift on hover -->
<div class="hover-lift">Hover me</div>

<!-- Glow on hover -->
<div class="hover-glow">Hover for glow</div>

<!-- Scale on hover -->
<div class="hover-scale">Hover to scale</div>
```

### Scroll Animations

```html
<!-- Reveal on scroll -->
<div class="reveal">I'll fade in when scrolled</div>

<!-- Staggered children -->
<ul class="stagger-children">
    <li>Item 1</li>
    <li>Item 2</li>
    <li>Item 3</li>
</ul>
```

---

## Usage Examples

### Import Order

```html
<!-- 1. Design System (MUST be first) -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/design-system.css') }}">

<!-- 2. Animations -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/animations.css') }}">

<!-- 3. Main Styles -->
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

### Page Layout

```html
<body>
    {% include 'sidebar.html' %}
    
    <div class="main-content">
        <h1 class="animate-fade-in">Page Title</h1>
        
        <div class="card card-glow">
            <div class="card-body">
                <p class="text-secondary">Content here</p>
                <button class="btn btn-primary">Action</button>
            </div>
        </div>
    </div>
</body>
```

### Dark Editor (Snippet Lab)

```css
.CodeMirror {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

.CodeMirror .cm-keyword { color: var(--pink-400) !important; }
.CodeMirror .cm-string { color: var(--green-400) !important; }
.CodeMirror .cm-comment { color: var(--text-muted) !important; }
```

### Gradient Text

```html
<h1 class="gradient-text">Gradient Title</h1>
```

```css
.gradient-text {
    background: linear-gradient(128.49deg, #CB3CFF 19.86%, #7F25FB 68.34%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

---

## Best Practices

1. **Always use CSS variables** for colors, don't hardcode hex values
2. **Use semantic color names** (`--bg-primary`, `--text-secondary`)
3. **Respect motion preferences** - use `@media (prefers-reduced-motion: reduce)`
4. **Maintain contrast ratios** - minimum 4.5:1 for text
5. **Use spacing tokens** consistently (`--space-4`, not `16px`)
6. **Animate `transform` and `opacity`** for performance

---

## File Structure

```
static/
├── css/
│   ├── design-system.css    # Core variables & utilities
│   └── animations.css       # Animation classes
├── style.css                # Main application styles
```

---

## Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

---

**Version:** 2.0  
**Last Updated:** 2026-02-04  
**Theme:** Dark Neon (Pink/Purple/Cyan)
