# SIR_FORGE — Verification Checklist
# Knight: SIR_FORGE | Domain: Engineering / Code Gen
# Store: headartwork.myshopify.com | Theme: Main (#175658238271)

---

## PRE-PUSH GATE (Before every `shopify theme push`)

### HTML Validity
- [ ] No unclosed tags (match every `<div>` with `</div>`)
- [ ] No duplicate IDs in document
- [ ] All `onclick` handlers reference existing functions
- [ ] All `href="#id"` targets exist in document
- [ ] Template renders without Liquid errors

### CSS Validity
- [ ] No syntax errors (unclosed braces, missing semicolons)
- [ ] No conflicting z-index layers
- [ ] All color values use hex or rgba (consistent)
- [ ] Media queries have matching closing braces
- [ ] No `!important` unless overriding third-party

### JS Validity
- [ ] No `console.error` on page load
- [ ] All `getElementById` targets exist in DOM
- [ ] All event listeners have matching cleanup
- [ ] No global variable collisions
- [ ] `sessionStorage` operations wrapped in try/catch

---

## SECTION-BY-SECTION VERIFICATION

### S8: Lead Capture Modal
| Test | Expected | Method |
|------|----------|--------|
| Click "Claim Your Skeleton Key" | Modal opens | Manual click |
| Click "Download Free Book" | Modal opens | Manual click |
| Submit empty form | Validation errors on Name + Email | Manual submit |
| Submit valid form | Loading state -> Success state | Manual submit |
| Click overlay background | Modal closes | Manual click |
| Press Escape | Modal closes | Keyboard |
| Click X button | Modal closes | Manual click |
| Open modal, check scroll | Body scroll disabled | Scroll attempt |
| Close modal, check scroll | Body scroll restored | Scroll attempt |
| Mobile 375px | Modal full-width, fields stacked | DevTools |
| Enter `<script>alert(1)</script>` in Name | Sanitized, no XSS | Manual input |

### S9: Exit Intent
| Test | Expected | Method |
|------|----------|--------|
| Move mouse above viewport | Exit overlay appears | Mouse movement |
| Exit overlay, click primary CTA | Lead modal opens | Manual click |
| Exit overlay, click dismiss | Overlay closes | Manual click |
| Trigger exit, dismiss, move mouse out again | Does NOT re-trigger | Mouse movement |
| Capture lead first, then mouseout | Does NOT trigger | Mouse movement |
| Mobile: rapid upward scroll | Exit overlay appears | Touch scroll |

### S6: QR Portals
| Test | Expected | Method |
|------|----------|--------|
| Section scrolls into view | Cards animate in with stagger | Scroll |
| Click download on QR card | PNG downloads | Manual click |
| Counter displays | Number visible, formatted | Visual check |
| Mobile 375px | Cards stack vertically | DevTools |

### SEO / Meta
| Test | Expected | Method |
|------|----------|--------|
| View page source | OG tags in `<head>` | View Source |
| Share URL on social | Preview shows title + image + desc | Social debugger |
| Google `site:headartwork.myshopify.com` | Description appears | Search (delayed) |

### Performance
| Test | Expected | Method |
|------|----------|--------|
| Lighthouse audit | Performance > 85 | Chrome DevTools |
| Initial page weight | < 100KB (before YouTube) | Network tab |
| Video load failure | Poster image shows | Throttle network |
| 30s no interaction | Auto-enter fires | Wait 30s |

### Accessibility
| Test | Expected | Method |
|------|----------|--------|
| Tab through page | Logical focus order | Keyboard only |
| Modal focus trap | Focus stays inside modal | Tab while modal open |
| Screen reader | Modal announced properly | NVDA/VoiceOver |
| prefers-reduced-motion | Animations disabled | OS setting |
| Lighthouse a11y | Score > 90 | Chrome DevTools |

---

## POST-PUSH VERIFICATION (Live on headartwork.myshopify.com)

### Live Store Checks
- [ ] Navigate to Phoenix Portal page URL
- [ ] Trailer plays (muted, looped)
- [ ] Audio toggle works
- [ ] Enter portal -> main content visible, scroll enabled
- [ ] Return visit -> trailer skipped (sessionStorage)
- [ ] All YouTube embeds load on click
- [ ] Lead capture modal opens and submits
- [ ] Exit intent fires (desktop only)
- [ ] All external links open in new tab
- [ ] No console errors
- [ ] Mobile (real device): full flow works

### Cross-Browser Matrix
| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome 124+ | [ ] | [ ] |
| Safari 17+ | [ ] | [ ] (iOS) |
| Firefox 125+ | [ ] | [ ] |
| Edge 124+ | [ ] | N/A |

---

## ROLLBACK PROCEDURE
If push breaks live site:
```bash
# Pull last known good state
shopify theme pull --store headartwork.myshopify.com \
  --password shptka_*** --theme 175658238271 \
  --path ~/CAMELOT_OS/02_FORGE/apps/headartworks-backup

# Restore from local backup
shopify theme push --store headartwork.myshopify.com \
  --password shptka_*** --theme 175658238271 \
  --path ~/CAMELOT_OS/02_FORGE/apps/headartworks-backup \
  --only templates/page.author-landing.liquid
```
