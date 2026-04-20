# SIR_DEBUG — Phoenix Portal Task Sheet
# Knight: SIR_DEBUG (Testing / QA / Self-Healing)
# Mode: BEAVER | Self-Error-Check: ON
# Target: Live page on headartwork.myshopify.com

---

## WAVE 2 TASKS

### T2.D1: Cross-Browser Compatibility Audit [HIGH]
**Priority:** P1

**Test Matrix:**
| Browser | Version | Platform | Status |
|---------|---------|----------|--------|
| Chrome | 124+ | Windows/Mac | [ ] |
| Safari | 17+ | Mac/iOS | [ ] |
| Firefox | 125+ | Windows/Mac | [ ] |
| Edge | 124+ | Windows | [ ] |
| Chrome | Mobile | Android | [ ] |
| Safari | Mobile | iOS 17+ | [ ] |

**Focus Areas:**
- Video autoplay behavior (muted required for all browsers)
- CSS `inset` property support (older Safari may need fallback)
- `backdrop-filter: blur()` support (Firefox needs `-webkit-` prefix)
- IntersectionObserver support (universal in modern browsers)
- sessionStorage availability (private browsing may restrict)

**Self-Error-Check:**
- [ ] Each browser loads page without JS errors
- [ ] Trailer video plays (muted) on all browsers
- [ ] Animations trigger on scroll in all browsers
- [ ] Modal opens/closes in all browsers
- [ ] YouTube embeds load in all browsers

---

### T2.D2: Mobile UX Audit [HIGH]
**Priority:** P1

**Device Breakpoints:**
| Width | Device Class | Status |
|-------|-------------|--------|
| 320px | iPhone SE | [ ] |
| 375px | iPhone 12/13/14 | [ ] |
| 390px | iPhone 14 Pro | [ ] |
| 412px | Pixel 7 | [ ] |
| 768px | iPad Mini | [ ] |
| 1024px | iPad Pro | [ ] |

**Mobile-Specific Tests:**
- [ ] Trailer video plays on mobile (autoplay+muted+playsinline)
- [ ] Audio toggle button reachable with thumb
- [ ] Skip button reachable with thumb
- [ ] Text readable without zooming (min 16px body)
- [ ] CTA buttons have min 44x44px touch target
- [ ] Modal is full-width on mobile
- [ ] Form fields don't zoom on focus (font-size >= 16px)
- [ ] Glossary table scrolls horizontally or adapts
- [ ] Network links stack vertically on mobile
- [ ] No horizontal overflow at any breakpoint

---

### T2.D3: Lighthouse Audit [MEDIUM]
**Priority:** P2

**Target Scores:**
| Category | Target | Current |
|----------|--------|---------|
| Performance | > 85 | TBD |
| Accessibility | > 90 | TBD |
| Best Practices | > 90 | TBD |
| SEO | > 90 | TBD |

**Common Issues to Check:**
- [ ] Largest Contentful Paint < 2.5s
- [ ] First Input Delay < 100ms
- [ ] Cumulative Layout Shift < 0.1
- [ ] Images have alt text
- [ ] Color contrast ratio >= 4.5:1 (gold #d4af37 on #050505)
- [ ] Interactive elements have accessible names
- [ ] Page has valid `<title>` and `<meta description>`

---

## WAVE 3 TASKS

### T3.D1: Full Regression Test [HIGH]
**Priority:** P1

**User Journey: First-Time Visitor**
1. [ ] Land on page -> Trailer plays (muted, looped)
2. [ ] Click audio toggle -> Audio on, video restarts, skip hidden
3. [ ] Video ends -> Auto-transition to hero
4. [ ] Hero animates in (scale + fade)
5. [ ] Scroll -> Master Locksmith section animates (slide in)
6. [ ] Click interview play button -> YouTube loads
7. [ ] Scroll -> Streamed Revolution animates
8. [ ] Click playlist play button -> YouTube loads
9. [ ] Scroll -> Glossary table rows stagger in
10. [ ] Scroll -> QR Portals section animates (if built)
11. [ ] Scroll -> Network Bridge links stagger in
12. [ ] Click "Claim Your Skeleton Key" -> Modal opens
13. [ ] Fill form, submit -> Success state, download available
14. [ ] Close modal -> Scroll restored
15. [ ] Try to leave page -> Exit intent does NOT fire (lead captured)

**User Journey: Return Visitor**
1. [ ] Land on page -> Trailer SKIPPED
2. [ ] Hero visible immediately
3. [ ] Scroll enabled from start
4. [ ] All sections animate on scroll

**User Journey: QR Scanner**
1. [ ] Land with ?utm_source=qr -> Trailer plays
2. [ ] UTM params captured in hidden form fields
3. [ ] Same flow as first-time

**Edge Cases:**
- [ ] Rapid click "Enter Portal" multiple times -> No double transition
- [ ] Open modal, close, open again -> Works correctly
- [ ] Slow network (3G) -> Video shows poster, page still functional
- [ ] JavaScript disabled -> Graceful degradation (static content visible)
- [ ] Clear sessionStorage -> Trailer shows again

**Self-Error-Check:**
- [ ] Zero console errors through entire flow
- [ ] Zero console warnings (except expected deprecations)
- [ ] No layout shifts during animations
- [ ] No memory leaks (check performance tab after 5 min)
