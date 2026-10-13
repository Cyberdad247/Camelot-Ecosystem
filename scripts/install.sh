#!/bin/bash
# CAMELOT-OS Bare-Metal Installer
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./scripts/install.sh)"
  exit 1
fi

echo "[⚡] Copying binaries to /usr/local/bin..."
cp target/release/camelot-kernel /usr/local/bin/
cp target/release/camelot-spawner /usr/local/bin/
cp target/release/camelot-transport /usr/local/bin/
cp target/release/camelot-runtime /usr/local/bin/

echo "[⚡] Registering systemd daemons..."
cp deploy/*.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable camelot-kernel camelot-spawner camelot-transport camelot-runtime

echo "[🏆] Installation Complete."
echo "Execute the following to boot the Spire:"
echo "  sudo systemctl start camelot-kernel"
echo "  sudo systemctl start camelot-spawner"
echo "  sudo systemctl start camelot-transport"
echo "  sudo systemctl start camelot-runtime"
