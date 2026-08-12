Camelot-OS KBA Drone — bundle for lakesha
=========================================
A self-contained governed drone: signed cartridges -> trust -> RBAC -> real KBA
executor -> tamper-evident audit, with Sir Heimdall on perimeter watch.

RUN (PowerShell, from this extracted folder):
  1. Install deps once:   pip install cryptography pydantic
  2. Start the drone:     powershell -ExecutionPolicy Bypass -File .\run_drone.ps1
  3. Verify (any tailnet member):  curl http://100.125.205.66:9000/health
       (or the box's real tailnet IP, e.g. 100.100.155.55)

WHAT YOU GET
  - Endpoints: /health, /kba/tools, /heimdall/status, POST /bifrost/dispatch
  - Governed KBA tools: kba.status, kba.echo, kba.tts, kba.transcribe, kba.voices
  - heimdall.scan (perimeter guardian), + built-ins echo, utc_now
  - Every dispatch is HMAC-authenticated + signature-verified + governance-checked.

DISPATCH FROM THE CONTROL PLANE (uses the same WEBHOOK_SECRET):
  from control_plane.drone_node import dispatch_to_drone
  dispatch_to_drone("http://100.100.155.55:9000","KBA_CORE","kba.status",{},
                    principal="sir_boris", secret=WEBHOOK_SECRET)

NOTES
  - CloudBrain/NotebookLM sync will show "queued" here until the NotebookLM bridge
    is configured on this box; events queue and flush later, nothing is lost.
  - Bind host is the tailnet IP (never 0.0.0.0). Change --host in run_drone.ps1 if
    this box's tailnet IP differs.
  - To keep it running after logout: register it as a Scheduled Task (AtLogOn).
