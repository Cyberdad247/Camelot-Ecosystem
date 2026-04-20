# SIR_BORIS — Verification Checklist
# Knight: SIR_BORIS v3.0 | Domain: Orchestration / Quality Gates
# Store: headartwork.myshopify.com

---

## WAVE GATE PROTOCOL

### Gate Check Template (Copy per wave)
```
WAVE [N] GATE CHECK — SIR_BORIS
Date: ____
Template size: ____ lines (was 945)

KNIGHT SIGN-OFFS:
  SIR_FORGE:    [ ] Tasks complete  [ ] Self-checked
  SIR_SENTINEL: [ ] Audit passed    [ ] No blockers
  SIR_DEBUG:    [ ] Tests passed    [ ] No P0/P1 bugs
  LADY_APIS:    [ ] Integrated      [ ] Or BLOCKED (reason: ____)

PRE-PUSH:
  [ ] Backup pulled to headartworks-pre-wave-N/
  [ ] Template has no Liquid syntax errors
  [ ] No API keys/secrets in template source
  [ ] File size reasonable (< 2000 lines)

POST-PUSH:
  [ ] Live page loads without errors
  [ ] Trailer flow works (new visitor)
  [ ] Skip flow works (return visitor)
  [ ] New features functional
  [ ] No regression in existing features
  [ ] Console: zero errors

DECISION: [ ] SHIP  [ ] HOLD  [ ] ROLLBACK
LEDGER:   [ ] Logged to PROVENANCE_LEDGER.md
```

---

## DEPLOYMENT VERIFICATION

### Push Success Indicators
- [ ] Shopify CLI reports "theme pushed successfully"
- [ ] No Liquid compilation errors
- [ ] Page accessible at store URL
- [ ] No 404 or 500 errors

### Rollback Triggers (Any one = ROLLBACK)
- Page returns 500 error
- Blank white/black screen (no content)
- JavaScript error prevents portal entry
- Lead capture modal completely broken
- Existing sections (trailer, hero, bio) broken

---

## NORTH STAR TRACKING

### Completion Dashboard
| Component | Wave | Status | Verified |
|-----------|------|--------|----------|
| Cinematic Gateway (S1) | Existing | DONE | [ ] |
| Hero Portal (S2) | Existing | DONE | [ ] |
| Master Locksmith (S3) | Existing | DONE | [ ] |
| Streamed Revolution (S4) | Existing | DONE | [ ] |
| Glossary Table (S5) | W2 | TODO | [ ] Expand |
| QR Portals (S6) | W2 | TODO | [ ] |
| Network Bridge (S7) | Existing | DONE | [ ] |
| Lead Capture Modal (S8) | W1 | TODO | [ ] |
| Exit Intent (S9) | W1 | TODO | [ ] |
| GA4 Analytics | W1 | BLOCKED | [ ] Need ID |
| Meta Pixel | W1 | BLOCKED | [ ] Need ID |
| Klaviyo Email | W1 | BLOCKED | [ ] Need keys |
| UTM Tracking | W2 | TODO | [ ] |
| SEO/OG Tags | W2 | TODO | [ ] |
| Performance | W3 | TODO | [ ] |
| Accessibility | W3 | TODO | [ ] |

### North Star Metric
> **Conversion Rate:** Visitors who complete lead capture / Total portal entries
> Target: > 5% (industry benchmark for landing pages)

---

## FINAL SIGN-OFF

```
PHOENIX PORTAL — FINAL VERIFICATION
Date: ____
Store: headartwork.myshopify.com
Theme: Main (#175658238271)
Template: page.author-landing.liquid

ALL WAVES COMPLETE: [ ] YES  [ ] NO
TOTAL TEMPLATE SIZE: ____ lines
LIGHTHOUSE: Perf ____ / A11y ____ / BP ____ / SEO ____
SECURITY: [ ] CLEAR
REGRESSION: [ ] PASS

KNIGHT COUNCIL SIGN-OFF:
  SIR_FORGE:    [ ] Approved
  SIR_SENTINEL: [ ] Approved
  SIR_DEBUG:    [ ] Approved
  LADY_APIS:    [ ] Approved
  SIR_BORIS:    [ ] Approved — SHIP IT

PROVENANCE_LEDGER: [ ] Final entry logged
STATUS: RADIANT / PARTIAL / HOLD
```
