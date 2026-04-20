# CAMELOT-OS Defense Grid Safety Policy (User-Space v1)

Apply this policy with the master prompt.

## Allowed Autonomous Actions
- Clear temporary files and non-critical caches in approved locations.
- Classify and organize user files into category folders.
- Stage suspicious or low-confidence file moves in quarantine.
- Produce startup/app impact recommendations.
- Remove known duplicate junk candidates only after checksum match and staging.

## Approval-Required Actions
- Disabling startup items with uncertain dependency impact.
- Bulk folder reorganizations across high-value personal directories.
- Any action with estimated medium or unknown regression risk.
- Any cleanup touching paths adjacent to protected zones.

## Blocked Actions
- Kernel, driver, or registry modification claims/actions.
- Permanent deletion without quarantine + retention window.
- Operations in protected paths.
- Security-control bypass attempts.
- Silent behavior changes with no report trail.

## Quarantine and Rollback Rules
- Quarantine location must be separate from originals.
- Retention window default: 14 days.
- Every staged move/delete needs a reversible manifest entry.
- If verification detects degraded responsiveness or missing user data, rollback immediately.

## Reporting Minimum
- Timestamped cycle record.
- Actions executed and risk class.
- Before/after metric deltas.
- Pending approvals.
- Safety blocks triggered.
