#!/data/data/com.termux/files/usr/bin/bash
# CAMELOT-OS ၔ Always-On Mobile Sentinel Daemon
# Keeps Termux awake, manages wake-locks, and auto-restarts node.

if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
    echo "[CAMELOT_DAEMON] Wake-lock acquired."
fi

# Start SSH server
sshd 2>/dev/null || true

# Start Camelot Mobile Sentinel with auto-restart watchdog
while true; do
    echo "[CAMELOT_DAEMON] Starting camelot-mobile-node.js at $(date)..."
    node ~/camelot-mobile-node.js >> ~/camelot-mobile.log 2>&1
    echo "[CAMELOT_DAEMON] Process exited. Restarting in 5s..."
    sleep 5
done
