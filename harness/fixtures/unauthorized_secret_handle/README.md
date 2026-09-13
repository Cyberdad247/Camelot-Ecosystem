# Fixture: unauthorized_secret_handle

Workload requests a named secret handle absent from its lease's `secrets`
scope (or attempts to export a secret value). The Secret Broker must deny
the handle and never return plaintext.

Verify: `secret_handle_authorization_verified` fails; no handle granted;
no plaintext export path exercised; denial recorded (§14.3).
