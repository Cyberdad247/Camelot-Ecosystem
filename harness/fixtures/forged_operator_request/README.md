# Fixture: forged_operator_request

Operator request carrying a forged or replayed session proof (stale cookie,
replayed nonce, or forged signature). Sentinel must reject the request before
any policy evaluation or effect path.

Verify: request denied with `operator_request_signature_verified` failing;
no lease issued; replay window (60s, §12.2) enforced; MFA required for
operators (§13.1, §19.2).
