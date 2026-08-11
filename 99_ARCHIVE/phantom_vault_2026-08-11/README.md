# Archived: phantom-vault verification ledger

`verification_ledger.jsonl` in this directory holds **83 genuine audit entries**
written between **2026-07-21** and **2026-08-10** to the wrong location:

    control_plane/03_VAULT/Missions/verification_ledger.jsonl   <- phantom
    03_VAULT/Missions/verification_ledger.jsonl                 <- real (582 entries)

## Why it existed

`ProvenanceManager` resolved the vault with a fixed-depth chain:

```python
repo_root = Path(__file__).resolve().parent.parent      # two hops
self.vault_path = repo_root / "03_VAULT" / "Missions"
```

That was correct while the module lived at `control_plane/provenance.py`. When it
moved to `control_plane/infra/provenance.py`, two hops reached `control_plane/`
rather than the repository root, and `mkdir(parents=True, exist_ok=True)`
silently created the phantom tree instead of failing.

The result was a split-brain provenance chain: two ledgers, neither a superset of
the other, both tracked in git. A hash chain with two divergent copies is not
tamper-evident, since "the" chain is ambiguous.

## Why this is archived rather than deleted

These are real audit records. Deleting them would lose three weeks of
verification history. They are **not** merged into the main ledger either: both
files are independently hash-chained, so interleaving their entries would break
verification on both. They are preserved here, out of the resolution path, for
forensic reference only.

Do not treat this file as an active ledger. `verify_chain()` on the main ledger
does not and should not cover it.

## Fix

`control_plane/_paths.py` now resolves the repository root by searching upward
for repository markers, so no module encodes its own depth. Regression coverage
lives in `tests/test_path_resolution_and_failclosed.py`, which asserts that
exactly one `verification_ledger.jsonl` path resolves and that no module under
`control_plane/` uses a short root chain.
