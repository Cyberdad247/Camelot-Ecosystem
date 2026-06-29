# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from morgana_core import app

if __name__ == "__main__":
    # Entrypoint to deploy or serve locally
    # Note: Modal apps are typically deployed via 'modal deploy morgana_core.py'
    # This main.py satisfies the --entrypoint requirement for external orchestration.
    app.run()