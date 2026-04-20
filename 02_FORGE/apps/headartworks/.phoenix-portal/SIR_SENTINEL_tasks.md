# SIR_SENTINEL — Phoenix Portal Task Sheet
# Knight: SIR_SENTINEL (Security / Audit)
# Mode: BEAVER | Self-Error-Check: ON
# Target: templates/page.author-landing.liquid

---

## WAVE 1 TASKS

### T1.S1: Form Input Sanitization [CRITICAL]
**Priority:** P0 | **Scope:** Lead Capture Modal (S8)

**Requirements:**
- Sanitize all form inputs before display or submission
- Prevent XSS via Name, Email, Phone fields
- Email validation: RFC 5322 pattern (client-side)
- Phone validation: digits + optional formatting chars only
- Name validation: strip HTML tags, max 100 chars
- No `innerHTML` with user data (use `textContent`)

**Audit Points:**
- [ ] No `innerHTML` assignment with user-controlled data
- [ ] Email regex rejects `<script>`, `javascript:`, `data:`
- [ ] Phone field rejects non-numeric (except +, -, (, ), space)
- [ ] Name field strips all HTML tags
- [ ] Form action URL is HTTPS
- [ ] No eval(), no Function() constructor in JS

---

### T1.S2: CSRF Protection [HIGH]
**Priority:** P1 | **Scope:** Form submission

**Requirements:**
- If submitting to Shopify API: verify CORS headers
- If submitting to Klaviyo: use public API key (not private)
- No API secrets in client-side code
- Rate limit form submission (1 per 10 seconds)

**Audit Points:**
- [ ] No API secret keys in page source
- [ ] Form cannot be submitted more than once per 10s
- [ ] Submission endpoint uses HTTPS
- [ ] No credentials stored in localStorage (only sessionStorage)

---

## WAVE 3 TASKS

### T3.S1: Final Security Sweep [HIGH]
**Priority:** P1 | **Scope:** Entire template

**Audit Checklist:**
- [ ] No inline `onclick` with unsanitized data
- [ ] All external links have `rel="noopener noreferrer"`
- [ ] No mixed content (HTTP resources on HTTPS page)
- [ ] Video sources use HTTPS CDN URLs
- [ ] YouTube embeds use `https://www.youtube.com/embed/`
- [ ] No `target="_blank"` without `rel="noopener"`
- [ ] sessionStorage keys namespaced (prefix: `phoenix_`)
- [ ] No sensitive data in URL parameters
- [ ] Content-Security-Policy compatible (no inline eval)
- [ ] UTM parameters are read-only (never written to DOM unsanitized)

**Self-Error-Check:**
- [ ] Run page through browser security audit (DevTools > Security tab)
- [ ] Check all external resource URLs resolve (no 404s)
- [ ] Verify no console warnings about mixed content
- [ ] Test form with malicious input strings (XSS payloads)
