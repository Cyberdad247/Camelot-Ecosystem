# Graphify NotebookLM Bridge Status

## Implemented

- `control_plane/notebooklm_graphify_bridge.py` now reads `~/.notebooklm/storage_state.json`.
- It normalizes notebooks and sources into a stable graph context.
- It materializes a Graphify-ready markdown corpus under `03_VAULT/runtime_state/notebooklm_graphify/`.
- It emits a manifest for provenance and repeatable replay.
- It prepares the Graphify command `graphify extract <corpus> --no-viz --force`.

## Notes

- The bridge defaults to dry-run execution for Graphify.
- This keeps the integration safe until the user confirms the external CLI and backend choice.
- The NotebookLM hosted product remains a Google Labs service, not an open-source upstream.

## Next Actions

1. Attach the bridge to the existing cloudbrain sync event.
2. Add a CLI subcommand or runic route for explicit operator invocation.
3. Decide whether Graphify should run locally, through a hosted backend, or only produce the corpus.

