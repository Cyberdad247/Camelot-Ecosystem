#!/usr/bin/env bash
# build_kinetic.sh — CAMELOT Kinetic Binary Build Harness
# =========================================================
# Compiles all 3 pending Rust binaries + Go TUI, copies to bin/.
# Run from CAMELOT_OS root: bash scripts/build_kinetic.sh
#
# Targets:
#   1. kinetic_edge/swarm_spawner  → bin/swarm-spawner[.exe]
#   2. kinetic_edge/pqcrypto       → bin/camelot-pqcrypto[.exe]
#   3. 02_FORGE/vizion-telemetry   → bin/vizion-telemetry[.exe]  (Go)
#
# Requirements: cargo (rustup), go 1.21+
# Usage:
#   bash scripts/build_kinetic.sh          # build all
#   bash scripts/build_kinetic.sh swarm    # build swarm-spawner only
#   bash scripts/build_kinetic.sh pqcrypto # build pqcrypto only
#   bash scripts/build_kinetic.sh vizion   # build vizion-telemetry only
#   bash scripts/build_kinetic.sh self-test # run pqcrypto self-test after build

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BIN="$ROOT/bin"
mkdir -p "$BIN"

# Colors
G="\033[92m"; Y="\033[93m"; R="\033[91m"; C="\033[96m"; X="\033[0m"; B="\033[1m"

ok()   { echo -e "${G}✅ $*${X}"; }
warn() { echo -e "${Y}⚠  $*${X}"; }
fail() { echo -e "${R}❌ $*${X}"; }
info() { echo -e "${C}   $*${X}"; }

# Detect platform suffix
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || -n "${WINDIR:-}" ]]; then
    EXT=".exe"
else
    EXT=""
fi

# ── Build target functions ────────────────────────────────────────────────────

build_swarm_spawner() {
    echo -e "\n${B}[1/3] swarm-spawner (Rust Tokio SRDL)${X}"
    local src="$ROOT/kinetic_edge/swarm_spawner"
    if [[ ! -f "$src/Cargo.toml" ]]; then
        fail "Cargo.toml not found at $src"
        return 1
    fi
    info "cargo build --release ..."
    cargo build --release --manifest-path "$src/Cargo.toml" 2>&1 | tail -5
    local bin="$src/target/release/swarm-spawner$EXT"
    if [[ -f "$bin" ]]; then
        cp "$bin" "$BIN/swarm-spawner$EXT"
        local size; size=$(du -sh "$BIN/swarm-spawner$EXT" | cut -f1)
        ok "swarm-spawner$EXT → bin/ ($size)"
    else
        fail "swarm-spawner binary not found after build"
        return 1
    fi
}

build_pqcrypto() {
    echo -e "\n${B}[2/3] camelot-pqcrypto (Rust ML-KEM-768 + ML-DSA-65)${X}"
    local src="$ROOT/kinetic_edge/pqcrypto"
    if [[ ! -f "$src/Cargo.toml" ]]; then
        fail "Cargo.toml not found at $src"
        return 1
    fi
    info "cargo build --release ..."
    cargo build --release --manifest-path "$src/Cargo.toml" 2>&1 | tail -5
    local bin="$src/target/release/camelot-pqcrypto$EXT"
    if [[ -f "$bin" ]]; then
        cp "$bin" "$BIN/camelot-pqcrypto$EXT"
        local size; size=$(du -sh "$BIN/camelot-pqcrypto$EXT" | cut -f1)
        ok "camelot-pqcrypto$EXT → bin/ ($size)"
    else
        fail "camelot-pqcrypto binary not found after build"
        return 1
    fi
}

build_vizion() {
    echo -e "\n${B}[3/3] vizion-telemetry (Go BubbleTea + GPU panel)${X}"
    local src="$ROOT/02_FORGE/vizion-telemetry"
    if [[ ! -f "$src/go.mod" ]]; then
        fail "go.mod not found at $src"
        return 1
    fi
    info "go build -ldflags='-s -w' ..."
    (cd "$src" && go build -ldflags="-s -w" -o "$BIN/vizion-telemetry$EXT" . 2>&1)
    if [[ -f "$BIN/vizion-telemetry$EXT" ]]; then
        local size; size=$(du -sh "$BIN/vizion-telemetry$EXT" | cut -f1)
        ok "vizion-telemetry$EXT → bin/ ($size)"
    else
        fail "vizion-telemetry binary not found after build"
        return 1
    fi
}

run_self_test() {
    echo -e "\n${B}[SELF-TEST] camelot-pqcrypto round-trip${X}"
    local bin="$BIN/camelot-pqcrypto$EXT"
    if [[ ! -f "$bin" ]]; then
        warn "pqcrypto binary not found — run build first"
        return 1
    fi
    local result; result=$("$bin" self-test)
    echo "$result"
    if echo "$result" | grep -q '"status": "PASS"'; then
        ok "ML-KEM-768 + ML-DSA-65 self-test PASS"
    else
        fail "self-test FAIL — check Cargo.toml dependencies"
        return 1
    fi
}

# ── Entry point ───────────────────────────────────────────────────────────────

TARGET="${1:-all}"
PASS=0; FAIL=0

echo -e "\n${B}${C}CAMELOT Kinetic Build Harness v400.1.0${X}"
echo -e "${C}ROOT: $ROOT${X}"
echo -e "${C}BIN:  $BIN${X}"

case "$TARGET" in
    swarm)    build_swarm_spawner && PASS=$((PASS+1)) || FAIL=$((FAIL+1)) ;;
    pqcrypto) build_pqcrypto && PASS=$((PASS+1)) || FAIL=$((FAIL+1)) ;;
    vizion)   build_vizion && PASS=$((PASS+1)) || FAIL=$((FAIL+1)) ;;
    self-test) run_self_test && PASS=$((PASS+1)) || FAIL=$((FAIL+1)) ;;
    all)
        build_swarm_spawner && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
        build_pqcrypto      && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
        build_vizion         && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
        run_self_test        && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
        ;;
    *)
        echo "Usage: $0 [all|swarm|pqcrypto|vizion|self-test]"
        exit 1
        ;;
esac

echo ""
if [[ $FAIL -eq 0 ]]; then
    ok "Build complete: $PASS targets built successfully"
    echo -e "${C}Run: awaken --status to verify all phases green${X}"
else
    warn "Build partial: $PASS OK, $FAIL FAILED"
    exit 1
fi
