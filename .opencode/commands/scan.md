---
description: Codebase intelligence scan for CAMELOT-OS. Triages a path for risk and secrets.
---

Scan this target:

1. Run `python -m squires.colony triage $ARGUMENTS`.
2. If secrets or privacy risk appear, follow with `python -m squires.colony ghost $ARGUMENTS`.
3. Report risk score and findings. If risk >= 50 or secrets are found, pause for human approval — never auto-approve.

Target: $ARGUMENTS
