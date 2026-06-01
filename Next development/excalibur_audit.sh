#!/usr/bin/env bash
# core/excalibur_audit.sh
# PRD 2 :: SIR CODEX :: bare-metal telemetry probe for EXCALIBUR v1000.0.0
# PROFILE: nitro-v15-cpu  (Acer Nitro V 15 / x86_64 / 8GB / CPU substrate)
# Emits raw JSON telemetry + a flat telemetry.env sidecar for Sir Boris.

PROFILE="nitro-v15-cpu"
ROOT="${EXCALIBUR_ROOT:-$HOME/excalibur}"
HOME_MNT="${EXCALIBUR_HOME:-$HOME}"
LOG_DIR="$ROOT/core/audit_logs"
mkdir -p "$LOG_DIR"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

have(){ command -v "$1" >/dev/null 2>&1 && echo true || echo false; }
ver(){ if command -v "$1" >/dev/null 2>&1; then "$1" --version 2>&1 | head -n1 | tr -d '"\\'; else echo absent; fi; }
clean(){ printf '%s' "$1" | tr -d '"\\' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'; }

# ---- CPU ----
arch="$(uname -m 2>/dev/null || echo unknown)"
kernel="$(uname -r 2>/dev/null || echo unknown)"
cores="$(nproc 2>/dev/null || echo 0)"
cpu_model="$(lscpu 2>/dev/null | sed -n 's/^Model name:[[:space:]]*//p' | head -n1)"
[ -z "$cpu_model" ] && cpu_model="$(awk -F: '/model name/{print $2; exit}' /proc/cpuinfo 2>/dev/null)"
cpu_model="$(clean "$cpu_model")"; [ -z "$cpu_model" ] && cpu_model="unknown"

# ---- Chassis / platform (DMI on x86 Linux; WSL aware) ----
product="$(clean "$(cat /sys/devices/virtual/dmi/id/product_name 2>/dev/null)")"; [ -z "$product" ] && product="unknown"
vendor="$(clean "$(cat /sys/devices/virtual/dmi/id/sys_vendor 2>/dev/null)")"; [ -z "$vendor" ] && vendor="unknown"
grep -qi microsoft /proc/version 2>/dev/null && wsl=true || wsl=false

# ---- RAM via /proc/meminfo ----
mem_total_kb="$(awk '/^MemTotal:/{print $2}' /proc/meminfo 2>/dev/null)"
mem_avail_kb="$(awk '/^MemAvailable:/{print $2}' /proc/meminfo 2>/dev/null)"
: "${mem_total_kb:=0}"; : "${mem_avail_kb:=0}"
mem_total_mb=$(( mem_total_kb / 1024 )); mem_avail_mb=$(( mem_avail_kb / 1024 ))
mem_used_mb=$(( mem_total_mb - mem_avail_mb ))

# ---- Storage on home mount (NVMe/SSD) ----
read -r fs blocks used avail cap mnt <<EOF
$(df -Pk "$HOME_MNT" 2>/dev/null | awk 'NR==2{print $1,$2,$3,$4,$5,$6}')
EOF
: "${blocks:=0}"; : "${used:=0}"; : "${avail:=0}"; : "${mnt:=unknown}"
store_total_mb=$(( blocks / 1024 )); store_used_mb=$(( used / 1024 )); store_free_mb=$(( avail / 1024 ))

# ---- eBPF / BTF capability (Aegis Shield prerequisite) ----
[ -r /sys/kernel/btf/vmlinux ] && btf=true || btf=false

# ---- Toolchain (x86 Linux: sandbox primitive = bwrap|proot|unshare) ----
have_rustc=$(have rustc); have_cargo=$(have cargo); have_python=$(have python3)
have_bwrap=$(have bwrap); have_proot=$(have proot); have_unshare=$(have unshare)
if [ "$have_bwrap" = true ] || [ "$have_proot" = true ] || [ "$have_unshare" = true ]; then have_sandbox=true; else have_sandbox=false; fi
v_rustc="$(ver rustc)"; v_cargo="$(ver cargo)"; v_python="$(ver python3)"

# ---- Package manager detection + remediation hint ----
if   command -v apt-get >/dev/null 2>&1; then pm="apt"
elif command -v dnf     >/dev/null 2>&1; then pm="dnf"
elif command -v pacman  >/dev/null 2>&1; then pm="pacman"
elif command -v zypper  >/dev/null 2>&1; then pm="zypper"
elif command -v brew    >/dev/null 2>&1; then pm="brew"
else pm="unknown"; fi

# ---- Package inventory (Squire buffer) ----
pkg_file="$LOG_DIR/pkg_installed.txt"
if [ ! -s "$pkg_file" ]; then
  case "$pm" in
    apt)    dpkg -l 2>/dev/null | awk '/^ii/{print $2}' > "$pkg_file" ;;
    dnf|zypper) rpm -qa 2>/dev/null > "$pkg_file" ;;
    pacman) pacman -Q 2>/dev/null > "$pkg_file" ;;
    brew)   brew list 2>/dev/null > "$pkg_file" ;;
    *)      : > "$pkg_file" ;;
  esac
fi
pkg_count=$(wc -l < "$pkg_file" 2>/dev/null | tr -d ' '); : "${pkg_count:=0}"

json_file="$LOG_DIR/telemetry.json"; env_file="$LOG_DIR/telemetry.env"
cat > "$json_file" <<JSON
{
  "schema": "excalibur.telemetry/v1000.0.0",
  "profile": "$PROFILE",
  "timestamp_utc": "$ts",
  "platform": { "vendor": "$vendor", "product": "$product", "wsl": $wsl, "pkg_manager": "$pm" },
  "cpu": { "arch": "$arch", "model": "$cpu_model", "kernel": "$kernel", "cores": $cores },
  "memory_mb": { "total": $mem_total_mb, "used": $mem_used_mb, "available": $mem_avail_mb },
  "storage_mb": { "mount": "$mnt", "total": $store_total_mb, "used": $store_used_mb, "free": $store_free_mb },
  "kernel_features": { "btf_ebpf": $btf },
  "toolchain": {
    "rustc":   { "present": $have_rustc, "version": "$v_rustc" },
    "cargo":   { "present": $have_cargo, "version": "$v_cargo" },
    "python3": { "present": $have_python, "version": "$v_python" },
    "sandbox": { "present": $have_sandbox, "bwrap": $have_bwrap, "proot": $have_proot, "unshare": $have_unshare }
  },
  "packages": { "installed_count": $pkg_count, "buffer": "core/audit_logs/pkg_installed.txt" }
}
JSON

cat > "$env_file" <<ENV
PROFILE="$PROFILE"
TS="$ts"
MOUNT="$mnt"
VENDOR="$vendor"
PRODUCT="$product"
WSL="$wsl"
PM="$pm"
ARCH="$arch"
CPU_MODEL="$cpu_model"
CORES="$cores"
MEM_TOTAL_MB="$mem_total_mb"
MEM_USED_MB="$mem_used_mb"
MEM_AVAIL_MB="$mem_avail_mb"
STORE_TOTAL_MB="$store_total_mb"
STORE_FREE_MB="$store_free_mb"
BTF_EBPF="$btf"
HAVE_RUSTC="$have_rustc"
HAVE_CARGO="$have_cargo"
HAVE_PYTHON="$have_python"
HAVE_SANDBOX="$have_sandbox"
HAVE_BWRAP="$have_bwrap"
HAVE_PROOT="$have_proot"
HAVE_UNSHARE="$have_unshare"
PKG_COUNT="$pkg_count"
ENV
cat "$json_file"
