# Fixture: receipt_parent_hash_tamper

An attacker rewrites `parent_hash` on a previously appended receipt to break
or redirect the hash link. Verification must detect the chain break via the
§11.3 rule (re-derivation + height continuity).

Verify: `tamper_detection_verified` catches the rewrite; `receipt_chain_verified`
fails at the broken link; ledger anchor at the next interval still verifies
against the pre-tamper chain (§11.3).
