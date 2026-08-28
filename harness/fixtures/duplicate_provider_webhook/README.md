# Fixture: duplicate_provider_webhook

Provider (HubSpot/Stripe/Calendar/Mailchimp) delivers the same signed
webhook twice. The provider perimeter must verify the signature and
deduplicate on the idempotency key so the action executes exactly once.

Verify: `webhook_signature_verified` passes for both copies;
`idempotent_provider_action_verified` dedupes; single provider action;
no double charge/send (§20.x).
