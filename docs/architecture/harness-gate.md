# Camelot-OS — Harness Gate Checklist

![harness-gate status](https://github.com/Cyberdad247/Camelot-Ecosystem/actions/workflows/harness-gate.yml/badge.svg)
*Badge reflects the latest run of `.github/workflows/harness-gate.yml` on the default branch of `Cyberdad247/Camelot-Ecosystem` (the harness gate's live home since 2026-08-15; the package repo `Cyberdad247/CAMELOT_OS` runs the same gate on its own pushes). Full run history lives on the Actions tab and offline in §5. (Update this URL if the workflow file is renamed or the repo moves.)*

**Canonical source of:** the harness CI gate — `harness/run_all.py` (logic), `harness/gate.sh` (CI wrapper), `.github/workflows/harness-gate.yml` (GitHub Actions).
**Scope:** the published contract family (`packages/contracts/`) and the §11.3 receipt-chain harness (`harness/`). Every build / PR / release must clear this gate before promotion.
**SADD anchors:** §11.3 (receipt chain), §22.2 (fixture → production-gate traceability), Appendix F (`docs/architecture/repo-alignment.md`).

The gate backs the following named production gates from the STRIDE model and §25: `receipt_chain_verified`, `tamper_detection_verified`, `ledger_anchor_verified` (T-10), and the catalog's "meta-validated 2020-12" claim.

**Committed golden set** (`harness/golden-receipts/`, all re-verified from disk by check 1): `rcp_0000..0003.json` (demo chain), `anchor_0000.json` + `anchor_1000.json` (tenant_ledger anchors at every Nth entry), `golden-anchor-0000.json` (the golden set's own ledger-anchor record covering the demo chain head), `sentinel_test_public.pem` (pinned public key), `chain.verified` (marker).

---

## 1. How to run

| Context | Command |
|---------|---------|
| Local (any OS, Git Bash on Windows) | `python harness/run_all.py` |
| CI wrapper (same result) | `bash harness/gate.sh` |
| GitHub Actions | `.github/workflows/harness-gate.yml` — runs on every push / PR |
| Override interpreter | `PYTHON=python3.12 bash harness/gate.sh` |
| Run a single check (fast iteration) | `python harness/run_all.py --check schema-meta` |
| Run a subset | `--check replay` (substring: both replay checks), `--check build --check schema-meta`, or comma-separated `--check replay,schema-meta` |
| List valid check ids | `python harness/run_all.py --list-checks` |

`--check NAME` filters which checks run (case-insensitive substring match on the check id; repeatable and comma-separated). With no `--check`, all four run — that is the promotion gate. A filter matching nothing exits `2` and lists the valid ids, so CI typos fail loudly. Note that a filtered run (e.g. `--check replay-emitted` without `build`) is an iteration aid, not a promotion gate.

Dependencies: `python ≥ 3.10`, `cryptography`, `jsonschema`. All checks run offline (the 2020-12 meta-schema is bundled with `jsonschema`).

## 1a. Configurable anchoring (stress-testing)

The anchored-chain parameters are CLI-configurable, defaults are the §11.3 canonical values:

| Flag | Default | Meaning |
|------|---------|---------|
| `--anchor-every N` | `1000` | Write the head to the ledger anchor every N entries |
| `--chain-size N` | `2000` | Receipts in the anchored stress-test chain (heights `0..N-1`) |

- **Build/emit** uses the flags; emission is authoritative for the current config — stale `anchor_*.json` files from an earlier config are removed first, and the config is persisted in `chain.verified`.
- **Replay ignores the flags** and always re-derives with the persisted config from `chain.verified` — otherwise committed anchors could never match. Forwarding flags to `--replay` just prints a note.
- Forward the flags through the whole gate: `bash harness/gate.sh --anchor-every 100 --chain-size 3000` (or `python harness/run_all.py --anchor-every 100 --chain-size 5000`). The stress run leaves the committed artifacts under the stress config; re-run with defaults afterwards to restore the canonical golden set.

Examples: `--anchor-every 100 --chain-size 5000` → 50 anchors (heights 0,100,…,4900); `--anchor-every 1` → every receipt anchor-eligible (dense-anchoring stress).

These flags are harness stress-testing controls only — the **production policy for per-tenant N deviation** (how a deviation is requested, approved, and bounded) is an open question tracked in `docs/architecture/open-questions.md` §27.5 and flagged in SADD §11.3.

## 1b. Result logs

Every check's full output is teed to the console **and** captured to `harness/results/<check-id>.log` (UTF-8, overwritten per run). Each log has a header recording the check id, purpose, and command, plus a footer recording the exit code. The GitHub Actions workflow uploads `harness/results/` as a `harness-results` artifact (`if: always()` — retained even when the gate fails) for post-run debugging. Logs are regenerable and gitignored (`harness/results/.gitignore`); do not commit them.

## 2. Checks (in order)

Order matters: the committed artifacts are verified **before** any rebuild so a tampered/stale/missing committed receipt or anchor can never be silently healed by regeneration.

| # | Check | Command | Asserts |
|---|-------|---------|---------|
| 1 | `replay-committed` | `python harness/contracts/verify_receipt_chain.py --replay` | The **committed golden set** verifies from disk: receipts (`rcp_0000..0003.json`) — self_hash, ed25519 signature under the pinned key, height continuity, epoch ≥ trusted; tenant_ledger anchors (`anchor_*.json`) pass **signature verification first** (tampering caught from the record alone, no chain re-derivation), then match the deterministically re-derived chain; `golden-anchor-0000.json` (the golden set's own anchor covering the demo chain head) is schema-validated and signature/linkage-verified; signer fingerprint matches `chain.verified`. |
| 2 | `build` | `python harness/contracts/verify_receipt_chain.py` | Rebuilds + emits the golden set: 4/4 receipts schema-conformant (Draft 2020-12), §11.3 rule PASS, 7/7 tamper cases detected (T-1 parent_hash/payload/height/self_hash, S-3 cross-tenant, S-4 forged signature, D-4 stale epoch); 2,000-receipt anchored chain verifies, **ed25519-signed** anchors written at every Nth entry (N=1000, heights 0 and 1000) and schema-validated, 5/5 anchor tamper cases detected (T-10 ×4, S-4 forged anchor signature) — each case dual-checked against the chain and against the anchor signature alone; the golden set's own `golden-anchor-0000.json` (covering the demo genesis head, height 0) is emitted, schema-validated, and signature/linkage-verified with its own T-10 tamper case. |
| 3 | `replay-emitted` | `python harness/contracts/verify_receipt_chain.py --replay` | The artifacts just emitted verify again from disk — determinism loop: emitted set is byte-identical to the committed set. |
| 4 | `schema-meta` | `python harness/contracts/validate_contract_schemas.py` | All 26 `*.schema.json` declare `$schema: draft/2020-12/schema` and meta-validate against the 2020-12 meta-schema; `index.json` catalog conformance (files ↔ entries ↔ `$id` URIs, no orphans/missing). |

## 3. Acceptance checklist

Before promotion, confirm every box:

- [ ] `python harness/run_all.py` exits `0` with "ALL CHECKS PASSED"
- [ ] Committed `harness/golden-receipts/rcp_*.json` + `sentinel_test_public.pem` + `chain.verified` are present and verified from disk (check 1)
- [ ] Committed `harness/golden-receipts/anchor_*.json` are present and match the re-derived chain (check 1)
- [ ] Re-running the gate is deterministic — receipts and anchors are byte-identical across runs (check 3)
- [ ] A deliberate tamper (receipt payload, signature, anchor `head_hash`) makes the gate fail with a non-zero exit — see §4 for how to verify
- [ ] `packages/contracts/index.json` lists exactly the schema files on disk with matching `$id`s (check 4)
- [ ] Any new/edited contract schema still meta-validates as Draft 2020-12 (check 4)

**Operator sign-off (mandatory before promotion).** The promoting operator must confirm the checklist above and sign the gate run. A promotion without a signed-off gate entry in §5 is a process violation; sign-off is a human governance control, not something the gate itself can assert.

- [ ] Gate green: `python harness/run_all.py` exits `0` with "ALL CHECKS PASSED"
- [ ] Gate run recorded in §5 with the `Signed off by` column filled in

```text
I confirm the acceptance checklist above is complete and the gate is green,
and I sign off on promoting this state.

Signed-off-by: <operator name / role> <yyyy-mm-dd>
```

## 4. Failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `signature does not verify` / `self_hash mismatch` in replay | Committed golden receipt tampered or stale (signed under an old key) | Regenerate with `python harness/contracts/verify_receipt_chain.py`, review the diff |
| `missing pinned signer key` | `golden-receipts/` not committed / purged | Run the build once to emit, then commit the golden set (it is now a required audit artifact) |
| `head_hash mismatch (ledger anchor tampering)` | Anchor record tampered or chain changed after anchoring | Rebuild + re-anchor; the mismatch is the T-10 detection firing (also caught by the anchor signature check alone) |
| `anchor signature does not verify` | Anchor record modified in place, or replayed against a different pinned key | Restore from a clean emit; the signature check catches tampering without re-deriving the chain (T-10/S-4) |
| `anchor count mismatch` | An anchor file added/removed, or stale anchors left over from a different `--chain-size`/`--anchor-every` run | Rebuild/emit under the intended config (emission auto-removes stale anchor files) |
| `schema-meta` FAIL | A schema uses an unknown keyword, wrong `$schema`, or `index.json` drift | Fix the schema or catalog; the failing keyword is printed |
| Check crashes with a traceback | Missing dependency | `pip install cryptography jsonschema` |

## 5. Gate run history

Local record of gate executions. The authoritative full history is the GitHub Actions **workflow runs** page on `Cyberdad247/Camelot-Ecosystem` (the gate's live home) and `Cyberdad247/CAMELOT_OS` (the package repo); this table is the offline record. Append a row after every gate-relevant change, and record expected-failure (negative) runs too — they are the evidence that detection works.

| Date | Command / config | Result | Signed off by | Notes |
|------|------------------|--------|---------------|-------|
| 2026-08-15 | `bash harness/gate.sh` (defaults) | ✅ PASS | — | First wired gate: replay-committed → build → replay-emitted → schema-meta all green. |
| 2026-08-15 | `bash harness/gate.sh --anchor-every 100 --chain-size 3000` | ✅ PASS | — | Stress config; first attempt exposed the stale-anchor bug (`replay-emitted` FAIL) → emission now removes stale `anchor_*.json`. |
| 2026-08-15 | `verify_receipt_chain.py --anchor-every 100 --chain-size 5000` + `--replay` | ✅ PASS | — | 50 signed anchors over 5,000 receipts; replay re-derived with the persisted config. |
| 2026-08-15 | negative drills: tampered receipt / missing golden set / tampered anchor / tampered golden anchor | ❌ EXPECTED FAIL | n/a | Gate blocked (exit 1) on every tamper — T-1/T-5/S-4/D-4/T-10 detection verified. |
| 2026-08-15 | `bash harness/gate.sh` (after signed anchors + `golden-anchor-0000.json`) | ✅ PASS | — | Anchor records ed25519-signed; golden set self-contained (receipts + anchors + golden anchor + pubkey + marker). |
| 2026-08-15 | `validate_contract_schemas.py` | ✅ PASS | — | 26/26 schemas meta-validate as Draft 2020-12; catalog conformance OK. |
| 2026-08-15 | `bash harness/gate.sh` (current HEAD) | ✅ PASS | — | All four checks green; per-check logs under `harness/results/`. |
| 2026-08-15 | GitHub Actions run `31919777711` (manual dispatch) | ✅ PASS | — | First live CI run on `Cyberdad247/CAMELOT_OS` (repo created 2026-08-15, badge wired). |
| 2026-08-15 | push-triggered run on `Cyberdad247/Camelot-Ecosystem` | ✅ PASS | — | Gate relocated to the ecosystem repo (contracts catalog 3→26 superset merge; `.pem` committed after the `*.pem` ignore dropped it on the first CI run). |
| 2026-08-15 | `c044b71` push to `Cyberdad247/Camelot-Ecosystem` | ❌ FAIL | — | `replay-committed` blocked: repo `*.pem` ignore dropped `sentinel_test_public.pem` from the commit → fixed by an explicit `!` exception (`e1e5343`). |
| 2026-08-15 | branch protection on `Cyberdad247/Camelot-Ecosystem` `main` | ✅ enforced | — | Required check `Contract harness (receipts + schemas)` (strict, incl. admins); force-push + deletions blocked. |

**Maintenance:** after a gate-relevant change, run the full gate locally and append a row with the exact command/config and result. New PASS rows must carry the promoting operator's sign-off (see §3); `—` marks rows recorded before the sign-off requirement. Keep expected-failure rows from tamper drills (sign-off `n/a`) — they document the gate's detection coverage.

## 6. Maintenance

- Keep the check order stable — `replay-committed` MUST stay first (artifact-integrity-before-rebuild).
- Add new checks to `build_checks` in `harness/run_all.py`, then update §2 of this file.
- Replay must always re-derive with the persisted `chain.verified` config; never let CLI flags change what replay verifies.
- This file is canonical; `repo-alignment.md` §3 and `PURGE_PREP.md` link to it.
