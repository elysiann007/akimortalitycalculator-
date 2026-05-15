# AKI Kidney Project — Web Frontend

## Project Overview
Next.js 16 (Turbopack) website for the AKI ICU Mortality Prediction research tool.
Built alongside the Python ML pipeline.

**Local path:** `E:\AKI\aki-kidney-project\web`
**Dev server:** `npm run dev` → http://localhost:3000

## Stack
| Layer | Tech |
|-------|------|
| Framework | Next.js 16 + App Router + TypeScript |
| Styling | Tailwind CSS v4 (CSS-first config in `globals.css`) |
| Animations | Framer Motion (`motion/react`) |
| UI Components | 21st.dev-style custom components |
| Icons | lucide-react |
| Utilities | clsx + tailwind-merge (`lib/utils.ts`) |

## Pages
| Route | File | Purpose |
|-------|------|---------|
| `/` | `app/page.tsx` | Landing — hero, stats, model bars, features, pipeline, CTA |
| `/calculator` | `app/calculator/page.tsx` | Interactive risk calculator with slider inputs + result card |
| `/models` | `app/models/page.tsx` | Model performance comparison, metrics table, feature importance |
| `/research` | `app/research/page.tsx` | Research methodology, pipeline, AKI background, tech stack |

## Key Components
- `components/Navbar.tsx` — sticky, scroll-aware, active route pill animation
- `components/ParticleField.tsx` — canvas-based animated particle network (hero bg)
- `components/CountUp.tsx` — scroll-triggered count-up animation

## Design System (globals.css CSS variables)
- Background: `#070b14` (deep navy)
- Primary accent: `#22d3ee` (teal cyan)
- Secondary: `#6366f1` (indigo)
- Cards: `rgba(255,255,255,0.02)` bg + `rgba(255,255,255,0.07)` border
- All dark — no light mode

## Calculator Logic
The calculator uses a clinical threshold-based scoring function (`computeRisk()` in calculator/page.tsx).
It is NOT connected to the Python backend — it simulates the ensemble model output using
weighted clinical thresholds for the 5 key features (Creatinine, WBC, Platelet, Bilirubin, Age).
Risk levels: Low (<25%), Moderate (25–50%), High (≥50%).

## Important Notes
- Tailwind v4 — no `tailwind.config.ts`; all config lives in `globals.css` under `@theme`
- `framer-motion` is imported as `"framer-motion"` (not `"motion/react"`)
- No external API calls — fully static/client-side
- Research tool only — disclaimers on every prediction-facing page
