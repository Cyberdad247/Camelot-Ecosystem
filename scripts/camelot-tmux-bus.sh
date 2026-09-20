#!/usr/bin/env bash
# Camelot-OS Bus & Telemetry Multiplexer
SESSION="camelot-bus"

tmux has-session -t "$SESSION" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[INFO] Spawning tmux session: $SESSION"
    # Window 0: Edge Bus Live Journal
    tmux new-session -d -s "$SESSION" -n "edge-bus" "journalctl -u camelot-edge-bus.service -f -n 50"
    
    # Window 1: Mesh Bridge Live Journal
    tmux new-window -t "${SESSION}:1" -n "mesh-bridge" "journalctl -u camelot-vps-mesh.service -f -n 50"
    
    # Window 2: Bifrost Gateway Live Journal
    tmux new-window -t "${SESSION}:2" -n "bifrost" "journalctl -u camelot-bifrost.service -f -n 50"
    
    # Window 3: Live Bus Telemetry Monitor
    tmux new-window -t "${SESSION}:3" -n "monitor" "watch -n 2 'echo \"=== CAMELOT EDGE BUS (:8096) ===\"; curl -s http://100.110.180.18:8096/healthz; echo \"\"; echo \"\"; echo \"=== MESH BRIDGE (:8095) ===\"; curl -s http://127.0.0.1:8095/mesh/status; echo \"\"; echo \"\"; echo \"=== LISTENING PORTS ===\"; ss -tulpn | grep -E \"8096|8095|3001\"'"
    
    # Window 4: Interactive Control Plane Shell
    tmux new-window -t "${SESSION}:4" -n "shell" "cd /opt/camelot-ecosystem && exec /bin/bash"

    # Window 5: Hermes Agent Container Live Logs
    tmux new-window -t "${SESSION}:5" -n "hermes-container" "docker logs -f hermes"

    # Window 6: Hermes Prime Continuous MGV Loop
    tmux new-window -t "${SESSION}:6" -n "hermes-prime" "journalctl -u camelot-hermes-prime.service -f -n 50"

    # Window 7: Motorola Moto Edge Bus Sentinel
    tmux new-window -t "${SESSION}:7" -n "moto-sentinel" "watch -n 2 'echo \"=== MOTOROLA EDGE SENTINEL (100.89.129.105) ===\"; curl -s http://100.110.180.18:8096/inbox; echo \"\"; echo \"=== OUTBOX QUEUE ===\"; curl -s http://100.110.180.18:8096/outbox; echo \"\"; echo \"=== S26 EXCALIBUR (100.106.246.126) ===\"; curl -s http://127.0.0.1:8095/mesh/status'"

    # Select default window
    tmux select-window -t "${SESSION}:0"
    echo "[OK] Session $SESSION initialized with 8 windows (edge-bus, mesh-bridge, bifrost, monitor, shell, hermes-container, hermes-prime, moto-sentinel)."
else
    echo "[INFO] Session $SESSION already exists. Checking for missing windows..."
    tmux list-windows -t "$SESSION" | grep -q "hermes-container" || tmux new-window -t "${SESSION}:5" -n "hermes-container" "docker logs -f hermes"
    tmux list-windows -t "$SESSION" | grep -q "hermes-prime" || tmux new-window -t "${SESSION}:6" -n "hermes-prime" "journalctl -u camelot-hermes-prime.service -f -n 50"
    tmux list-windows -t "$SESSION" | grep -q "moto-sentinel" || tmux new-window -t "${SESSION}:7" -n "moto-sentinel" "watch -n 2 'echo \"=== MOTOROLA EDGE SENTINEL (100.89.129.105) ===\"; curl -s http://100.110.180.18:8096/inbox; echo \"\"; echo \"=== OUTBOX QUEUE ===\"; curl -s http://100.110.180.18:8096/outbox; echo \"\"; echo \"=== S26 EXCALIBUR (100.106.246.126) ===\"; curl -s http://127.0.0.1:8095/mesh/status'"
fi

# Also create symlink or alias for camelot-os session name
tmux has-session -t "camelot-os" 2>/dev/null
if [ $? -ne 0 ]; then
    tmux new-session -d -s "camelot-os" -t "$SESSION"
fi

tmux list-sessions
