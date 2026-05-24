#!/usr/bin/env bash
set -euo pipefail

write_guest_entropy() {
  local guest_root="${1:?guest root required}"
  local entropy_file="$guest_root/run/camelot-guest.entropy"

  mkdir -p "$(dirname "$entropy_file")"
  umask 077

  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32 > "$entropy_file"
  else
    head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n' > "$entropy_file"
    printf '\n' >> "$entropy_file"
  fi
}

create_cow_snapshot() {
  local base_image="${1:?base image required}"
  local snapshot_image="${2:?snapshot image required}"

  if ! command -v qemu-img >/dev/null 2>&1; then
    echo "qemu-img is required for COW snapshot creation" >&2
    return 127
  fi

  qemu-img create -f qcow2 -F qcow2 -b "$base_image" "$snapshot_image"
}

main() {
  local command="${1:-}"
  shift || true

  case "$command" in
    entropy) write_guest_entropy "$@" ;;
    snapshot) create_cow_snapshot "$@" ;;
    *) echo "usage: $0 {entropy <guest-root>|snapshot <base.qcow2> <snapshot.qcow2>}" >&2; return 2 ;;
  esac
}

main "$@"

