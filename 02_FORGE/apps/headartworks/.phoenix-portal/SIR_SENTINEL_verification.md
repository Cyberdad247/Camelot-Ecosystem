# SIR_SENTINEL — Verification Checklist
# Knight: SIR_SENTINEL | Domain: Security / Agent-Armor
# Store: headartwork.myshopify.com

---

## INPUT VALIDATION TESTS

### XSS Attack Vectors (Must ALL be blocked)
| Input | Field | Expected Result |
|-------|-------|-----------------|
| `<script>alert('xss')</script>` | Name | Stripped, no execution |
| `<img src=x onerror=alert(1)>` | Name | Stripped, no execution |
| `javascript:alert(1)` | Email | Rejected by validation |
| `"><svg onload=alert(1)>` | Name | Stripped, no execution |
| `'; DROP TABLE users; --` | Email | Rejected by validation |
| `{{constructor.constructor('alert(1)')()}}` | Name | No template injection |

### Email Validation
| Input | Expected |
|-------|----------|
| `user@example.com` | PASS |
| `user+tag@example.com` | PASS |
| `user@sub.domain.com` | PASS |
| `@nouser.com` | FAIL |
| `user@` | FAIL |
| `user@.com` | FAIL |
| `<script>@evil.com` | FAIL |
| (empty) | FAIL (required) |

### Phone Validation
| Input | Expected |
|-------|----------|
| `555-123-4567` | PASS |
| `(555) 123-4567` | PASS |
| `+1 555 123 4567` | PASS |
| `<script>alert(1)</script>` | FAIL |
| `abcdefghij` | FAIL |
| (empty) | PASS (optional field) |

---

## API SECURITY

- [ ] No API keys with write/admin access in page source
- [ ] Klaviyo uses PUBLIC key only (starts with `pk_`)
- [ ] No Shopify Admin API tokens in client-side code
- [ ] Theme Access password NOT embedded in template
- [ ] Form submission rate limited (test rapid clicks)

---

## TRANSPORT SECURITY

- [ ] All resource URLs use HTTPS
- [ ] No mixed content warnings in browser console
- [ ] External links use `rel="noopener noreferrer"`
- [ ] YouTube embeds use HTTPS
- [ ] Shopify CDN video URLs use HTTPS
- [ ] No resources loaded from untrusted domains

---

## DATA HANDLING

- [ ] Only `sessionStorage` used (not `localStorage` for sensitive data)
- [ ] Session keys prefixed with `phoenix_`
- [ ] No PII stored in localStorage
- [ ] UTM parameters read but never written to DOM without sanitization
- [ ] Form data sent over HTTPS POST (not GET with query params)

---

## SEVERITY CLASSIFICATION

| Finding | Severity | Action |
|---------|----------|--------|
| XSS in form field | CRITICAL | Block push until fixed |
| API key exposed | CRITICAL | Block push, rotate key |
| Mixed content | HIGH | Fix before push |
| Missing rel="noopener" | MEDIUM | Fix in same wave |
| Console warning | LOW | Fix in next wave |
