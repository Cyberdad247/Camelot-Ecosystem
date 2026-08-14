#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# ============================================================
# CAMELOT-OS Installer — Linux / macOS / WSL
# WARP_GATE v1.0.0
#
# Usage:
#   bash scripts/install.sh             # from repo root
#   curl -fsSL <url>/install.sh | bash  # one-liner
#
# Options (env vars):
#   CAMELOT_HOME=/path/to/CAMELOT_OS   override repo path
#   CAMELOT_NO_PROFILE=1               skip shell profile modification
#   CAMELOT_NO_CONFIGURE=1             skip camelot configure step
#   CAMELOT_PORTABLE=1                 portable mode (no PATH writes)
# ============================================================

set -euo pipefail

CAMELOT_VERSION="400.1.0"
WARP_VERSION="1.0.0"
MIN_PYTHON_MINOR=11   # Python 3.11+

# ── Colors ────────────────────────────────────────────────────────────────────

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

step()  { echo -e "\n${CYAN}${BOLD}  >>  ${RESET}$*"; }
ok()    { echo -e "  ${GREEN}[OK]${RESET} $*"; }
warn()  { echo -e "  ${YELLOW}[!!]${RESET} $*"; }
fail()  { echo -e "  ${RED}[XX]${RESET} $*"; exit 1; }

# ── Banner ────────────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}${BOLD}  ============================================${RESET}"
echo -e "${YELLOW}${BOLD}   CAMELOT-OS v${CAMELOT_VERSION}  //  WARP_GATE v${WARP_VERSION}${RESET}"
echo -e "${YELLOW}${BOLD}   Linux / macOS Installer${RESET}"
echo -e "${YELLOW}${BOLD}  ============================================${RESET}"
echo ""

# ── Locate CAMELOT_OS root ────────────────────────────────────────────────────

step "Locating CAMELOT_OS root..."

if [[ -n "${CAMELOT_HOME:-}" ]]; then
    REPO="$CAMELOT_HOME"
elif [[ -n "${CAMELOT_OS_HOME:-}" ]]; then
    REPO="$CAMELOT_OS_HOME"
else
    # Try: script location → parent
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
    REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

if [[ ! -f "$REPO/pyproject.toml" ]]; then
    fail "Cannot find CAMELOT_OS at: $REPO\nSet CAMELOT_HOME or clone the repo first:\n  git clone https://github.com/your-org/CAMELOT_OS.git"
fi

ok "CAMELOT_OS root: $REPO"
VENV_DIR="$REPO/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_BIN="$VENV_DIR/bin"

# ── Detect OS ─────────────────────────────────────────────────────────────────

OS="$(uname -s)"
ARCH="$(uname -m)"
ok "Platform: $OS $ARCH"

# ── Check Python ──────────────────────────────────────────────────────────────

step "Checking Python version..."

PYTHON_CMD=""
for cmd in python3.13 python3.12 python3.11 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver="$($cmd --version 2>&1 | grep -oP '\d+\.\d+' | head -1)"
        major="${ver%%.*}"
        minor="${ver##*.}"
        if [[ "$major" -ge 3 && "$minor" -ge $MIN_PYTHON_MINOR ]]; then
            PYTHON_CMD="$cmd"
            ok "Found: $($cmd --version)"
            break
        else
            warn "Found $cmd $ver — need >= 3.$MIN_PYTHON_MINOR"
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    fail "Python 3.$MIN_PYTHON_MINOR+ not found.\n\nInstall via:\n  macOS:  brew install python@3.11\n  Ubuntu: sudo apt install python3.11 python3.11-venv\n  Arch:   sudo pacman -S python"
fi

# ── Create / verify virtual environment ───────────────────────────────────────

step "Checking virtual environment..."

if [[ -x "$VENV_PYTHON" ]]; then
    ok "Existing .venv found: $VENV_DIR"
else
    echo "  Creating .venv at $VENV_DIR ..."
    if command -v uv &>/dev/null; then
        uv venv "$VENV_DIR" --python "$PYTHON_CMD"
    else
        "$PYTHON_CMD" -m venv "$VENV_DIR"
    fi

    if [[ ! -x "$VENV_PYTHON" ]]; then
        fail "Failed to create .venv — try: $PYTHON_CMD -m venv $VENV_DIR"
    fi
    ok ".venv created"
fi

PIP_CMD="$VENV_PYTHON -m pip"

# ── Install minimum required packages ─────────────────────────────────────────

step "Installing required packages into .venv..."

MIN_PACKAGES="httpx rich psutil pyyaml"
MISSING=""
for pkg in $MIN_PACKAGES; do
    mod="${pkg//-/_}"
    if ! "$VENV_PYTHON" -c "import $mod" 2>/dev/null; then
        MISSING="$MISSING $pkg"
    fi
done

if [[ -n "$MISSING" ]]; then
    echo "  Installing:$MISSING"
    if command -v uv &>/dev/null; then
        uv pip install --python "$VENV_PYTHON" $MISSING
    else
        $PIP_CMD install --quiet $MISSING
    fi
    ok "Packages installed"
else
    ok "All required packages already present"
fi

# ── Create global symlinks / wrappers in .venv/bin ────────────────────────────

step "Creating command wrappers in .venv/bin..."

create_wrapper() {
    local name="$1"
    local script="$2"
    local dest="$VENV_BIN/$name"

    if [[ -f "$dest" && "${CAMELOT_FORCE:-0}" != "1" ]]; then
        ok "$name already exists"
        return
    fi

    cat > "$dest" << WRAPPER
#!/usr/bin/env bash
exec "$VENV_PYTHON" -X utf8 "$REPO/$script" "\$@"
WRAPPER
    chmod +x "$dest"
    ok "Created: $name"
}

create_wrapper "camelot"        "bin/camelot.py"
create_wrapper "ai"             "bin/camelot.py"
create_wrapper "ks"             "bin/knight_session.py"
create_wrapper "knight-session" "bin/knight_session.py"

# ── Register PATH + shell integration ─────────────────────────────────────────

if [[ "${CAMELOT_PORTABLE:-0}" != "1" ]]; then
    step "Configuring shell integration..."

    # Detect shell config files
    SHELL_CONFIGS=()
    if [[ -f "$HOME/.bashrc" ]];             then SHELL_CONFIGS+=("$HOME/.bashrc"); fi
    if [[ -f "$HOME/.zshrc" ]];              then SHELL_CONFIGS+=("$HOME/.zshrc"); fi
    if [[ -f "$HOME/.config/fish/config.fish" ]]; then SHELL_CONFIGS+=("$HOME/.config/fish/config.fish"); fi
    if [[ ${#SHELL_CONFIGS[@]} -eq 0 ]]; then
        SHELL_CONFIGS=("$HOME/.profile")
        touch "$HOME/.profile"
    fi

    PROFILE_BLOCK="
# ── CAMELOT-OS Integration (WARP_GATE v${WARP_VERSION}) ──────────────────────────
export CAMELOT_OS_HOME=\"$REPO\"
export PATH=\"$VENV_BIN:\$PATH\"
alias ai='camelot'
# Type 'camelot' to warp into Camelot-OS
# ─────────────────────────────────────────────────────────────────────────────"

    for cfg in "${SHELL_CONFIGS[@]}"; do
        if grep -q "CAMELOT-OS Integration" "$cfg" 2>/dev/null; then
            ok "Profile already configured: $cfg"
        elif [[ "${CAMELOT_NO_PROFILE:-0}" != "1" ]]; then
            echo "$PROFILE_BLOCK" >> "$cfg"
            ok "Profile updated: $cfg"
        else
            warn "Skipping profile (CAMELOT_NO_PROFILE=1): $cfg"
        fi
    done

    # Apply to current session
    export CAMELOT_OS_HOME="$REPO"
    export PATH="$VENV_BIN:$PATH"
fi

# ── Run camelot configure ─────────────────────────────────────────────────────

if [[ "${CAMELOT_NO_CONFIGURE:-0}" != "1" ]]; then
    step "Running auto-configuration..."
    echo ""
    "$VENV_PYTHON" -X utf8 "$REPO/bin/camelot.py" configure || warn "Configure step had errors (non-fatal)"
fi

# ── Done ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}${BOLD}  ============================================${RESET}"
echo -e "${GREEN}${BOLD}   CAMELOT-OS installation complete!${RESET}"
echo -e "${GREEN}${BOLD}  ============================================${RESET}"
echo ""
echo -e "  Commands available:"
echo -e "    ${CYAN}camelot${RESET}          warp into Camelot-OS REPL"
echo -e "    ${CYAN}camelot status${RESET}   probe all services"
echo -e "    ${CYAN}ai${RESET}               alias for camelot"
echo -e "    ${CYAN}ks${RESET}               direct knight-session REPL"
echo ""
echo -e "  ${YELLOW}Reload your shell or run: source ~/.bashrc${RESET}"
echo -e "  ${YELLOW}Then type: camelot${RESET}"
echo ""
