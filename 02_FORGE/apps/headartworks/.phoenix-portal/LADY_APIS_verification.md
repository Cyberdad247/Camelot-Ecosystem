# LADY_APIS — Verification Checklist
# Knight: LADY_APIS | Domain: Research / Growth / Analytics
# Store: headartwork.myshopify.com

---

## GA4 VERIFICATION

### Setup
- [ ] gtag.js snippet present in `<head>`
- [ ] Measurement ID is correct (G-XXXXXXXXXX)
- [ ] Script loads async (non-render-blocking)

### Event Verification (GA4 DebugView)
| Event | Fires? | Parameters Correct? |
|-------|--------|-------------------|
| page_view | [ ] | [ ] page_title, page_location |
| trailer_started | [ ] | [ ] source |
| audio_enabled | [ ] | [ ] - |
| trailer_completed | [ ] | [ ] duration |
| trailer_skipped | [ ] | [ ] time_watched |
| portal_entered | [ ] | [ ] method |
| video_played | [ ] | [ ] video_id, section |
| cta_clicked | [ ] | [ ] cta_text, section |
| lead_modal_opened | [ ] | [ ] trigger |
| lead_captured | [ ] | [ ] has_phone |
| exit_intent_fired | [ ] | [ ] time_on_page |
| external_link | [ ] | [ ] destination |

### UTM Forwarding
- [ ] Visit with `?utm_source=test&utm_medium=test`
- [ ] Check GA4 > Acquisition > Traffic Source: params appear
- [ ] Verify no duplicate sessions created

---

## META PIXEL VERIFICATION

### Setup
- [ ] Pixel base code in `<head>`
- [ ] Pixel ID correct
- [ ] Meta Pixel Helper extension shows green icon

### Event Verification (Meta Events Manager)
| Event | Fires? | Deduplicated? |
|-------|--------|--------------|
| PageView | [ ] | [ ] (once per load) |
| ViewContent | [ ] | [ ] (once per portal entry) |
| Lead | [ ] | [ ] (once per form submit) |
| CompleteRegistration | [ ] | [ ] (once per download) |

---

## KLAVIYO VERIFICATION

### Setup
- [ ] Only PUBLIC key in client code (pk_*)
- [ ] No private/secret keys exposed
- [ ] API endpoint uses HTTPS

### Profile Creation
| Test | Expected | Status |
|------|----------|--------|
| Submit with email only | Profile created, email set | [ ] |
| Submit with name + email | Profile created, both fields | [ ] |
| Submit with all fields | Profile created, phone included | [ ] |
| Submit duplicate email | Profile updated (not duplicated) | [ ] |
| Submit with UTM params | Custom properties attached | [ ] |

### List Subscription
- [ ] Profile added to correct Klaviyo list
- [ ] Tags applied: `phoenix_lead`, `source:portal`
- [ ] Welcome flow triggered (if configured in Klaviyo)

### Error Handling
| Scenario | Expected Response |
|----------|------------------|
| Network offline | User sees "Connection error, try again" |
| Invalid API key | Graceful failure, form still works locally |
| Rate limited (429) | "Please wait a moment" message |
| Server error (500) | "Something went wrong" + retry button |

---

## UTM TRACKING VERIFICATION

### Parameter Capture
| URL | Expected Storage |
|-----|-----------------|
| `?utm_source=google&utm_medium=cpc` | Both captured |
| `?utm_source=qr` | QR scan tracked |
| `?utm_campaign=phoenix_launch` | Campaign captured |
| (no params) | Empty/null, no errors |
| `?utm_source=<script>alert(1)</script>` | Sanitized, no XSS |

### Parameter Flow
- [ ] Params stored in sessionStorage on landing
- [ ] Params forwarded to GA4 automatically
- [ ] Params included in Klaviyo profile properties
- [ ] Params included as hidden form fields
- [ ] Params persist across page sections (single-page)

---

## SIGN-OFF

```
LADY_APIS VERIFICATION: [WAVE X] COMPLETE
Date: ____
GA4 Events: ____/12 verified
Meta Pixel Events: ____/4 verified
Klaviyo Integration: PASS / FAIL / NOT_CONFIGURED
UTM Tracking: PASS / FAIL
Recommendation: SHIP / HOLD / NEEDS_API_KEYS
```
