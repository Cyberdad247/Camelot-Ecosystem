# Fixture: forged_node_receipt

Node submits a receipt with a forged signer (e.g. `signer: "sentinel"`),
bad ed25519 signature, or `immutable_inputs` checksum mismatch. The receipt
service must reject it and refuse to link it into the tenant chain.

Verify: `receipt_signature_verified` fails for the forged receipt; chain
linkage refused; no chain discontinuity introduced (§11.3).
