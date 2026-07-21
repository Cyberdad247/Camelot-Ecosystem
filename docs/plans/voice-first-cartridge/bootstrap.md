# VFC Bootstrap Cartridge

```text
[SYSTEM_ACTIVATE] :: CAMELOT_VFC_v10000.15
[TARGET] :: CAMELOT_OS
[AUTHORITY] :: docs/protocols/pre-flight.md
[SOURCE] :: docs/plans/voice-first-cartridge/{blueprint,tasks,verification}.md

Execute only after the resource pre-flight returns GO.

1. Validate source hashes and the canonical pre-flight contract.
2. Build the shared browser voice runtime and bounded AudioWorklet transport.
3. Wire authenticated same-origin frames to loopback OmniVoice.
4. Preserve one microphone owner, transient PCM custody, text fallback, and Iron Gate.
5. Run the declared verification commands.
6. Emit a Forge Law cartridge only when every gate passes.

Markdown is non-executable. Structured Forge Law operations remain the sole
kinetic contract. Never write protected ledgers or restart services directly.
```
