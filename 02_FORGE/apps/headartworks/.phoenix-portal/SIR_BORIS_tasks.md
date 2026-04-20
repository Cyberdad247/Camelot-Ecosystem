# SIR_BORIS — Phoenix Portal Task Sheet
# Knight: SIR_BORIS v3.0 (Foundry Lead / Orchestrator)
# Mode: BEAVER | Crucible Conductor
# Scope: Coordination, Quality Gates, Deployment

---

## ORCHESTRATION TASKS

### T0.1: Pre-Flight Backup [CRITICAL]
**Priority:** P0 | **Before any code changes**

- [ ] Pull current live theme to backup directory
- [ ] Verify backup is complete and matches live
- [ ] Document current template line count (945 lines)

```bash
shopify theme pull --store headartwork.myshopify.com \
  --password shptka_*** --theme 175658238271 \
  --path ~/CAMELOT_OS/02_FORGE/apps/headartworks-backup \
  --only templates/page.author-landing.liquid
```

---

### T0.2: Collect External API Keys [BLOCKER]
**Priority:** P0 | **Blocks Wave 1 analytics + email**

**Required from user:**
- [ ] GA4 Measurement ID (G-XXXXXXXXXX)
- [ ] Meta Pixel ID (numeric)
- [ ] Klaviyo Public API Key (pk_*)
- [ ] Klaviyo List ID for Phoenix Portal subscribers
- [ ] PDF download URL for "Skeleton Key" book

**Nice-to-have:**
- [ ] QR code image URLs (or generate client-side)
- [ ] Video poster/thumbnail image URL

---

### T0.3: Wave Gate Reviews [ONGOING]

**Wave 1 Gate (Foundation):**
- [ ] SIR_FORGE: T1.1 (Lead Modal) complete + self-checked
- [ ] SIR_FORGE: T1.2 (Exit Intent) complete + self-checked
- [ ] SIR_SENTINEL: T1.S1 (Input Sanitization) audit passed
- [ ] SIR_SENTINEL: T1.S2 (CSRF) audit passed
- [ ] LADY_APIS: T1.A1-A3 integration code ready (or marked BLOCKED)
- [ ] BORIS: Code review of all Wave 1 changes
- [ ] BORIS: Push to Shopify, verify on live store
- [ ] BORIS: Log to PROVENANCE_LEDGER

**Wave 2 Gate (Enhancement):**
- [ ] SIR_FORGE: T2.1 (QR Portals) complete
- [ ] SIR_FORGE: T2.2 (Glossary expansion) complete
- [ ] SIR_FORGE: T2.3 (SEO/OG tags) complete
- [ ] SIR_DEBUG: T2.D1 (Cross-browser) audit passed
- [ ] SIR_DEBUG: T2.D2 (Mobile UX) audit passed
- [ ] LADY_APIS: T2.A1 (UTM System) complete
- [ ] BORIS: Push to Shopify, verify on live store
- [ ] BORIS: Log to PROVENANCE_LEDGER

**Wave 3 Gate (Polish):**
- [ ] SIR_FORGE: T3.1 (Performance) complete
- [ ] SIR_FORGE: T3.2 (Accessibility) complete
- [ ] SIR_DEBUG: T2.D3 (Lighthouse) scores meet targets
- [ ] SIR_DEBUG: T3.D1 (Full regression) PASS
- [ ] SIR_SENTINEL: T3.S1 (Final security sweep) PASS
- [ ] BORIS: Final push + production verification
- [ ] BORIS: Close PROVENANCE_LEDGER entry

---

### T0.4: Deployment Protocol [PER-WAVE]

```bash
# 1. Backup current live state
shopify theme pull --store headartwork.myshopify.com \
  --password $THEME_PWD --theme 175658238271 \
  --path ~/CAMELOT_OS/02_FORGE/apps/headartworks-pre-wave-N \
  --only templates/page.author-landing.liquid

# 2. Push changes
shopify theme push --store headartwork.myshopify.com \
  --password $THEME_PWD --theme 175658238271 \
  --path ~/CAMELOT_OS/02_FORGE/apps/headartworks \
  --only templates/page.author-landing.liquid

# 3. Verify live
# Open: https://headartwork.myshopify.com/pages/[phoenix-portal-slug]
# Run SIR_DEBUG post-push checklist

# 4. If broken: ROLLBACK
shopify theme push --store headartwork.myshopify.com \
  --password $THEME_PWD --theme 175658238271 \
  --path ~/CAMELOT_OS/02_FORGE/apps/headartworks-pre-wave-N \
  --only templates/page.author-landing.liquid
```

---

### T0.5: PROVENANCE_LEDGER Entry [PER-WAVE]

Template:
```markdown
## [2026-04-11] - PHOENIX_PORTAL_WAVE_N (Operation Phoenix Forge)
*   **[KINETIC]** :: `page.author-landing.liquid` — [description of changes]
*   **[VERIFY]** :: SIR_DEBUG regression: PASS. Lighthouse: Perf X / A11y X.
*   **[SENTINEL]** :: Security sweep: CLEAR. No XSS, no exposed keys.
*   **[STATUS]** :: RADIANT. Wave N deployed to headartwork.myshopify.com.
---
*Synchronized by SIR_BORIS — [timestamp]*
```

---

## BEAVER MODE RULES (Enforced by Boris)

1. **No gold-plating** - Ship what's needed, nothing more
2. **Self-check before escalation** - Knights verify own work first
3. **Wave gates are hard gates** - No Wave 2 work until Wave 1 ships
4. **One template, one push** - All changes in single file per wave
5. **Backup before every push** - No exceptions
6. **Console zero** - Zero JS errors on live site or it doesn't ship
