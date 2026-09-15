# Fixture: single_operator_t3_approval_attempt

A single operator attempts to approve a T3+ effect (`external.publish.publish`,
`payment.capture`, `promote.worktree.merge`, …). The two-person rule must
reject the attempt: two distinct operator identities are required.

Verify: `two_person_rule_enforced` fires; approval rejected with a single
identity; `single_operator_t3_approval_attempt` denial receipt emitted;
no lease issued (§5.5, Principle 15).
