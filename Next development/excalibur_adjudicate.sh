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
