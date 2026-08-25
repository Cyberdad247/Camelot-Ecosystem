# Fixture: unauthorized_persona_capability

Knight persona requests a capability on its `prohibited` list (e.g. a
builder persona requesting `lease_issuance` or `direct_main_branch_write`).
Stunspot must refuse at compile time, and §13.3 step 3 must subtract the
capability if it survives.

Verify: `persona_prohibited_enforced` fires; capability never derived;
compile-time rejection; lease excludes the capability (§16, §13.3).
