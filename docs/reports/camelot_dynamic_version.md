# Camelot OS Dynamic Version

## Status

- `control_plane/versioning.py` provides a dynamic version source.
- Resolution order:
  1. `CAMELOT_OS_VERSION`
  2. `git describe --tags --always --dirty --long`
  3. UTC timestamp fallback

## Integration Surface

- `control_plane/notebooklm_graphify_manifest.py` can stamp mirrored NotebookLM manifests with the active dynamic version.

## Verification Gap

- The shell helper is currently unstable in this session, so I could not run a live `git describe` or end-to-end version check.
- The version source is still implemented in code and is ready to be wired into the existing CLI/runtime path once the shell stabilizes.

