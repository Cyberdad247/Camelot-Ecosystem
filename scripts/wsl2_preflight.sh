#!/usr/bin/env bash
# SPDX-License-Identifier: MIT

# scripts/wsl2_preflight.sh — Phase 3 substrate preflight (stdout-emit v3)
# Read-only on host. Emits JSON describing current libkrun + UFFD readiness
# directly to stdout. Callers may redirect with `bash scripts/wsl2_preflight.sh
# > out.json`.
set -uo pipefail

wsl_check() {
    if grep -qi microsoft /proc/version 2>/dev/null \
       || grep -qi WSL /proc/version 2>/dev/null \
       || [ -n "${WSL_DISTRO_NAME:-}" ]; then
        printf '{"name":"wsl2","value":"present","warn":false}'
    else
        printf '{"name":"wsl2","value":"absent","warn":true,"remediation":"install WSL2 kernel + enable Developer Mode in Windows"}'
    fi
}

kvm_check() {
    if [ -e /dev/kvm ] && [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
        printf '{"name":"kvm","value":"/dev/kvm accessible","warn":false}'
    else
        printf '{"name":"kvm","value":"/dev/kvm missing or restricted","warn":true,"remediation":"enable nested virtualization in BIOS/UEFI; verify /dev/kvm is owned by current user"}'
    fi
}

uffd_check() {
    KVER=$(uname -r 2>/dev/null || echo unknown)
    if echo "$KVER" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+'; then
        MAJOR=$(echo "$KVER" | cut -d. -f1)
        MINOR=$(echo "$KVER" | cut -d. -f2)
        if [ "$MAJOR" -ge 5 ] || { [ "$MAJOR" -ge 4 ] && [ "$MINOR" -ge 3 ]; }; then
            printf '{"name":"userfaultfd","value":"kernel=%s","warn":false}' "$KVER"
        else
            printf '{"name":"userfaultfd","value":"kernel=%s (<4.3)","warn":true,"remediation":"upgrade kernel to >= 4.3"}' "$KVER"
        fi
    else
        printf '{"name":"userfaultfd","value":"non-linux or unknown kernel","warn":true,"remediation":"Phase 3 requires Linux host"}'
    fi
}

libkrun_check() {
    if command -v krun >/dev/null 2>&1 || ldconfig -p 2>/dev/null | grep -qi libkrun; then
        printf '{"name":"libkrun","value":"installed","warn":false}'
    else
        printf '{"name":"libkrun","value":"missing","warn":true,"remediation":"apt-get install libkrun0 librun0 OR cargo install krun-cli"}'
    fi
}

nested_check() {
    if [ -r /sys/module/kvm_intel/parameters/nested ] && grep -q Y /sys/module/kvm_intel/parameters/nested 2>/dev/null; then
        printf '{"name":"nested_virt","value":"intel=K","warn":false}'
    elif [ -r /sys/module/kvm_amd/parameters/nested ] && grep -q 1 /sys/module/kvm_amd/parameters/nested 2>/dev/null; then
        printf '{"name":"nested_virt","value":"amd=K","warn":false}'
    else
        printf '{"name":"nested_virt","value":"unconfirmed","warn":true,"remediation":"enable nested virtualization in BIOS"}'
    fi
}

W=$(wsl_check)
K=$(kvm_check)
U=$(uffd_check)
L=$(libkrun_check)
N=$(nested_check)

VERDICT="GO"
for line in "$W" "$K" "$U" "$L" "$N"; do
    if echo "$line" | grep -q '"warn":true'; then
        VERDICT="NO-GO"
        break
    fi
done

# Emit JSON directly to stdout. Avoid printf format-string escape pitfalls by
# using echo for the literal scaffolding; values here are bounded and safe.
echo "{"
echo "  \"host\": \"$(uname -srm 2>/dev/null | tr '\n' ' ' | tr -d '\"' | tr -d '\\\\')\","
echo "  \"verdict\": \"$VERDICT\","
echo "  \"checks\": ["
entries=("$W" "$K" "$U" "$L" "$N")
last=$(( ${#entries[@]} - 1 ))
for i in "${!entries[@]}"; do
    sep=","
    [ "$i" -eq "$last" ] && sep=""
    echo "    ${entries[$i]}$sep"
done
echo "  ]"
echo "}"
