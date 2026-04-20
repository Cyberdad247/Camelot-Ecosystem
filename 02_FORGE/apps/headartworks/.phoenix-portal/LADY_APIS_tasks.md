# LADY_APIS — Phoenix Portal Task Sheet
# Knight: LADY_APIS (Research / Growth / Context)
# Mode: BEAVER | Self-Error-Check: ON
# Target: Analytics + Email integration for Phoenix Portal

---

## WAVE 1 TASKS

### T1.A1: GA4 Analytics Integration [HIGH]
**Priority:** P1 | **Est. Lines:** ~40 JS

**Requirements:**
- Google Analytics 4 integration via gtag.js
- Events to track:
  | Event Name | Trigger | Parameters |
  |------------|---------|------------|
  | `page_view` | Page load | page_title, page_location |
  | `trailer_started` | Trailer begins | source (direct/qr) |
  | `audio_enabled` | Audio toggle on | - |
  | `trailer_completed` | Video ends naturally | duration |
  | `trailer_skipped` | Skip/Enter clicked | time_watched |
  | `portal_entered` | Main content shown | method (auto/click/video_end) |
  | `video_played` | YouTube embed clicked | video_id, section |
  | `cta_clicked` | Any CTA button | cta_text, section |
  | `lead_modal_opened` | Modal displayed | trigger (cta/exit_intent) |
  | `lead_captured` | Form submitted | has_phone (bool) |
  | `exit_intent_fired` | Exit overlay shown | time_on_page |
  | `external_link` | Network bridge link | destination |

**Implementation:**
- gtag.js snippet in `<head>` (async, non-blocking)
- `gtag('event', ...)` calls at each trigger point
- UTM parameter extraction and forwarding

**Self-Error-Check:**
- [ ] gtag.js loads without blocking render
- [ ] All 12 events fire in GA4 DebugView
- [ ] UTM parameters appear in GA4 acquisition reports
- [ ] No duplicate page_view events
- [ ] Events fire exactly once per trigger (no double-fire)

**BLOCKER:** Needs GA4 Measurement ID (G-XXXXXXXXXX) from user.

---

### T1.A2: Meta Pixel Integration [HIGH]
**Priority:** P1 | **Est. Lines:** ~30 JS

**Requirements:**
- Meta (Facebook) Pixel for retargeting
- Events:
  | Pixel Event | Trigger |
  |-------------|---------|
  | `PageView` | Page load |
  | `ViewContent` | Portal entered (past trailer) |
  | `Lead` | Form submitted |
  | `CompleteRegistration` | Download initiated |

**Implementation:**
- Meta Pixel base code in `<head>`
- `fbq('track', ...)` calls at trigger points

**Self-Error-Check:**
- [ ] Pixel fires on page load (check Meta Pixel Helper extension)
- [ ] Lead event fires on form submit
- [ ] No duplicate PageView events
- [ ] Pixel doesn't block page render

**BLOCKER:** Needs Meta Pixel ID from user.

---

### T1.A3: Klaviyo Email Integration [CRITICAL]
**Priority:** P0 | **Est. Lines:** ~50 JS

**Requirements:**
- Klaviyo identify + subscribe on form submit
- Use Klaviyo Client API (public key only, client-safe)
- Create/update profile with: email, first_name, phone (optional)
- Subscribe to list (needs list ID)
- Tag profile: `phoenix_lead`, `source:portal`
- Custom properties: utm_source, utm_medium, utm_campaign

**Integration Pattern:**
```javascript
// Klaviyo Client API (no server needed)
fetch('https://a.klaviyo.com/client/subscriptions/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'revision': '2024-02-15'
  },
  body: JSON.stringify({
    data: {
      type: 'subscription',
      attributes: {
        custom_source: 'Phoenix Portal',
        profile: {
          data: {
            type: 'profile',
            attributes: {
              email: formEmail,
              first_name: formName,
              phone_number: formPhone,
              properties: { source: 'phoenix_portal', ...utmParams }
            }
          }
        }
      },
      relationships: {
        list: { data: { type: 'list', id: 'LIST_ID' } }
      }
    }
  })
});
```

**Self-Error-Check:**
- [ ] Only PUBLIC API key used (starts with `pk_`)
- [ ] Profile created in Klaviyo on submit
- [ ] Profile tagged correctly
- [ ] UTM properties attached
- [ ] Error handling: show user-friendly message on API failure
- [ ] Rate limited (prevent spam submissions)

**BLOCKERS:**
- Klaviyo Public API Key
- Klaviyo List ID for Phoenix Portal subscribers

---

## WAVE 2 TASKS

### T2.A1: UTM Parameter System [HIGH]
**Priority:** P1 | **Est. Lines:** ~25 JS

**Requirements:**
- Parse URL parameters on page load
- Store in sessionStorage: utm_source, utm_medium, utm_campaign, utm_content, utm_term
- Forward to: GA4 (automatic via gtag), Meta Pixel, Klaviyo, hidden form fields
- Special handling: `?utm_source=qr` triggers QR scan tracking

**Self-Error-Check:**
- [ ] Landing with `?utm_source=qr&utm_medium=print` captures both
- [ ] Parameters persist through session (page refresh)
- [ ] Parameters included in lead capture form submission
- [ ] No URL parameters leak into visible UI

---

## RESEARCH DELIVERABLES

### R1: Shopify Customer Creation (Alternative to Klaviyo)
If Klaviyo not available, document how to create Shopify customers via:
- Shopify Forms app (free, native)
- Shopify Customer API via Ajax
- Third-party form builder (Privy, OptinMonster)

### R2: QR Code Generation
- Document best approach for generating QR codes client-side
- Evaluate: qrcode.js vs Canvas API vs pre-generated images
- Recommendation with code snippet
