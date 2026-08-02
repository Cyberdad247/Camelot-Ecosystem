# 🤖 Assimilation — Voice Assistant Omega

> **STATUS:** In Development · Python

The Assimilation module contains the Voice Assistant Omega — a Python-based voice interaction system with gVisor sandboxing for secure execution. Designed to integrate with the CAMELOT-OS voice pipeline.

## Structure

```
assimilation/
└── voice_assistant_omega/
    ├── main.py              # Main entry point
    ├── BriefingScript.md    # Operational briefing
    ├── requirements.txt     # Python dependencies
    └── gvisor-run.ps1       # gVisor sandbox launcher (PowerShell)
```

## Setup

```bash
cd 02_FORGE/assimilation/voice_assistant_omega
pip install -r requirements.txt
python main.py
```

## Sandbox

For secure gVisor-isolated execution:

```powershell
.\gvisor-run.ps1
```
