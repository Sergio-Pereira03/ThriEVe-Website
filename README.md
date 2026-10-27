# ThriEVe — Website

**Live site:** https://sergio-pereira03.github.io/ThriEVe-Website/
(GitHub Pages — auto-deploys on every push to `main`)

Marketing site for **ThriEVe** — *Classic · Custom · Exotic*. ThriEVe's product is an
**interface** — paired with a sim-racing H-pattern shifter hand-built in Wales — that
brings a real, functional **manual shift to electric cars**, reconnecting the driver to
the car. ThriEVe does **not** convert customer cars; the demo builds exist only to show
off what the shifter and interface can do.

Single-page, dependency-free static site: one HTML file, one CSS design system, one
small JS file. No build step, no npm install. Hosted at **thrieveev.com/LJ**.

## Structure

```
Thrive Website/            (folder name is historical; the brand is ThriEVe)
├─ index.html      # The whole site: one continuous scroll, section per "gear"
├─ css/styles.css  # Design system: tokens, panels, dashboard, per-gear color, parallax
├─ js/main.js      # Scroll engine (gear + tach + color + parallax), reveal, contact form
└─ assets/
   ├─ ev-symbol.png  # Logo used in the header (29 KB, exported from the .ai/.svg)
   └─ ev-symbol.svg  # Original vector mark (large; kept as source)
```

## How it works

One continuous scrolling page. Each section is a **gear**, in order:
Neutral (hero) → 1 *revival* → 2 *what we lost* → 3 *the shifter (Welsh sim-racing
hardware)* → 4 *the interface (the product)* → 5 *the demos* → 6 *contact*. The top nav
and logo are in-page anchors.

Signature behaviour, all driven by scroll in `js/main.js`:
- **Dashboard** (fixed, bottom-center) — a **tachometer** that revs through each section,
  a **gear readout**, and an **H-pattern shifter** whose knob rows N→1→…→6.
- **Per-gear color** — each section sets `--accent` (blue, orange, cyan, green, purple,
  pink); headings, dashboard, and watermark recolor smoothly on entry.
- **Parallax** — a giant watermark word behind each section drifts slower than the text.

## Design system

Theming lives in CSS custom properties at the top of `css/styles.css` (`:root`):
`--bg` (gray), `--accent` (set per section by JS). The wordmark is `Thri` + an
accent-colored `EV` + `e`; the logo's own palette is blue/orange/cyan.

## Running it

Just open `index.html` in a browser (CSS/JS load from relative paths). When hosting at
`thrieveev.com/LJ`, serve the folder so the URL resolves to `…/LJ/` (trailing slash) and
the relative `css/`, `js/`, `assets/` paths work.

## Next steps for production

1. **Contact form backend** — `js/main.js` simulates submit; point the form at a real
   service (Formspree, Basin, Netlify Forms) with a `fetch()`.
2. **Real photography, specs, and copy** — build specs/years and the LJ Pro shifter
   details are placeholders; drop a shifter photo where the `[ photo / render ]` slot is.
3. **SEO/social** — Open Graph tags, favicon, sitemap once copy is final.
