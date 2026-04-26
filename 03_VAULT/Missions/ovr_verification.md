# QA VERIFICATION MATRIX — ONE VIZION RECORDS: THE GRAND EXPERIENCE
**QA Lead:** SIR_CONSTANTINE | **Review:** SIR_SENTINEL + SIR_DEBUG
**Standard:** Production-ready only. Every FAIL blocks deploy.
**Forged:** 2026-04-26

---

## V-A: DESIGN SYSTEM

### VA-01 — CSS Token Coverage
```bash
grep -c "var(--gold-sovereign\|var(--obsidian\|var(--void" src/app/globals.css
```
- [ ] ≥ 8 custom tokens defined in `:root`
- [ ] `@keyframes chandelier-fall` defined
- [ ] `@keyframes gold-pulse` defined
- [ ] `@keyframes marquee-scroll` defined
- [ ] Background defaults to `--void` (#000), not white

### VA-02 — Typography
- [ ] Cormorant Garamond loaded via `next/font/google`
- [ ] `--font-cormorant` CSS variable accessible
- [ ] VenueMarquee uses serif font class
- [ ] Jukebox mono labels still use Geist Mono
- [ ] No layout shift from font loading (next/font handles this)

### VA-03 — Build green post-design-system
```bash
cd one-vizion-records && npm run build
```
- [ ] Exit code 0
- [ ] Zero TypeScript errors
- [ ] Zero new ESLint errors

---

## V-B: ENTRANCE SEQUENCE

### VB-01 — DoorSequence functional
**Browser:** Fresh session (sessionStorage cleared)
- [ ] OVR logo visible centered on black screen on load
- [ ] Doors animate open within 0–2s
- [ ] No flicker or white flash during sequence
- [ ] Lobby visible after doors open
- [ ] Second visit: doors DO NOT replay (sessionStorage `ovr_entered` = `true`)
- [ ] No hydration mismatch errors in console

### VB-02 — DoorSequence performance
```js
// DevTools → Performance → record 5s including door open
```
- [ ] No dropped frames below 30fps during door animation
- [ ] CSS transforms only (no layout-triggering properties animated)
- [ ] GPU compositing active (check Layers panel — element should be on own layer)

### VB-03 — ChandelierField
- [ ] Gold particles visible raining down across header area
- [ ] No particles generated on server (hydration safe)
- [ ] 0 errors in console related to chandelier
- [ ] At 60fps BPM: particles fall at base speed
- [ ] At 140 BPM: particles noticeably faster

---

## V-C: LOBBY

### VC-01 — VenueMarquee
- [ ] "ONE VIZION RECORDS" renders in Cormorant Garamond serif
- [ ] Gold color (#C9A84C or equivalent)
- [ ] Scrolling subtitle marquee animates continuously
- [ ] Art Deco horizontal rules visible above/below text
- [ ] Responsive: looks correct at 375px (mobile), 768px (tablet), 1440px (desktop)

### VC-02 — StageFrame (Proscenium)
- [ ] Gold border wraps hero video section
- [ ] Corner ornaments visible (SVG or CSS)
- [ ] Border glows when `isPlaying = true`
- [ ] Video still plays/loops behind the frame
- [ ] Frame does not clip video content

### VC-03 — DJBooth (Persistent)
- [ ] Jukebox visible at bottom of screen on ALL pages (/, /artists/*)
- [ ] Hidden on /login and /admin
- [ ] Does not obscure page content (main has `pb-28`)
- [ ] Music continues playing when navigating between pages
- [ ] Console gold styling distinguishes it from page content
- [ ] EngineContext state preserved across navigation

### VC-04 — Page layout (Lobby)
- [ ] No nested Jukebox in page body (removed from page.tsx)
- [ ] Full-bleed layout, no excessive white space
- [ ] RhythmEngine panel displays "DANCE FLOOR" label
- [ ] BPM floor glow visible below RhythmEngine when music plays

---

## V-D: NAVIGATION & TRANSITIONS

### VD-01 — SpotlightCursor
- [ ] Custom cursor renders on desktop (hidden on touch devices)
- [ ] Cursor follows mouse with smooth spring lag (~100ms delay)
- [ ] Expands on hover over buttons/links
- [ ] `mix-blend-mode: screen` creates spotlight blend effect
- [ ] Does not prevent normal click interactions
- [ ] Hidden when pointer leaves window

### VD-02 — Page Transitions
- [ ] Navigating / → /artists/vizion-wealth: fade+slide out/in animation
- [ ] Back navigation: smooth reverse
- [ ] No white flash between pages
- [ ] Animation completes in ≤ 600ms
- [ ] Works correctly on mobile (touch navigation)

### VD-03 — Layout integrity
```bash
npx tsc --noEmit
```
- [ ] layout.tsx TypeScript clean
- [ ] All client components properly marked `"use client"`
- [ ] No server/client boundary violations

---

## V-E: ARTIST SUITES

### VE-01 — Vizion Wealth Suite
- [ ] Artist name in large Cormorant Garamond, gold gradient
- [ ] Cinematic quote renders correctly
- [ ] Discography section placeholder renders (no broken layout)
- [ ] Back navigation styled as gold Art Deco arrow
- [ ] Mobile: stacks cleanly

### VE-02 — Breakout Boyz Suite
- [ ] Fuchsia/crimson visual language distinct from VW suite
- [ ] Bold italic treatment on artist name
- [ ] Kinetic energy conveyed through border/animation
- [ ] Consistent structure with VW suite

### VE-03 — VIP Login Gate
- [ ] Gold + black color scheme (not cyan/fuchsia)
- [ ] "VIP LOUNGE" or equivalent luxury copy
- [ ] Card slide-in animation on mount
- [ ] Form still functional (existing Supabase auth untouched)
- [ ] Error states still display correctly
- [ ] Link back to home styled as gold "← Exit" 

---

## V-F: SIR CONSTANTINE GOVERNANCE

### VF-01 — ErrorBoundary wraps app
- [ ] `<SirConstantine>` wraps `{children}` in layout.tsx
- [ ] Deliberately thrown error in a component shows fallback UI (not blank/crash)
- [ ] Fallback UI is on-brand (luxury aesthetic, not default React error)
- [ ] Auto-retry logic fires after 3s delay

### VF-02 — useGovernor quality assertions
- [ ] In dev mode: FPS monitor logs warning if < 30fps
- [ ] Audio context state checked after play — warns if still `suspended`
- [ ] No governor code ships to production bundle (`process.env.NODE_ENV` guard)
- [ ] No TypeScript errors in hook

### VF-03 — Production bundle clean
```bash
npm run build 2>&1 | grep -E "error|Error|warning|Warning"
```
- [ ] Zero TypeScript compilation errors
- [ ] Zero ESLint errors (warnings reviewed and accepted or fixed)
- [ ] No `console.log` in production components (only `console.warn`/`console.error` where intentional)

---

## V-FINAL: SOVEREIGN REVIEW

### FINAL-01 — Full production build
```bash
cd one-vizion-records && npm ci && npm run lint && npm run build
echo "Exit: $?"
```
- [ ] `npm run lint`: 0 errors
- [ ] `npm run build`: exit 0
- [ ] Route table shows all 6 routes (/, /admin, /artists/*, /login)
- [ ] No new routes broken

### FINAL-02 — Mobile smoke test
Chrome DevTools → Device: iPhone 14 Pro
- [ ] Door sequence renders (or gracefully skips if reduced motion)
- [ ] DJ Booth visible and usable at mobile breakpoint
- [ ] VenueMarquee text does not overflow
- [ ] RhythmEngine canvas doesn't cause OOM

### FINAL-03 — Accessibility minimum
- [ ] All images have `alt` props
- [ ] Interactive elements have `aria-label` where icon-only
- [ ] Custom cursor has `pointer-events: none` (doesn't block a11y)
- [ ] `prefers-reduced-motion` media query respected on door sequence + cursor

### FINAL-04 — Vercel deployment green
- [ ] `vercel deploy --prod` exits 0
- [ ] Production URL returns 200 on /
- [ ] No build errors in Vercel logs
- [ ] Deployment ID logged to CAMELOT_OS/PROVENANCE_LEDGER.md

---

## QA SCOREBOARD

| EPIC | Checks | Pass | Fail | Warn |
|---|---|---|---|---|
| A Design System | 9 | | | |
| B Entrance | 7 | | | |
| C Lobby | 10 | | | |
| D Navigation | 7 | | | |
| E Artist Suites | 9 | | | |
| F Governance | 7 | | | |
| FINAL | 10 | | | |
| **TOTAL** | **59** | | | |

**SHIP when:** 59/59 PASS or all FAILs escalated to SIR_BORIS with disposition.

**ESCALATION:**
- Security FAIL → halt, SIR_SENTINEL + BORIS
- Build FAIL → do not deploy
- Accessibility FAIL → fix before deploy (not optional)
- Performance WARN → document + accept or fix

*SIR_CONSTANTINE governs this matrix. Any FAIL is a BLOCK. No exceptions.*
