# Fixture: operator-console-readonly-audit

Deterministic read-only audit task for the Operator Console. Two workers
(`ant-mapper` done, `owl-auditor` running), one completed receipt, no
approval path. Verify: all six panels render real state, no fabricated
content, no-write receipt (design AC19).
