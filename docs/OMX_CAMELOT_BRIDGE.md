# OmX and Camelot-OS Bridge

This repository integrates the official [`oh-my-codex`](https://github.com/Yeachan-Heo/oh-my-codex) CLI as an execution layer around Camelot-OS. OmX remains responsible for Codex workflows; Camelot remains authoritative for repository guidance, runic routing, boot, status, privacy scanning, and provenance governance.

## Boundary

The bridge deliberately does not run `omx setup`, install OmX hooks, or rewrite `AGENTS.md`. The wrapper sets `OMX_MODEL_INSTRUCTIONS_FILE` to the existing root `AGENTS.md` and preserves `OMX_BYPASS_DEFAULT_SYSTEM_PROMPT=0` unless the operator explicitly overrides it.

The bridge is implemented in [`scripts/omx-camelot.py`](../scripts/omx-camelot.py) and exposed through the root npm script `npm run omx:camelot -- <command>`.

## Prerequisites

```bash
node --version
npm --version
codex --version
npm install -g oh-my-codex
```

The global install is machine-level. Do not store credentials in this repository. Authenticate Codex through its normal user-level configuration and verify it with `codex login status`.

## Commands

```bash
# Check the OmX install without modifying project guidance
python scripts/omx-camelot.py doctor

# Same bridge through npm
npm run omx:camelot -- doctor

# Verify Camelot's live health probes
python scripts/omx-camelot.py status

# Activate Camelot's quick boot sequence
python scripts/omx-camelot.py boot

# Route through the live Camelot runic router
python scripts/omx-camelot.py route --rune STATUS --task "integration check"

# Run the Squire Colony file walk or local-only privacy scan
python scripts/omx-camelot.py scan .
python scripts/omx-camelot.py scan . --ghost

# Launch OmX with Camelot guidance in the current repository
python scripts/omx-camelot.py launch --direct

# Run an explicit non-interactive OmX execution with normal Codex approvals
python scripts/omx-camelot.py exec --skip-git-repo-check -C . "Reply with exactly OMX-CAMELOT-OK"
```

`--madmax` remains an OmX alias for `--dangerously-bypass-approvals-and-sandbox`; it is not part of the bridge defaults and should require an explicit operator decision in a trusted isolated worktree.

## Verification

The integration is considered locally ready when these checks pass:

```bash
omx --version
omx doctor
codex login status
python scripts/omx-camelot.py route --rune STATUS --task "bridge smoke test"
```

`omx doctor` may report warnings until OmX's optional user-scoped setup is performed. Those warnings do not authorize OmX to overwrite Camelot guidance. If project-scoped OmX setup is desired later, review its merge and hook behavior separately before running it.

## Sources

- OmX repository and install contract: <https://github.com/Yeachan-Heo/oh-my-codex>
- OmX setup and prompt-source behavior: <https://github.com/Yeachan-Heo/oh-my-codex/blob/main/docs/getting-started.html>
- Camelot control-plane entry point: [`control_plane/__main__.py`](../control_plane/__main__.py)
- Camelot root governance: [`AGENTS.md`](../AGENTS.md)
