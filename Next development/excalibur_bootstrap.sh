#!/usr/bin/env bash
# ============================================================
# LUKAS_FORGE :: EXCALIBUR v1000.0.0 PRE-FLIGHT  (one-paste deploy)
# PROFILE: nitro-v15-cpu  (Acer Nitro V 15 / x86_64 / 8GB / CPU)
# ============================================================
set -o pipefail
ROOT="${EXCALIBUR_ROOT:-$HOME/excalibur}"
export EXCALIBUR_ROOT="$ROOT"
mkdir -p "$ROOT/core/audit_logs" "$ROOT/core/topology_maps"

cat > "$ROOT/core/excalibur_audit.sh" <<'___AUDIT_EOF___'
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
___AUDIT_EOF___

cat > "$ROOT/core/excalibur_adjudicate.sh" <<'___ADJ_EOF___'
#!/usr/bin/env bash
# core/excalibur_adjudicate.sh
# PRD 3 :: SIR BORIS :: zero-trust GO/NO-GO vs EXCALIBUR physical laws
# PROFILE: nitro-v15-cpu (Acer Nitro V 15 / x86_64 / 8GB / CPU)
ROOT="${EXCALIBUR_ROOT:-$HOME/excalibur}"
ENV_FILE="${1:-$ROOT/core/audit_logs/telemetry.env}"

# --- EXCALIBUR v1000.0.0 physical laws :: nitro-v15-cpu profile ---
ARCH_REQ="x86_64"
RAM_CEILING_MB=8192
RAM_EXPECT_MIN_MB=7000          # 8GB reports ~7.6GB usable after reserve
BOOT_SPRAWL_MAX_MB=1200         # RL-Conductor sprawl during boot (runtime gate)
TRELLIS_POOL_MB=512             # fixed KV-pool reservation
HEADROOM_REQ_MB=$(( BOOT_SPRAWL_MAX_MB + TRELLIS_POOL_MB ))   # 1712 pre-flight headroom
STORE_MIN_FREE_MB=4096          # Rust/WASM target dirs on a build box

[ -r "$ENV_FILE" ] || { echo "[NO-GO] telemetry env not readable: $ENV_FILE"; exit 2; }
# shellcheck disable=SC1090
. "$ENV_FILE"

violations=(); warns=(); missing=()

[ "$ARCH" = "$ARCH_REQ" ]   || violations+=("CPU arch '$ARCH' != required '$ARCH_REQ'")
[ "$HAVE_PYTHON" = "true" ] || { violations+=("missing toolchain: python3"); missing+=("python3"); }
[ "$HAVE_RUSTC" = "true" ]  || { violations+=("missing toolchain: rustc");   missing+=("rustc"); }
[ "$HAVE_CARGO" = "true" ]  || { violations+=("missing toolchain: cargo");   missing+=("cargo"); }
[ "$HAVE_SANDBOX" = "true" ]|| { violations+=("missing sandbox primitive (need bwrap|proot|unshare)"); missing+=("bubblewrap"); }

if [ "${MEM_AVAIL_MB:-0}" -lt "$HEADROOM_REQ_MB" ]; then
  violations+=("RAM headroom ${MEM_AVAIL_MB}MB < required ${HEADROOM_REQ_MB}MB (1.2GB sprawl + 512MB Trellis) -- close apps/browser")
fi
if [ "${STORE_FREE_MB:-0}" -lt "$STORE_MIN_FREE_MB" ]; then
  violations+=("Disk free ${STORE_FREE_MB}MB < required ${STORE_MIN_FREE_MB}MB for Rust/WASM artifacts")
fi

[ "${MEM_TOTAL_MB:-0}" -lt "$RAM_EXPECT_MIN_MB" ] && warns+=("total RAM ${MEM_TOTAL_MB}MB below expected ~${RAM_CEILING_MB}MB ceiling")
[ "$BTF_EBPF" = "true" ] || warns+=("kernel BTF/eBPF unavailable -- Aegis Shield falls back to regex-only PII redaction")
case "$PRODUCT" in *Nitro*|*ANV15*) : ;; *) warns+=("chassis '$PRODUCT' not confirmed Acer Nitro V 15");; esac
[ "$WSL" = "true" ] && warns+=("running under WSL -- eBPF/cgroup isolation may be constrained by the Windows host")

sprawl_gate=FAIL; [ "${MEM_AVAIL_MB:-0}" -ge "$HEADROOM_REQ_MB" ] && sprawl_gate=PASS

echo "==================== SIR BORIS :: ADJUDICATION ===================="
echo " profile ...... ${PROFILE:-n/a}"
echo " probe ........ ${TS:-n/a}"
echo " platform ..... ${VENDOR:-?} ${PRODUCT:-?}  (WSL=${WSL:-?}  pm=${PM:-?})"
echo " cpu .......... ${CPU_MODEL:-unknown}"
echo " arch ......... ${ARCH:-unknown} / ${CORES:-0} cores"
echo " ram .......... total ${MEM_TOTAL_MB:-0}MB | used ${MEM_USED_MB:-0}MB | avail ${MEM_AVAIL_MB:-0}MB"
echo " disk ......... free ${STORE_FREE_MB:-0}MB / total ${STORE_TOTAL_MB:-0}MB @ ${MOUNT:-home}"
echo " toolchain .... rustc=$HAVE_RUSTC cargo=$HAVE_CARGO python3=$HAVE_PYTHON sandbox=$HAVE_SANDBOX (bwrap=$HAVE_BWRAP proot=$HAVE_PROOT unshare=$HAVE_UNSHARE)"
echo " aegis ........ BTF/eBPF=$BTF_EBPF"
echo " sprawl gate .. runtime-DEFERRED :: pre-flight headroom = $sprawl_gate"
echo "-------------------------------------------------------------------"
for w in "${warns[@]}"; do echo " [warn] $w"; done

if [ "${#violations[@]}" -eq 0 ]; then
  echo "-------------------------------------------------------------------"
  echo " VERDICT: [GO] - substrate satisfies EXCALIBUR v1000.0.0 (nitro-v15-cpu)"
  echo "==================================================================="
  exit 0
else
  echo "-------------------------------------------------------------------"
  echo " VERDICT: [NO-GO] - ${#violations[@]} blocking constraint(s):"
  for v in "${violations[@]}"; do echo "   x $v"; done
  echo "-------------------------------------------------------------------"
  echo " REMEDIATION:"
  if [ "${#missing[@]}" -gt 0 ]; then
    case "$PM" in
      apt)    echo "   sudo apt update && sudo apt install -y python3 bubblewrap"; echo "   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh   # rustc+cargo" ;;
      dnf)    echo "   sudo dnf install -y python3 bubblewrap && curl --proto '=https' -sSf https://sh.rustup.rs | sh" ;;
      pacman) echo "   sudo pacman -S --needed python bubblewrap rustup && rustup default stable" ;;
      *)      echo "   install: ${missing[*]}  (+ rustup for rustc/cargo)" ;;
    esac
  fi
  echo "==================================================================="
  exit 1
fi
___ADJ_EOF___

cat > "$ROOT/core/excalibur_topology.md" <<'___TOPO_EOF___'
# EXCALIBUR v1000.0.0 — Topological Map :: PROFILE nitro-v15-cpu
> PRD 1 :: SIR HELIO :: CURRENT Acer Nitro V 15 substrate vs TARGET EXCALIBUR topology

```mermaid
flowchart TB
    subgraph CUR["CURRENT — Acer Nitro V 15 (pre-flight)"]
        direction TB
        C0["x86_64 CPU substrate · 8GB RAM"]
        C1["Linux / bash shell (WSL-aware)"]
        C2["NVMe SSD @ $HOME"]
        C3["python3 / rustc / cargo / bwrap ??? (unverified)"]
        C4["Flat process space — no KV governance, no isolation"]
        C0 --> C1 --> C2
        C1 --> C3
        C1 --> C4
    end
    subgraph TGT["TARGET — EXCALIBUR Topology (CPU-only)"]
        direction TB
        R["1.5B RL-Conductor<br/>(Runic routing / dispatch)"]
        O["Ouroboros Engine<br/>1.58-bit SSM · Zero KV-Cache"]
        T["Trellis<br/>512MB Fixed KV-Pool"]
        A["Aegis Shield<br/>eBPF(BTF) + Regex PII redaction"]
        Z["Omega-Root<br/>bubblewrap/unshare immutable chroot"]
        R -->|routes| O
        O -->|streams| T
        R -->|all I/O gated by| A
        A -.->|fault / breach| Z
        Z -.->|restore| R
    end
    C0 -.->|"audit: x86_64 / cores / 8GB ceiling"| R
    C3 -.->|"toolchain + sandbox gate"| A
    C2 -.->|"NVMe free-space gate (>=4GB)"| T
```

## Component → Pre-flight Gate Mapping (nitro-v15-cpu)
| EXCALIBUR Component | Physical Law | Audited By |
|---|---|---|
| 1.5B RL-Conductor | `uname -m == x86_64`, cores > 0 | Codex → Boris |
| Ouroboros (1.58-bit SSM, Zero KV) | MemAvailable ≥ 1712MB headroom | Codex → Boris |
| Trellis 512MB Fixed KV-Pool | avail RAM reserves 512MB | Boris |
| Aegis Shield (eBPF/Regex PII) | `/sys/kernel/btf/vmlinux` + sandbox primitive | Boris (eBPF=soft) |
| Omega-Root (immutable chroot) | NVMe free ≥ 4096MB + bwrap/proot/unshare | Boris |
___TOPO_EOF___

cat > "$ROOT/forge_deploy.sh" <<'___ORCH_EOF___'
#!/usr/bin/env bash
# forge_deploy.sh :: LUKAS_FORGE orchestrator :: PROFILE nitro-v15-cpu
# Sequence: SWARM SQUIRES -> SIR CODEX -> SIR HELIO -> SIR BORIS
set -o pipefail
ROOT="${EXCALIBUR_ROOT:-$HOME/excalibur}"
export EXCALIBUR_ROOT="$ROOT"

# --- SWARM SQUIRES :: concurrent scaffold ---
mkdir -p "$ROOT/core/audit_logs" &
mkdir -p "$ROOT/core/topology_maps" &
wait

# --- SIR CODEX :: probe -> JSON telemetry ---
bash "$ROOT/core/excalibur_audit.sh" >/dev/null

# --- SIR HELIO :: static topology at core/excalibur_topology.md ---

# --- SIR BORIS :: adjudication ---
bash "$ROOT/core/excalibur_adjudicate.sh"
___ORCH_EOF___

chmod +x "$ROOT/core/excalibur_audit.sh" "$ROOT/core/excalibur_adjudicate.sh" "$ROOT/forge_deploy.sh"
echo "[LUKAS_FORGE] nitro-v15-cpu artifacts materialized -> $ROOT"; echo
bash "$ROOT/forge_deploy.sh"
