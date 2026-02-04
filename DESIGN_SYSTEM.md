# XTools Design System - shadcn/ui Edition

## Overview

A comprehensive design system for XTools featuring a **modern, clean aesthetic** inspired by shadcn/ui. The system prioritizes usability, accessibility, and professional appearance through carefully designed components and consistent spacing.

---

## Philosophy

- **Clean & Modern**: Light theme with subtle grays and clear hierarchy
- **Accessible First**: High contrast ratios, clear focus states
- **Professional**: Corporate-ready appearance suitable for enterprise tools
- **Developer Friendly**: CSS variables for easy customization
- **Component-Based**: Modular, reusable UI elements

---

## Architecture

### CSS Architecture

```
┌─────────────────────────────────────────┐
│     1. shadcn-theme.css                 │
│     - CSS Variables (HSL tokens)        │
│     - Base component styles             │
│     - Utility classes                   │
├─────────────────────────────────────────┤
│     2. Component-specific styles         │
│     - Page layouts                      │
│     - Custom overrides                  │
└─────────────────────────────────────────┘
```

---

## Color System

### CSS Variables (HSL)

All colors are defined using HSL (Hue, Saturation, Lightness) for better theming support:

```css
:root {
  --background: 0 0% 100%;        /* White */
  --foreground: 222.2 84% 4.9%;   /* Near black */
  
  --card: 0 0% 100%;              /* White */
  --card-foreground: 222.2 84% 4.9%;
  
  --popover: 0 0% 100%;
  --popover-foreground: 222.2 84% 4.9%;
  
  --primary: 222.2 47.4% 11.2%;   /* Dark slate */
  --primary-foreground: 210 40% 98%;
  
  --secondary: 210 40% 96.1%;     /* Light gray */
  --secondary-foreground: 222.2 47.4% 11.2%;
  
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  
  --destructive: 0 84.2% 60.2%;   /* Red */
  --destructive-foreground: 210 40% 98%;
  
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
}
```

### Color Usage

| Variable | Hex Value | Usage |
|----------|-----------|-------|
| Background | #FFFFFF | Page background |
| Foreground | #0F172A | Primary text |
| Muted | #F1F5F9 | Secondary backgrounds |
| Muted Foreground | #64748B | Secondary text |
| Border | #E2E8F0 | Borders, dividers |
| Primary | #0F172A | Buttons, active states |
| Primary Foreground | #F8FAFC | Text on primary |

---

## Typography

### Font Stack

```css
--font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 2.25rem (36px) | 600 | 2.5rem |
| H2 | 1.875rem (30px) | 600 | 2.25rem |
| H3 | 1.5rem (24px) | 600 | 2rem |
| H4 | 1.25rem (20px) | 600 | 1.75rem |
| Body | 1rem (16px) | 400 | 1.5rem |
| Small | 0.875rem (14px) | 400 | 1.25rem |
| Caption | 0.75rem (12px) | 500 | 1rem |

---

## Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | 0.25rem (4px) | Tight spacing |
| space-2 | 0.5rem (8px) | Icon gaps |
| space-3 | 0.75rem (12px) | Small padding |
| space-4 | 1rem (16px) | Default padding |
| space-5 | 1.25rem (20px) | Component gaps |
| space-6 | 1.5rem (24px) | Section gaps |
| space-8 | 2rem (32px) | Large gaps |
| space-10 | 2.5rem (40px) | Page sections |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| --radius-sm | 0.375rem (6px) | Small elements |
| --radius-md | 0.5rem (8px) | Buttons, inputs |
| --radius-lg | 0.75rem (12px) | Cards |
| --radius-xl | 1rem (16px) | Large cards |
| --radius-full | 9999px | Pills, badges |

---

## Components

### Buttons

```html
<!-- Primary -->
<button class="btn btn-primary">Primary</button>

<!-- Secondary -->
<button class="btn btn-secondary">Secondary</button>

<!-- Outline -->
<button class="btn btn-outline">Outline</button>

<!-- Ghost -->
<button class="btn btn-ghost">Ghost</button>

<!-- Destructive -->
<button class="btn btn-destructive">Delete</button>
```

### Cards

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Card Title</h3>
    <p class="card-description">Card description</p>
  </div>
  <div class="card-content">
    <!-- Content -->
  </div>
  <div class="card-footer">
    <!-- Footer actions -->
  </div>
</div>
```

### Form Elements

```html
<!-- Input -->
<input type="text" class="form-control" placeholder="Enter text...">

<!-- Select -->
<select class="form-select">
  <option>Option 1</option>
</select>

<!-- Label -->
<label class="form-label">Label</label>
```

### Badges

```html
<span class="badge badge-default">Default</span>
<span class="badge badge-secondary">Secondary</span>
<span class="badge badge-outline">Outline</span>
<span class="badge badge-destructive">Error</span>
```

---

## Layout Patterns

### Sidebar

- Fixed width: 260px
- Background: --card (#FFFFFF)
- Border-right: 1px solid --border
- Navigation links with hover and active states

### Main Content

- Margin-left: 260px (to account for sidebar)
- Padding: 2rem
- Responsive: Full width on mobile

### Grid System

```css
/* Auto-fill grid */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

/* Two column layout */
.two-column {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}
```

---

## Icons

Using **Lucide Icons** - modern, consistent icon set:

```html
<!-- Include script -->
<script src="https://unpkg.com/lucide@latest"></script>

<!-- Use icon -->
<i data-lucide="search" style="width: 16px; height: 16px;"></i>

<!-- Initialize -->
<script>lucide.createIcons();</script>
```

---

## Responsive Breakpoints

| Breakpoint | Width | Behavior |
|------------|-------|----------|
| Mobile | < 768px | Sidebar hidden, hamburger menu |
| Tablet | 768px - 1024px | Adjusted grid columns |
| Desktop | > 1024px | Full layout |

---

## Implementation

### 1. Include Theme CSS

```html
<link rel="stylesheet" href="/static/css/shadcn-theme.css">
```

### 2. Use Semantic Classes

```html
<div class="card">
  <h3 class="card-title">Title</h3>
  <p class="card-description">Description</p>
  <div class="card-content">
    <label class="form-label">Input Label</label>
    <input type="text" class="form-control">
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Submit</button>
  </div>
</div>
```

### 3. Initialize Icons

```javascript
lucide.createIcons();
```

---

## Best Practices

### Do
- Use semantic color variables
- Maintain consistent spacing
- Use proper heading hierarchy
- Include focus states for accessibility
- Test on mobile devices

### Don't
- Use hardcoded colors
- Mix different border radius values arbitrarily
- Skip form labels
- Use non-semantic HTML elements
- Ignore responsive design

---

## Resources

- **Font**: Inter (Google Fonts)
- **Icons**: Lucide Icons
- **Inspired by**: shadcn/ui design system
- **CSS Method**: CSS Variables with HSL colors

---

**Version**: 1.0 - shadcn/ui Edition  
**Maintainer**: XTools Team
