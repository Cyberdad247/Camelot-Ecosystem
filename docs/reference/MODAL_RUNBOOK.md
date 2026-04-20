# Modal Cloud Deployment Runbook
# Camelot Apex OS v300.4 — Sovereign Cloud Operations
# Last updated: 2026-04-01

## Quick Reference

| App | Deploy Command | GPU | Secrets Required |
|-----|---------------|-----|-----------------|
| excalibur-brain | `modal deploy CAMELOT_OS/squires/bridge/bridge_script.py` | T4 | my-sovereign-secrets |
| excalibur-bridge | `modal deploy CAMELOT_OS/01_KERNEL/EXCALIBUR/proxy/bridge.py` | - | github-token |
| excalibur-scrub-trainer | `modal run CAMELOT_OS/squires/bridge/train_script.py` | A100 | my-huggingface-secret |
| morgana-prod | `modal deploy CAMELOT_OS/02_FORGE/Modal/morgana/morgana_core.py` | - | shared-api-keys |
| morgana-staging | `modal deploy CAMELOT_OS/02_FORGE/Modal/morgana/morgana_staging.py` | - | shared-api-keys |
| tasha-voice-agent | `modal deploy CAMELOT_OS/02_FORGE/Modal/tasha_voice_agent.py` | - | my-sovereign-secrets, livekit-keys |
| resonance-bridge-v56 | `modal deploy CAMELOT_OS/02_FORGE/Modal/bridge.py` | - | github-token, hf-secret |
| camelot-kinetic-fortress | `modal deploy "CAMELOT_OS/02_FORGE/Modal/New folder/Kinetic_fortress.py"` | - | my-sovereign-secrets |
| camelot_modal_sky | `modal deploy CAMELOT_OS/01_KERNEL/forge/modal_cloud.py` | any | - |

---

## Prerequisites

### 1. Modal CLI Authentication
```bash
# Verify token
modal token verify

# Re-authenticate if needed (opens browser)
modal token set --token-id <TOKEN_ID> --token-secret <TOKEN_SECRET>
```

### 2. Required Modal Secrets
Create these in the Modal dashboard or via CLI:

```bash
# Excalibur Brain + Morgana (Google API + Appwrite)
modal secret create shared-api-keys \
  GOOGLE_API_KEY=<key> \
  APPWRITE_ENDPOINT=<url> \
  APPWRITE_PROJECT_ID=<id> \
  APPWRITE_API_KEY=<key> \
  APPWRITE_DATABASE_ID=<id> \
  APPWRITE_COLLECTION_ID=<id>

# GitHub integration
modal secret create github-token GITHUB_TOKEN=<token>

# HuggingFace models
modal secret create hf-secret HF_TOKEN=<token>
modal secret create my-huggingface-secret HF_TOKEN=<token>

# Sovereign secrets (Appwrite + Google + Supabase + OpenAI)
modal secret create my-sovereign-secrets \
  GOOGLE_API_KEY=<key> \
  APPWRITE_ENDPOINT=<url> \
  APPWRITE_PROJECT_ID=<id> \
  APPWRITE_API_KEY=<key> \
  SUPABASE_URL=<url> \
  SUPABASE_SERVICE_KEY=<key> \
  OPENAI_API_KEY=<key>

# LiveKit voice infrastructure
modal secret create livekit-keys \
  LIVEKIT_URL=<wss://url> \
  LIVEKIT_API_KEY=<key> \
  LIVEKIT_API_SECRET=<secret>
```

### 3. Modal Volumes
```bash
# Squire brain training volume (auto-created)
modal volume list  # Verify squire-brain-vol exists
```

---

## Deployment Procedures

### Standard Deploy (Single App)
```bash
# 1. Activate venv
source CAMELOT_OS/.venv/Scripts/activate  # Windows
source CAMELOT_OS/.venv/bin/activate      # Linux/Mac

# 2. Deploy
modal deploy <path_to_app.py>

# 3. Verify
modal app list
```

### CI/CD Deploy (GitHub Actions)
Trigger via:
- Push to `main` branch (paths: squires/bridge/**, 02_FORGE/Modal/**, etc.)
- Manual dispatch: Actions > Modal Deploy > Run workflow

Required GitHub Secrets:
- `MODAL_TOKEN_ID`
- `MODAL_TOKEN_SECRET`

### GPU Training Run (excalibur-scrub-trainer)
```bash
# CAUTION: Uses A100 GPU — runs cost ~$2/run
# Run logs saved to squire-brain-vol:/brain/outputs/run_<timestamp>.json
modal run CAMELOT_OS/squires/bridge/train_script.py
```

---

## Verification Checklist

After any deploy:
1. `modal app list` — verify app shows as "deployed"
2. Hit health endpoint (if available): `curl <app-url>/health`
3. Check Modal dashboard for errors
4. Verify secrets are bound: check function logs for missing env var errors

---

## Backup & Recovery

### Morgana Backups
```bash
# Backups stored at: CAMELOT_OS/02_FORGE/Modal/morgana/backups/
# Retention: last 3 kept automatically

# Manual cleanup (keep N most recent)
python CAMELOT_OS/02_FORGE/Modal/morgana/cleanup_backups.py --keep 3

# Dry run (preview without deleting)
python CAMELOT_OS/02_FORGE/Modal/morgana/cleanup_backups.py --keep 3 --dry-run
```

### Squire Brain Adapter
```bash
# Adapter weights stored in Modal Volume: squire-brain-vol
# Path: /brain/scout_squire_adapter/

# Download locally
modal volume get squire-brain-vol /brain/scout_squire_adapter ./local_backup/
```

---

## Security

### Token Rotation
1. Go to modal.com > Settings > API Tokens
2. Generate new token pair
3. Update `~/.modal.toml` with new credentials
4. Update GitHub Secrets (MODAL_TOKEN_ID, MODAL_TOKEN_SECRET)
5. Verify: `modal token verify`

### Credential Hygiene
- `.modal.toml` is in `.gitignore` (root + CAMELOT_OS)
- `local_modal.toml` is in `02_FORGE/Modal/.gitignore`
- Never commit `.env` files — use Modal Secrets for cloud, `.env` for local only
- Run `git log --all -p -- "*.modal.toml" "*.env"` to check for past leaks

---

## Cost Monitoring

### GPU Usage
- A100 training: ~$3.50/hr (timeout capped at 2hr = $7 max/run)
- T4 inference: ~$0.59/hr (scaledown after 300s idle)
- Check: Modal dashboard > Usage tab

### Scaling Controls
- `min_containers=1` on tasha-voice-agent (always-on cost)
- `scaledown_window=300` on SovereignInference (5-min idle timeout)
- All other functions scale to 0 when idle

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: modal` | `pip install modal` in venv |
| Secret not found | Create via `modal secret create <name> KEY=VALUE` |
| GPU not available | Check Modal dashboard for GPU quotas |
| Deployment fails silently | `modal deploy --verbose <path>` |
| Volume missing | Volume auto-creates on first use (`create_if_missing=True`) |
| Token expired | `modal token set` or regenerate at modal.com |
| Morgana 500 errors | Check Appwrite connection + GOOGLE_API_KEY validity |
