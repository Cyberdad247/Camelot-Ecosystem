# Fixture: mobile_permission_denied

Device action requested without the required Android OS permission (e.g.
SMS send with permission revoked). The Android permission broker must deny
the action; no effect proceeds without the §10.1 condition set.

Verify: `OS_permission_flow_verified` fires; action denied; no bypass via
lease or confirmation alone (§10.1).
