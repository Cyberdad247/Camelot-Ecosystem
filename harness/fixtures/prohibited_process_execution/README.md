# Fixture: prohibited_process_execution

Workload invokes an executable not on the lease allowlist (e.g. a shell,
curl, or compiler outside the pinned set). The native process supervisor
must deny execution and drop privileges.

Verify: `unapproved_process_denied` fires; process never starts; no child
spawn; resource budget unaffected (§14.1).
