#!/usr/bin/env bash
set -euo pipefail

verify_with_z3() {
  local model_file="${1:?z3 model file required}"

  if ! command -v z3 >/dev/null 2>&1; then
    echo "z3 is required for OpenSRE v2 safety verification" >&2
    return 127
  fi

  local result
  result="$(z3 "$model_file")"
  case "$result" in
    *unsat*) return 0 ;;
    *) echo "unsafe patch model: $result" >&2; return 1 ;;
  esac
}

verify_and_apply_patch() {
  local z3_model="${1:?z3 model file required}"
  local patch_file="${2:?patch file required}"
  local target_dir="${3:-.}"

  verify_with_z3 "$z3_model"
  git -C "$target_dir" apply --check "$patch_file"
  git -C "$target_dir" apply "$patch_file"
}

main() {
  local command="${1:-}"
  shift || true

  case "$command" in
    verify) verify_with_z3 "$@" ;;
    apply) verify_and_apply_patch "$@" ;;
    *) echo "usage: $0 {verify <model.smt2>|apply <model.smt2> <patch.diff> [target-dir]}" >&2; return 2 ;;
  esac
}

main "$@"

