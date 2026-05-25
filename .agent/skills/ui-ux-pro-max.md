# UI UX Pro Max Skill - VALENTI AI Fashion E-commerce

## Design System (Derived from UI UX Pro Max DB)

### Target: Luxury E-commerce + AI/Voice Platform (Hybrid)
**Primary Style**: Liquid Glass + Glassmorphism + Dark Mode OLED
**Secondary**: 3D & Hyperrealism, Aurora UI, Motion-Driven
**Landing Pattern**: Hero-Centric + Feature-Rich Showcase + Social Proof

### Color Palette (E-commerce Luxury + AI Platform Fusion)
| Token         | Value                | Usage                        |
|---------------|----------------------|------------------------------|
| `--bg-deep`   | `#060608`            | OLED primary background      |
| `--bg-card`   | `rgba(16,16,22,0.7)` | Glassmorphic card surfaces   |
| `--primary`   | `#9d4edd`            | AI Purple - brand identity   |
| `--accent`    | `#ff007f`            | CTA accent - urgency/action  |
| `--gold`      | `#d4a574`            | Premium/luxury accent        |
| `--text`      | `#f3f4f6`            | Primary text                 |
| `--muted`     | `#7a7f8e`            | Secondary text               |
| `--border`    | `rgba(255,255,255,0.06)` | Subtle glass borders    |

### Typography
- **Display**: `Outfit` (800/700/600) - Headlines, brand
- **Body**: `Inter` (300-600) - Content, descriptions
- **Mono**: `Space Grotesk` (400-700) - Tags, badges, code

### Key Effects Checklist
- [x] Glassmorphic cards: `backdrop-filter: blur(16px)` + translucent bg
- [x] Liquid glass morphing on hero
- [x] Scroll-triggered reveal animations (IntersectionObserver)
- [x] 3D perspective tilt on category cards (`perspective: 800px`)
- [x] Parallax background orbs (3 layers, 28s drift cycle)
- [x] Custom cursor with ring expansion on hover
- [x] Scroll progress bar (gradient primary→accent)
- [x] Marquee ticker strip for categories
- [x] Counter animation on hero stats
- [x] Product card staggered fade-in with `translateY + rotateX`
- [x] Waveform audio visualizer (Canvas API)
- [x] Micro-interactions: button hover lift, cart glow, scale

### Anti-Patterns to AVOID
- No emojis as icons (use FontAwesome SVG icons)
- No flat/generic colors (use curated palette above)
- No jarring instant transitions (min 200ms cubic-bezier)
- No placeholder images (all 50 downloaded from Unsplash)
- No default browser fonts
- No heavy JS frameworks in static site (vanilla JS only)

### Pre-Delivery Checklist
- [ ] cursor: pointer on all clickable elements
- [ ] Hover states with smooth transitions (200-400ms)
- [ ] Focus states visible for keyboard navigation
- [ ] prefers-reduced-motion respected
- [ ] Responsive: 375px, 768px, 1024px, 1400px
- [ ] WCAG AA contrast on all text
- [ ] Loading states for async operations
- [ ] Error states with fallback images

### Motion.dev-Inspired Patterns (Vanilla JS Implementation)
Since this is a vanilla HTML/CSS/JS project (not React), we implement Motion.dev
patterns using native browser APIs:

1. **Scroll-triggered reveals** → IntersectionObserver API
2. **Spring physics** → CSS cubic-bezier(0.16, 1, 0.3, 1)
3. **Layout animations** → CSS transitions on transform/opacity
4. **Gesture animations** → mousemove/mouseleave event listeners
5. **Staggered children** → transition-delay increments
6. **Scroll progress** → scroll event + percentage calculation
