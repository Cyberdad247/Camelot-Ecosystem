# Fixture: cached_epoch_across_policy_bump

Phone holds a cached authority epoch when a policy bump or key rotation
increments the epoch. The cached-epoch window must reset to 0 and the
device must come online to fetch the new epoch; no renewal across the bump.

Verify: `mobile_epoch_window_enforced` fires; cached window invalidated;
device cannot act on the old epoch; new epoch required before any action
(§10.3, §6.3).
