# SIR_DEBUG — Verification Checklist
# Knight: SIR_DEBUG | Domain: Testing / QA / PIV Self-Healing
# Store: headartwork.myshopify.com

---

## AUTOMATED CHECKS (Run before each push)

### HTML Validation
```bash
# Validate HTML structure (count open vs close tags)
grep -c '<div' templates/page.author-landing.liquid
grep -c '</div>' templates/page.author-landing.liquid
# Counts must match

# Check for duplicate IDs
grep -oP 'id="[^"]*"' templates/page.author-landing.liquid | sort | uniq -d
# Must be empty
```

### JS Console Check
```javascript
// Paste in browser console after page load
// Should return 0
window.onerror = (msg) => console.error('CAUGHT:', msg);
console.log('Error listeners active');
```

---

## VISUAL REGRESSION MATRIX

### Desktop (1920x1080)
| Section | Renders | Animates | Interactive |
|---------|---------|----------|-------------|
| Trailer | [ ] | [ ] | [ ] Audio/Skip/Enter |
| Hero | [ ] | [ ] | [ ] CTA button |
| Bio/Interview | [ ] | [ ] | [ ] YouTube play |
| Streamed Revolution | [ ] | [ ] | [ ] YouTube play |
| Glossary Table | [ ] | [ ] | [ ] Row hover |
| QR Portals | [ ] | [ ] | [ ] Download |
| Network Bridge | [ ] | [ ] | [ ] Link hover |
| Lead Modal | [ ] | [ ] | [ ] Form submit |
| Exit Intent | [ ] | [ ] | [ ] CTA/Dismiss |

### Mobile (375x812)
| Section | Renders | Animates | Interactive |
|---------|---------|----------|-------------|
| Trailer | [ ] | [ ] | [ ] Audio/Skip/Enter |
| Hero | [ ] | [ ] | [ ] CTA button |
| Bio/Interview | [ ] | [ ] | [ ] YouTube play |
| Streamed Revolution | [ ] | [ ] | [ ] YouTube play |
| Glossary Table | [ ] | [ ] | [ ] Scroll/Tap |
| QR Portals | [ ] | [ ] | [ ] Download |
| Network Bridge | [ ] | [ ] | [ ] Link tap |
| Lead Modal | [ ] | [ ] | [ ] Form submit |

---

## PERFORMANCE BENCHMARKS

| Metric | Target | Actual | Pass? |
|--------|--------|--------|-------|
| First Contentful Paint | < 1.5s | | [ ] |
| Largest Contentful Paint | < 2.5s | | [ ] |
| Total Blocking Time | < 200ms | | [ ] |
| Cumulative Layout Shift | < 0.1 | | [ ] |
| Initial Transfer Size | < 100KB | | [ ] |
| Total Requests (initial) | < 15 | | [ ] |
| Lighthouse Performance | > 85 | | [ ] |
| Lighthouse Accessibility | > 90 | | [ ] |

---

## BUG SEVERITY CLASSIFICATION

| Severity | Definition | Action |
|----------|-----------|--------|
| P0 - Blocker | Page won't load, modal broken, form loses data | Fix immediately, block push |
| P1 - Critical | Section doesn't render, animation broken, XSS | Fix before push |
| P2 - Major | Visual glitch on specific browser, slow load | Fix in same wave |
| P3 - Minor | Cosmetic issue, minor alignment off | Fix in next wave |
| P4 - Enhancement | Polish, nice-to-have | Backlog |

---

## SIGN-OFF

After all checks pass:
```
SIR_DEBUG VERIFICATION: [WAVE X] COMPLETE
Date: ____
Browser Matrix: ____/6 pass
Mobile Matrix: ____/6 pass  
Lighthouse: Perf ____ / A11y ____ / BP ____ / SEO ____
Console Errors: 0
Regression: PASS / FAIL
Recommendation: SHIP / HOLD / ROLLBACK
```
