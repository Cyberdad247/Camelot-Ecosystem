# SIR_FORGE — Phoenix Portal Task Sheet
# Knight: SIR_FORGE (Engineering / Code Gen)
# Mode: BEAVER | Self-Error-Check: ON
# Target: templates/page.author-landing.liquid

---

## WAVE 1 TASKS

### T1.1: Lead Capture Modal (Section 8) [CRITICAL]
**Priority:** P0 | **Est. Lines:** ~120 HTML + ~80 CSS + ~60 JS

**Requirements:**
- Modal triggered by: "Claim Your Skeleton Key" CTA, "Download Free Book" link
- Fields: Name (required), Email (required), Phone (optional)
- Hidden fields: UTM params, timestamp, referrer
- States: Initial -> Loading ("Unlocking Vault...") -> Success -> Error
- Gold/black theme matching existing design system (#d4af37, #050505)
- Close on overlay click, Escape key, X button
- Body scroll lock when modal open
- Mobile responsive (full-width on <768px)

**Implementation Notes:**
- Insert modal HTML before closing `</div>` of `.phoenix-portal`
- CSS goes in existing `<style>` block
- JS goes in existing `<script>` block
- Form POST to Shopify customer creation endpoint OR Klaviyo
- Fallback: `mailto:` link if no backend configured

**Self-Error-Check:**
- [ ] Modal opens from both CTA buttons
- [ ] Form validates Name + Email before submit
- [ ] Modal closes on overlay click, X, and Escape
- [ ] Scroll locked when open, restored on close
- [ ] Success state shows download button
- [ ] Error state shows inline validation (red borders)
- [ ] Mobile: modal is full-width, fields are touch-friendly
- [ ] No XSS via form inputs (sanitize before display)

---

### T1.2: Exit Intent Recovery (Section 9) [HIGH]
**Priority:** P1 | **Est. Lines:** ~40 HTML + ~30 CSS + ~40 JS

**Requirements:**
- Desktop trigger: mouseout event when cursor Y < 10px
- Mobile trigger: rapid upward scroll detection
- Conditions: `!leadCaptured && !exitIntentShown` (show once only)
- Content: "Wait, Truth Seeker" headline, social proof ("12,000+ people"), two buttons
- Primary CTA opens lead capture modal (reuse T1.1)
- Secondary CTA dismisses (transparent button)
- Slide-down animation from top

**Self-Error-Check:**
- [ ] Only fires once per session
- [ ] Does NOT fire if lead already captured
- [ ] Desktop: triggers on mouseout Y < 10
- [ ] Mobile: triggers on rapid upward scroll
- [ ] Primary button opens lead modal
- [ ] Secondary button dismisses overlay
- [ ] Dismiss persisted to sessionStorage

---

## WAVE 2 TASKS

### T2.1: QR Portals Section (Section 6) [MEDIUM]
**Priority:** P2 | **Est. Lines:** ~80 HTML + ~50 CSS + ~30 JS

**Requirements:**
- 3 QR code cards: "The 1% Theorem" (Book), "Revelator Access" (Interview), "Audio Archives" (Playlist)
- Badges: "Most Popular", "Exclusive", "New"
- Static scan counters (localStorage-based, no WebSocket for now)
- Download button per QR (Canvas API PNG generation)
- Gold border cards on dark background
- Responsive: 3-col desktop, stack mobile

**Self-Error-Check:**
- [ ] All 3 QR cards render with correct badges
- [ ] Counter displays and increments on simulated scan
- [ ] Download generates PNG image
- [ ] Cards stack on mobile (<768px)
- [ ] Scroll animation triggers (IntersectionObserver)

---

### T2.2: Expand Glossary Table [LOW]
**Priority:** P3 | **Est. Lines:** ~30 HTML

**Requirements:**
- Add 4-5 more dictionary entries to existing table
- Maintain existing animation stagger pattern
- Research accurate 1913 Webster's definitions

**Words to Add:**
- GOVERNMENT, EDUCATION, PERSON, CITIZEN, FREEDOM
- Each with 1913 principles-based definition vs 2026 authority-based

**Self-Error-Check:**
- [ ] All new rows animate with stagger delay
- [ ] Definitions are historically accurate (verify sources)
- [ ] Table doesn't overflow on mobile

---

### T2.3: SEO + OG Meta Tags [HIGH]
**Priority:** P1 | **Est. Lines:** ~25 HTML

**Requirements:**
- Add inside `<head>`:
  - `<meta name="description">` (150 chars)
  - `<meta property="og:title">`, `og:description`, `og:image`, `og:url`
  - `<meta name="twitter:card">`, twitter title/description/image
  - `<link rel="canonical">`
- OG image: use store logo or trailer thumbnail

**Self-Error-Check:**
- [ ] All meta tags present in `<head>`
- [ ] OG image URL resolves (not 404)
- [ ] Description under 160 chars
- [ ] No duplicate meta tags

---

## WAVE 3 TASKS

### T3.1: Performance Optimization [MEDIUM]
**Priority:** P2 | **Est. Lines:** ~20 modifications

**Requirements:**
- Add `<link rel="preload">` for trailer video
- Add `loading="lazy"` to non-critical images
- Add `poster` attribute to video elements (thumbnail fallback)
- Defer YouTube API script loading
- Fix auto-enter timeout: 45s -> 30s per spec
- Add video error handler (poster fallback on load failure)

**Self-Error-Check:**
- [ ] Preload hint in `<head>` for video
- [ ] Video has poster attribute
- [ ] Auto-enter fires at 30s (not 45s)
- [ ] Video error shows fallback image
- [ ] Lighthouse Performance > 85

---

### T3.2: Accessibility [MEDIUM]
**Priority:** P2 | **Est. Lines:** ~40 modifications

**Requirements:**
- ARIA labels on all interactive elements
- `role="dialog"` + `aria-modal="true"` on lead capture modal
- Focus trap inside modal when open
- `aria-hidden="true"` on cinema container when exited
- Skip-to-content link
- Keyboard navigation for glossary table
- `prefers-reduced-motion` media query (disable animations)

**Self-Error-Check:**
- [ ] Tab order logical through all interactive elements
- [ ] Modal traps focus when open
- [ ] Screen reader announces modal open/close
- [ ] Reduced motion respected
- [ ] Lighthouse Accessibility > 90
