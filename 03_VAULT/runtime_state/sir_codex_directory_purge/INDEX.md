# Sir Codex Directory Purge Audit Index

Generated: 2026-07-01

Purpose: provide a stable index over existing Sir Codex purge/scorpion artifacts without deleting, moving, or rewriting the original reports.

## Indexed Scopes

| Scope | Purge report | Scorpion review | Proposed disposition |
|---|---|---|---|
| `camelot_os_audit` | `camelot_os_audit/sir_codex_directory_purge_report.json` | `camelot_os_audit/sir_codex_scorpion_review.md` | Keep; Camelot repo audit evidence. |
| `home_defensegrid_quarantine` | `home_defensegrid_quarantine/sir_codex_directory_purge_report.json` | `home_defensegrid_quarantine/sir_codex_scorpion_review.md` | Keep; quarantine evidence lane. |
| `home_dot_cache` | `home_dot_cache/sir_codex_directory_purge_report.json` | `home_dot_cache/sir_codex_scorpion_review.md` | Archive candidate after cache cleanup verification. |
| `home_dot_docker` | `home_dot_docker/sir_codex_directory_purge_report.json` | `home_dot_docker/sir_codex_scorpion_review.md` | Archive candidate after Docker state verification. |
| `home_dot_npm` | `home_dot_npm/sir_codex_directory_purge_report.json` | `home_dot_npm/sir_codex_scorpion_review.md` | Archive candidate after npm cache verification. |
| `home_dot_ollama` | `home_dot_ollama/sir_codex_directory_purge_report.json` | `home_dot_ollama/sir_codex_scorpion_review.md` | Keep until local model inventory is reconciled. |
| `home_dot_rustup` | `home_dot_rustup/sir_codex_directory_purge_report.json` | `home_dot_rustup/sir_codex_scorpion_review.md` | Archive candidate after Rust toolchain verification. |
| `home_downloads` | `home_downloads/sir_codex_directory_purge_report.json` | `home_downloads/sir_codex_scorpion_review.md` | Keep until user-owned downloads are classified. |
| `scripts_probe` | `scripts_probe/sir_codex_directory_purge_report.json` | `scripts_probe/sir_codex_scorpion_review.md` | Keep; script audit evidence. |
| `user_home_audit` | `user_home_audit/sir_codex_directory_purge_report.json` | `user_home_audit/sir_codex_scorpion_review.md` | Keep; broad home audit evidence. |

## Rules

- Do not delete individual reports from this folder without a corresponding update to this index.
- Do not treat repeated basenames as duplicates; each pair belongs to a different audit scope.
- If any scope is archived later, move the full folder as a unit and leave a pointer here.
