# J Star Technologies — Website

A static marketing site for **J Star Technologies**, an AI-native engineering
partner. Deep-navy canvas, electric-blue + gold accents, three linked pages.

It ships as **plain HTML / CSS / vanilla JS** — no framework, no build step
required to deploy, no runtime dependencies beyond Google Fonts. Drop the folder
on any static host and it works.

## Pages

| File                   | Purpose                                                              |
| ---------------------- | ------------------------------------------------------------------- |
| `index.html`           | **Home** — hero, stats, persona toggle, capabilities, ventures, filterable tech stack, Zero-to-Ten teaser, leadership, CTA |
| `zero-to-ten.html`     | **Zero-to-Ten** methodology — AI-native advantage, human engineering, and the auto-advancing interactive pipeline |
| `fractional-cto.html`  | **Fractional CTO & Advisory** — executive edge, engagement cards, why-fractional |

## Quick preview

Any static file server works — for example:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy

No build is needed; the HTML is already generated. Publish the whole directory:

- **GitHub Pages** — push to a repo and enable Pages (serve from the branch root).
- **Netlify / Vercel / Cloudflare Pages** — point at the repo; no build command,
  publish directory `/`.
- **S3 / any static host / nginx** — upload the folder; `index.html` is the entry.

## Project structure

```
.
├── index.html            # Home (entry point)
├── zero-to-ten.html      # Methodology page
├── fractional-cto.html   # Advisory page
├── jstar.css             # Brand foundations — tokens, type, buttons
├── site.css              # Shared chrome — nav, footer, sections, CTA
├── home.css              # Home-page section styles
├── pages.css             # Zero-to-Ten & Fractional-CTO styles
├── app.js                # Interactivity: scroll-reveal, persona toggle,
│                         #   tech-stack filter, animated pipeline
├── assets/               # Brand logo (mark + full lockup)
├── fonts/                # Self-hosted Inter (Space Grotesk + JetBrains Mono
│                         #   load from Google Fonts via @import in jstar.css)
└── build.py              # Generator: regenerates the three HTML files
```

## Editing content

Page copy and data (capabilities, ventures, tech stack, leadership, pipeline
stages, advisory engagements) live in **`build.py`**. Edit there and regenerate:

```bash
python3 build.py
```

This rewrites `index.html`, `zero-to-ten.html`, and `fractional-cto.html`.
Styling lives in the four CSS files; behavior lives in `app.js`.

## Placeholders to replace with real assets

- **Leadership photos** — currently elegant initial monograms (`AS`, `GS`) and a
  "PHOTO TO COME" portrait on the advisory page. Swap in real headshots when ready.
- **Tech-stack tiles** — clean brand-styled monogram tiles (no copyright risk).
  Swap for real logo files if preferred.
- **Contact** — email is `lets.code.net@gmail.com` (footer + all `mailto:` CTAs).
- **Venture links** — point to `qwiik.com`, `zanbio.com`, `xten.pro`.

---

Design handed off from Claude Design and implemented as a deployable static site.
