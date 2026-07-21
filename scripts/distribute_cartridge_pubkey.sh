#!/bin/bash
################################################################################
# CAMELOT-OS Cartridge Public Key Distribution
#
# Pushes the local Ed25519 cartridge-signing public key
# (~/.camelot/cartridge_ed25519.pub) to other cluster nodes, so their
# CartridgeSandbox (TrustMode.STRICT) can verify manifests signed on this
# machine. Mirrors deploy_cluster.sh's --nodes/--user/--key conventions —
# run it the same way, against whichever nodes are actually reachable.
#
# This script does NOT touch KBA_CORE's HMAC-signed manifest or the shared
# CAMELOT_CARTRIDGE_HMAC_KEY — those are a separate, symmetric trust path
# (see control_plane/drone_node.py) and are out of scope here.
#
# Usage:
#   ./scripts/distribute_cartridge_pubkey.sh --nodes 192.168.1.10,192.168.1.11,192.168.1.12
#   ./scripts/distribute_cartridge_pubkey.sh --nodes camelot-node-1,camelot-node-2 --user ec2-user --key ~/.ssh/camelot_deploy.pem
#
# Options:
#   --nodes <list>     Comma-separated node hosts/IPs (required)
#   --user <name>       SSH user (default: root)
#   --key <path>        SSH private key (default: ~/.ssh/camelot_deploy)
#   --pubkey <path>      Local public key file to distribute
#                         (default: ~/.camelot/cartridge_ed25519.pub)
#   --dry-run            Print what would happen; don't touch any node
################################################################################

set -euo pipefail

NODES=""
SSH_USER="root"
SSH_KEY="${HOME}/.ssh/camelot_deploy"
PUBKEY_PATH="${HOME}/.camelot/cartridge_ed25519.pub"
DRY_RUN=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

while [[ $# -gt 0 ]]; do
    case "$1" in
        --nodes) NODES="$2"; shift 2 ;;
        --user) SSH_USER="$2"; shift 2 ;;
        --key) SSH_KEY="$2"; shift 2 ;;
        --pubkey) PUBKEY_PATH="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$NODES" ]]; then
    echo -e "${RED}[✗]${NC} --nodes is required, e.g. --nodes 192.168.1.10,192.168.1.11,192.168.1.12" >&2
    exit 1
fi

if [[ ! -f "$PUBKEY_PATH" ]]; then
    echo -e "${RED}[✗]${NC} Public key not found at $PUBKEY_PATH" >&2
    echo "    Generate one first: python -m cartridge.cartridge_crypto keygen" >&2
    exit 1
fi

PUBKEY_VALUE="$(cat "$PUBKEY_PATH")"
echo -e "${BLUE}[INFO]${NC} Distributing cartridge public key: ${PUBKEY_VALUE:0:16}..."

IFS=',' read -ra NODE_ARRAY <<< "$NODES"
FAILED=()

for node in "${NODE_ARRAY[@]}"; do
    echo -e "${BLUE}[INFO]${NC} → $node"

    if $DRY_RUN; then
        echo "    (dry-run) would write ~/.camelot/cartridge_ed25519.pub on $node"
        continue
    fi

    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SSH_USER@$node" "echo 'SSH OK'" > /dev/null 2>&1; then
        echo -e "    ${RED}✗ unreachable via SSH${NC}"
        FAILED+=("$node")
        continue
    fi

    if ssh -i "$SSH_KEY" "$SSH_USER@$node" \
        "mkdir -p ~/.camelot && cat > ~/.camelot/cartridge_ed25519.pub" <<< "$PUBKEY_VALUE"
    then
        echo -e "    ${GREEN}✓ public key written to ~/.camelot/cartridge_ed25519.pub${NC}"
    else
        echo -e "    ${RED}✗ write failed${NC}"
        FAILED+=("$node")
    fi
done

echo ""
if [[ ${#FAILED[@]} -eq 0 ]]; then
    echo -e "${GREEN}[✓]${NC} Public key distributed to all ${#NODE_ARRAY[@]} node(s)."
else
    echo -e "${YELLOW}[!]${NC} Failed on: ${FAILED[*]}"
    echo "    Re-run with --nodes limited to just the failed hosts once they're reachable."
    exit 1
fi
