#!/bin/bash
# 🛡️ SIR HEIMDALL — Universal Inscription for Linux/Termux
# This script installs the "Heimdall-Open the Bifrost" command.

INSTALL_PATH="/usr/local/bin/Heimdall-Open"
if [ "$PREFIX" ]; then INSTALL_PATH="$PREFIX/bin/Heimdall-Open"; fi # Termux support

cat << 'EOF' > "$INSTALL_PATH"
#!/bin/bash
if [[ "$1" == "the" && "$2" == "Bifrost" ]]; then
    echo "⚔️ Summoning the Bifrost..."
    # Check if we are on a remote node and should connect to the Spire
    if command -v tailscale >/dev/null; then
        SPIRE_IP="100.118.224.52"
        echo "Linking to Spire Node ($SPIRE_IP)..."
        # If heimdall.py is not local, we try to run it via ssh or just show status
        tailscale status
    else
        echo "Tailscale not detected. Ensure node is part of the mesh."
    fi
else
    echo "Usage: Heimdall-Open the Bifrost"
fi
EOF

chmod +x "$INSTALL_PATH"
echo "✅ Inscription complete. Command 'Heimdall-Open the Bifrost' is now global."
