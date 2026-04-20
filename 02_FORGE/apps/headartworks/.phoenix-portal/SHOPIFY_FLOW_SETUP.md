# Shopify Flow + Email Automation Setup Guide
# Phoenix Portal | headartwork.myshopify.com
# No Klaviyo needed — 100% native Shopify

---

## STEP 1: Create Email Templates in Shopify Email

Go to: `headartwork.myshopify.com/admin/email`

Create 5 email templates (copy content from NotebookLM notebook or below):

| # | Template Name | Subject Line | Send Timing |
|---|--------------|--------------|-------------|
| 1 | Phoenix - Skeleton Key Delivered | The Vault Opens: Your Skeleton Key Awaits | Immediate |
| 2 | Phoenix - 300 Year Deception | The 300-Year Deception | Day 1 |
| 3 | Phoenix - Frequency of Awakening | Hear the Revelator | Day 3 |
| 4 | Phoenix - Master Locksmith | The Architect of the Portal | Day 5 |
| 5 | Phoenix - Forge Your Reality | Forge Your Own Reality | Day 7 |

### Email Design Notes:
- Background: Black (#050505)
- Text: Light gray (#e0e0e0)
- Accent/CTA: Gold (#d4af37)
- Font: Clean sans-serif (Helvetica Neue or similar)
- Header: Store logo
- Footer: Invisioned Marketing Inc. | Unsubscribe link

---

## STEP 2: Set Up Shopify Flow Automation

Go to: `headartwork.myshopify.com/admin/flow`

### Flow 1: Welcome (Immediate)
```
TRIGGER: Customer created
CONDITION: Customer tags CONTAINS "phoenix_lead"
ACTION: Send marketing email → "Phoenix - Skeleton Key Delivered"
```

### Flow 2: Day 1 Follow-up
```
TRIGGER: Customer created
CONDITION: Customer tags CONTAINS "phoenix_lead"
ACTION: Wait → 24 hours
ACTION: Send marketing email → "Phoenix - 300 Year Deception"
```

### Flow 3: Day 3 YouTube Push
```
TRIGGER: Customer created
CONDITION: Customer tags CONTAINS "phoenix_lead"
ACTION: Wait → 72 hours
ACTION: Send marketing email → "Phoenix - Frequency of Awakening"
```

### Flow 4: Day 5 Authority Builder
```
TRIGGER: Customer created
CONDITION: Customer tags CONTAINS "phoenix_lead"
ACTION: Wait → 120 hours
ACTION: Send marketing email → "Phoenix - Master Locksmith"
```

### Flow 5: Day 7 Conversion
```
TRIGGER: Customer created
CONDITION: Customer tags CONTAINS "phoenix_lead"
ACTION: Wait → 168 hours
ACTION: Send marketing email → "Phoenix - Forge Your Reality"
```

### Alternative: Single Flow with Wait Steps
Instead of 5 separate flows, you can create ONE flow:
```
TRIGGER: Customer created
CONDITION: Customer tags CONTAINS "phoenix_lead"
  → Send email: Skeleton Key Delivered
  → Wait 24 hours
  → Send email: 300 Year Deception
  → Wait 48 hours
  → Send email: Frequency of Awakening
  → Wait 48 hours
  → Send email: Master Locksmith
  → Wait 48 hours
  → Send email: Forge Your Reality
```

---

## STEP 3: Verify the Pipeline

### Test Checklist:
- [ ] Create a test customer with tag "phoenix_lead" in Shopify admin
- [ ] Verify Email 1 sends immediately
- [ ] Check email renders correctly (gold/black theme)
- [ ] Verify download link works in email
- [ ] Check unsubscribe link functions
- [ ] Wait 24h (or manually trigger) to verify Email 2
- [ ] Verify all 5 emails in sequence

### Monitor:
- Shopify Email dashboard: Open rates, click rates
- Shopify Flow: Execution history, errors
- Customer list: Filter by tag "phoenix_lead" to see growth

---

## COST: $0

- Shopify Email: Free for first 10,000 emails/month
- Shopify Flow: Free on all Shopify plans
- No third-party app needed
- No API keys needed

---

## LINKS

| Resource | URL |
|----------|-----|
| Shopify Email | headartwork.myshopify.com/admin/email |
| Shopify Flow | headartwork.myshopify.com/admin/flow |
| Customer List | headartwork.myshopify.com/admin/customers |
| NotebookLM | notebooklm.google.com/notebook/b55270dd-4e49-4da0-8044-668143c3e120 |
| Theme Editor | headartwork.myshopify.com/admin/themes/175658238271/editor |
