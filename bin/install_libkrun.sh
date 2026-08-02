#!/usr/bin/env bash
# bin/install_libkrun.sh — HiveIDE_Apex_v1000 Phase 3 substrate installer.
# Run ONLY inside a WSL2 distribution with nested virt.
# Idempotent: re-running re-checks before each install step.
# Verdict is emitted as a single JSON line on stdout; exit 0 on GO, 1 on NO-GO/FAIL.
set -euo pipefail

emit() {
    local verdict="$1"; shift
    local detail="$1"; shift
    printf '{"verdict":"%s","detail":"%s","step":"%s"}\n' "$verdict" "$detail" "$STEP"
}

on_wsl() {
    if grep -qi microsoft /proc/version 2>/dev/null; then return 0; fi
    if grep -qi WSL /proc/version 2>/dev/null; then return 0; fi
    if [ -n "${WSL_DISTRO_NAME:-}" ]; then return 0; fi
    return 1
}

kvm_ok() {
    [ -e /dev/kvm ] && [ -r /dev/kvm ] && [ -w /dev/kvm ]
}

uffd_kernel_ok() {
    local kver
    kver="$(uname -r 2>/dev/null || echo unknown)"
    if echo "$kver" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+'; then
        local maj min
        maj="$(echo "$kver" | cut -d. -f1)"
        min="$(echo "$kver" | cut -d. -f2)"
        if [ "$maj" -ge 5 ] || { [ "$maj" -ge 4 ] && [ "$min" -ge 3 ]; }; then
            return 0
        fi
    fi
    return 1
}

STEP="preflight"
if ! command -v sudo >/dev/null 2>&1; then
    emit NO-GO "sudo not installed in WSL2 dist" $STEP
    exit 1
fi

STEP="wsl-detect"
on_wsl || { emit NO-GO "host is not WSL2 (run 'wsl --install' in admin PowerShell)" $STEP; exit 1; }

STEP="kvm-detect"
kvm_ok || { emit NO-GO "/dev/kvm unavailable — enable nested virtualization in BIOS/UEFI" $STEP; exit 1; }

STEP="uffd-detect"
uffd_kernel_ok || { emit NO-GO "kernel too old for userfaultfd (need >=4.3, ideally >=5)" $STEP; exit 1; }

STEP="apt-install"
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y >/dev/null 2>&1 || emit WARN "apt-get update noisy" $STEP
    sudo apt-get install -y libkrun0 librun0 || emit WARN "apt-get install returned non-zero" $STEP
fi

STEP="cargo-fallback"
if ! command -v krun >/dev/null 2>&1 && [ -n "${CARGO_HOME:-}" ]; then
    cargo install --locked krun-cli 2>/dev/null || emit WARN "cargo install krun-cli failed" $STEP
fi

STEP="verify"
if command -v krun >/dev/null 2>&1; then
    emit GO "libkrun installed; krun on PATH" $STEP
    exit 0
fi

# krun binary absent but library may still be installed (linked into the Rust cage)
if ldconfig -p 2>/dev/null | grep -qi libkrun; then
    emit GO "libkrun shared library present; krun CLI not on PATH but cargo test will link against the .so" $STEP
    exit 0
fi

emit NO-GO "libkrun not detected after install — check apt-cache policy libkrun0 librun0" $STEP
exit 1
