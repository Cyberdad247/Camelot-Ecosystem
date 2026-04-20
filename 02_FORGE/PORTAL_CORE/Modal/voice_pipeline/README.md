# camelot-voice-pipeline

Canonical repo-owned replacement for the deployed Modal app
`camelot-voice-pipeline`.

## Purpose

This service provides the speech-to-text surface for uploaded audio.

## Ownership boundary

- Role: speech-to-text
- Does not own long-term memory
- Does not own short-term NotebookLM state
- Must not be described as replacing `excalibur-brain`

## Entrypoints

- `POST /transcribe_audio`
- `GET /health`

## Secrets

- `my-sovereign-secrets`
  - `OPENAI_API_KEY`

## Deploy

```powershell
modal deploy CAMELOT_OS/02_FORGE/PORTAL_CORE/Modal/voice_pipeline/app.py
```
