# MISSION: ONE VIZION RECORDS — THE GRAND EXPERIENCE
## Full UI/UX Forge Blueprint
**Forged:** 2026-04-26 | **Lead:** ANYA_Omega + SIR_BORIS | **Governed by:** SIR_CONSTANTINE (new)
**Northstar:** Luxury concert experience — lavish lobby → main stage. Never compromise elegance for speed.

---

## TASK DAG

```
EPIC-A (Design System) ──► EPIC-B (Entrance) ──► EPIC-C (Lobby)
                                                       │
EPIC-F (Governance) ──────────────────────────────────►├──► EPIC-D (Navigation)
                                                       │
                                                       └──► EPIC-E (Artist Suites)
All EPICs gate through SIR_CONSTANTINE QA before deploy.
```

---

## EPIC-A — DESIGN SYSTEM
**Knights:** Sir Visage + SIR_SONUS | **Nano:** SWEEP (reset old tokens)

### A-01 — Obsidian Gold Token System (globals.css)
Full replacement of default tokens with the "Obsidian Gold" luxury palette.
Tokens: `--void` `--obsidian` `--gold-sovereign` `--gold-shine` `--velvet` `--pearl` `--smoke`
Custom animations: `chandelier-fall` `gold-pulse` `marquee-scroll` `spotlight-sweep`

### A-02 — Typography Upgrade (layout.tsx)
Add `Cormorant Garamond` (serif luxury) via next/font/google alongside existing Geist.
Apply via `--font-cormorant` CSS var. Headings use serif; mono/labels stay Geist Mono.

### A-03 — Install framer-motion
`npm install framer-motion` — transitions, door sequence, stagger reveals, cursor spring.

---

## EPIC-B — ENTRANCE SEQUENCE
**Knights:** Sir Visage + SIR_FORGE | **Nano:** MASON (scaffold)

### B-01 — DoorSequence.tsx
Full-screen CSS 3D door reveal. Left/right Art Deco doors rotate open on Y-axis via Framer Motion.
Shows once per session (sessionStorage flag). Gold OVR logo centered while doors are closed.
Sequence: Logo fade → Doors part → Warm light bleeds through → Fade into lobby.
File: `src/app/components/entrance/DoorSequence.tsx`

### B-02 — ChandelierField.tsx
Pure CSS particle rain — 50 gold dust motes, staggered `chandelier-fall` keyframes.
Client-only (particles generated in useEffect to avoid hydration mismatch).
Responds to BPM via EngineContext: faster BPM = faster fall speed.
File: `src/app/components/entrance/ChandelierField.tsx`

---

## EPIC-C — LOBBY RESTRUCTURE
**Knights:** Sir Visage + SIR_FORGE + SIR_ALEX | **Nano:** SCAN (pre-audit current page)

### C-01 — VenueMarquee.tsx
Top-of-page venue sign: "ONE VIZION RECORDS" in Cormorant Garamond, gold, with scrolling
sub-title marquee (artist names, "NOW LIVE", etc.). Art Deco horizontal rules.
File: `src/app/components/lobby/VenueMarquee.tsx`

### C-02 — StageFrame.tsx
Gold Art Deco proscenium border wrapping the hero video. CSS border-image + ornamental
corner SVGs. Inner glow responds to `isPlaying` state.
File: `src/app/components/lobby/StageFrame.tsx`

### C-03 — DJBooth.tsx (Persistent Layout Component)
Wrapper around Jukebox styled as a professional DJ console — gold fader rail, eq bar labels,
raised platform illusion via box-shadow + border. Fixed bottom bar in layout.tsx.
Conditionally hidden on /login and /admin routes.
File: `src/app/components/lobby/DJBooth.tsx`

### C-04 — page.tsx Full Restructure
Remove Jukebox from page (moved to layout). Add VenueMarquee + ChandelierField header.
Hero video gets StageFrame. RhythmEngine panel gets "DANCE FLOOR" label + BPM floor glow.
Full bleed layout, no padding wasted. Edge-to-edge luxury.

---

## EPIC-D — NAVIGATION & TRANSITIONS
**Knights:** SIR_LINK + SIR_FORGE

### D-01 — SpotlightCursor.tsx
Fixed overlay cursor: gold crosshair default, expands to diffused spotlight circle on hover.
Uses Framer Motion `useMotionValue` + `useSpring` for smooth lag-follow.
CSS `mix-blend-mode: screen` creates real spotlight blending on content beneath.
File: `src/app/components/cursor/SpotlightCursor.tsx`

### D-02 — PageTransition.tsx + layout.tsx AnimatePresence
Client wrapper providing Framer Motion `AnimatePresence` around page content.
Each page: `initial={{ opacity: 0, y: 20 }}` → `animate={{ opacity: 1, y: 0 }}` → `exit={{ opacity: 0, y: -20 }}`
600ms ease, cinematic. Never rushed.
File: `src/app/components/PageTransition.tsx`

### D-03 — layout.tsx Full Upgrade
Add: Cormorant font, SpotlightCursor (fixed), DoorSequence (fixed), DJBooth (fixed bottom),
PageTransition wrapper, `pb-28` on main for DJ booth clearance.

---

## EPIC-E — ARTIST SUITES
**Knights:** Sir Visage + SIR_SONUS | **Nano:** MASON

### E-01 — Vizion Wealth Suite
Full-bleed parallax gold portrait header. Cormorant Garamond artist name in massive gold.
Cinematic quote. Horizontal scrolling discography (placeholder vinyl cards).
Back navigation as gold Art Deco arrow.

### E-02 — Breakout Boyz Suite
High-energy variant: fuchsia/crimson palette, italic black typography, kinetic energy.
Animated distortion border. Same structure as E-01 but with their visual language.

### E-03 — Login Page → VIP Gate
Rebrand: "THE VIP LOUNGE". Gold + black color scheme. Keypad aesthetic.
Hidden door motif — the card appears to slide in from the right.

---

## EPIC-F — SIR_CONSTANTINE GOVERNANCE
**New Knight:** SIR_CONSTANTINE — Meta-Archwizard, Sovereign Governor
**Role:** Oversees Merlin. Runs self-validation, error detection, enhancement loops.

### F-01 — SirConstantine.tsx (React Error Boundary)
Class-based ErrorBoundary with:
- Graceful fallback UI (luxury "THE SYSTEM IS RESTING" screen)
- Error reporter (console.error in dev, could extend to Supabase logging)
- Auto-retry mechanism (componentDidCatch → setState retry after 3s)
- Performance assertions: warns if frame budget exceeded
File: `src/app/components/governance/SirConstantine.tsx`

### F-02 — useGovernor.ts (Quality Hook)
Runtime quality assertions:
- Checks AudioContext state after play
- Warns if note list > 20 in RhythmEngine
- FPS monitor via requestAnimationFrame delta
- Dev-only overlay with real-time metrics
File: `src/app/hooks/useGovernor.ts`

### F-03 — Knight Registry Entry
Add SIR_CONSTANTINE to CAMELOT_OS knight roster.
Role: L4 Governance. Domain: Project quality, error sovereignty, Merlin oversight.

---

## BIOSWARM NANO-KNIGHT ASSIGNMENTS

| Knight | Tasks | Mode |
|---|---|---|
| SWEEP | Reset globals.css defaults | Purge |
| MASON | Scaffold all new component directories | Build |
| SCAN | Pre-read all files before modification | Audit |
| JUDGE | Post-EPIC TypeScript check (`tsc --noEmit`) | Validate |
| VECTOR | Index new component tree | Context |
| SENTINEL-squire | Scan for any new secrets/env exposure | Security |

---

## UKG CRYSTAL
```json
{
  "UKG_NODE": {
    "SESSION_ID": "ovr-grand-experience-2026-04-26",
    "CONTEXT_STATE": ["OBSIDIAN_GOLD", "DOOR_SEQUENCE", "DJ_BOOTH", "SIR_CONSTANTINE", "ARTIST_SUITES"],
    "ACTIVE_KNIGHTS": ["ANYA_Omega", "SIR_BORIS", "SIR_FORGE", "Sir Visage", "SIR_SONUS", "SIR_ALEX", "SIR_LINK", "SIR_CONSTANTINE"],
    "NORTHSTAR": "Luxury concert experience — lavish lobby doors open into a living, breathing record label"
  }
}
```
