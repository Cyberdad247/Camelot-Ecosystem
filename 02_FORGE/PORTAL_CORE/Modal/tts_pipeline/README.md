# camelot-tts-pipeline

Canonical repo-owned replacement for the deployed Modal app
`camelot-tts-pipeline`.

## Purpose

This service provides text-to-speech output for upstream voice workflows.

## Ownership boundary

- Role: text-to-speech
- Does not own long-term memory
- Does not own short-term NotebookLM state
- Must not be described as replacing `excalibur-brain`

## Entrypoints

- `POST /synthesize_speech`
- `GET /health`

## Secrets

- `my-sovereign-secrets`
  - `OPENAI_API_KEY`

## Deploy

```powershell
modal deploy CAMELOT_OS/02_FORGE/PORTAL_CORE/Modal/tts_pipeline/app.py
```
