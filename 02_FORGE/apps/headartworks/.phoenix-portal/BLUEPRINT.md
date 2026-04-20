# PHOENIX PORTAL BLUEPRINT
# Operation: PHOENIX_FORGE | Mode: BEAVER (Efficiency + Self-Error-Check)
# Store: headartwork.myshopify.com | Theme: Main (#175658238271)
# Template: page.author-landing.liquid (945 lines, monolithic)
# Date: 2026-04-11 | Lead: SIR_BORIS v3.0

---

## I. CURRENT STATE AUDIT

### What EXISTS (in page.author-landing.liquid):
| Section | Spec Name | Status | Quality |
|---------|-----------|--------|---------|
| S0 | Session Controller | BUILT | OK - sessionStorage check works |
| S1 | Cinematic Gateway | BUILT | OK - video/audio/skip/progress bar |
| S2 | Hero Portal | BUILT | OK - video bg, title, CTA |
| S3 | Master Locksmith (Bio) | BUILT | OK - grid layout, interview embed |
| S4 | Streamed Revolution | BUILT | OK - playlist embed |
| S5 | 1949 Script / Glossary | BUILT | PARTIAL - only 3 dictionary entries |
| S7 | Network Bridge | BUILT | OK - 4 links with animations |

### What is MISSING:
| Section | Spec Name | Priority | Complexity |
|---------|-----------|----------|------------|
| S6 | QR Portals (live counters) | MEDIUM | HIGH (needs WebSocket) |
| S8 | Lead Capture Modal | CRITICAL | MEDIUM |
| S9 | Exit Intent Recovery | HIGH | LOW |
| L4a | Analytics (GA4 + Meta Pixel) | HIGH | LOW |
| L4b | UTM Parameter Tracking | HIGH | LOW |
| L4c | Shopify Customer API integration | CRITICAL | MEDIUM |
| L4d | Klaviyo Email Flow | HIGH | MEDIUM |
| PERF | Critical CSS / Preload / Lazy Load | MEDIUM | LOW |
| SEO | Meta tags, OG tags, structured data | HIGH | LOW |
| A11Y | Accessibility (ARIA, keyboard nav) | MEDIUM | LOW |

### Architecture Issues:
1. **Monolithic template** - 945 lines of HTML+CSS+JS in single .liquid file
2. **No Shopify sections** - bypasses theme editor entirely (standalone page)
3. **Auto-enter timeout** - 45s (spec says 30s)
4. **No mobile-specific UX** - only basic 768px breakpoint
5. **No error boundaries** - video load failure = blank screen
6. **Glossary table** - only 3 entries, spec implies more
7. **No form/modal** - zero lead capture capability
8. **No analytics** - no GA4, no Meta Pixel, no event tracking

---

## II. NORTH STAR

> A cinematic, conversion-optimized portal that converts visitors to leads
> through the "Illusions Revealed" narrative journey, with real-time social
> proof, analytics tracking, and email automation.

### Success Metrics:
- Lead capture modal functional with Shopify Customer creation
- Exit intent fires on desktop (mouseout) and mobile (scroll velocity)
- GA4 events: page_view, trailer_completed, lead_captured, cta_clicked
- All 9 sections render correctly on mobile + desktop
- Page weight < 100KB initial (before YouTube iframes)
- Lighthouse Performance > 85, Accessibility > 90

---

## III. KNIGHT DISPATCH (Beaver Mode - Parallel Execution)

### WAVE 1: Foundation (Parallel)
| Knight | Domain | Deliverable |
|--------|--------|-------------|
| SIR_FORGE | Code Gen | S8: Lead Capture Modal (HTML/CSS/JS) |
| SIR_FORGE | Code Gen | S9: Exit Intent Recovery |
| LADY_APIS | Research | Klaviyo + GA4 + Meta Pixel integration code |
| SIR_SENTINEL | Security | Input validation, XSS audit, CSRF for forms |

### WAVE 2: Enhancement (After Wave 1)
| Knight | Domain | Deliverable |
|--------|--------|-------------|
| SIR_FORGE | Code Gen | S6: QR Portal section (static first, WebSocket later) |
| SIR_FORGE | Code Gen | Expand glossary table (5+ entries) |
| SIR_FORGE | Code Gen | SEO meta tags + OG tags |
| SIR_DEBUG | Testing | Cross-browser test, mobile audit, Lighthouse |

### WAVE 3: Polish (After Wave 2)
| Knight | Domain | Deliverable |
|--------|--------|-------------|
| SIR_FORGE | Code Gen | Performance: critical CSS, preloads, lazy loading |
| SIR_FORGE | Code Gen | Accessibility: ARIA labels, focus management |
| SIR_DEBUG | Testing | Full regression + UAT checklist |
| SIR_SENTINEL | Security | Final security sweep |

---

## IV. FILE STRATEGY

All changes go into the existing `page.author-landing.liquid` template.
No Shopify section refactor (would break live page).
Additions are appended in-place to maintain the monolithic pattern.

### Files to Modify:
- `templates/page.author-landing.liquid` - Main portal (all sections)

### Files to Create (in theme assets, optional):
- `assets/phoenix-portal.css` - Extract critical CSS (Wave 3)
- `assets/phoenix-portal.js` - Extract JS (Wave 3)

### Shopify Admin Config:
- Create page "Phoenix Portal" using template `page.author-landing`
- Configure Klaviyo form/list (requires Klaviyo account)
- Add GA4 measurement ID to theme settings or hardcode

---

## V. BEAVER MODE PROTOCOL

1. **Build smallest shippable unit first** - Lead capture modal (S8)
2. **Self-error-check after each section** - Validate HTML, test JS in console
3. **No speculative code** - Only build what the spec requires
4. **Push after each wave** - Deploy to Shopify, verify live
5. **Measure twice, cut once** - Read existing code before modifying
6. **Rollback plan** - Theme pull before each push = local backup

---

## VI. DEPENDENCY MAP

```
S8 (Lead Modal) ──> Shopify Customer API (needs API token or form action)
S8 (Lead Modal) ──> Klaviyo (needs Klaviyo public API key)
S9 (Exit Intent) ──> S8 (reuses modal)
S6 (QR Portals) ──> WebSocket server (deferred - use static counters first)
Analytics ──> GA4 Measurement ID
Analytics ──> Meta Pixel ID
```

### Blockers Requiring User Input:
1. **GA4 Measurement ID** - needed for analytics
2. **Meta Pixel ID** - needed for retargeting
3. **Klaviyo Public API Key** - needed for email capture
4. **PDF download URL** - for "Skeleton Key" book delivery
5. **QR code image URLs** - or generate via Canvas API

---

## VII. RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|------------|
| Monolithic file grows too large | Maintainability | Extract CSS/JS in Wave 3 |
| Shopify Liquid restrictions | Can't use server-side logic | Client-side JS for all dynamic features |
| No server for WebSocket | QR real-time counters won't work | Use static counters with localStorage |
| Klaviyo not configured | No email capture backend | Fallback to Shopify form submission |
| Video CDN failure | Blank cinema screen | Add poster image fallback |
