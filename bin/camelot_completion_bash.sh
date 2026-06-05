# CAMELOT-OS bash/zsh completion
# Source in ~/.bashrc:   eval "$(camelot completion bash)"
# Source in ~/.zshrc:    eval "$(camelot completion zsh)"
#
# Or write to file:
#   camelot completion bash > /etc/bash_completion.d/camelot
#   camelot completion zsh  > "${fpath[1]}/_camelot"

_camelot_knights=(
  sir_boris sir_alex sir_sentinel sir_mnemo sir_codex sir_helio
  sir_link sir_liberte sir_forge sir_ghost sir_forge_master
  sir_gideon sir_octavian lady_apis
)

_camelot_subcommands=(
  configure config status install build update warp
  shell-setup keys cockpit completion
)

_camelot_tiers=(T0 T1 T2 T3)

_camelot_complete() {
  local cur prev words cword
  _init_completion 2>/dev/null || {
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
  }

  case "$prev" in
    --knight|-k)
      COMPREPLY=( $(compgen -W "${_camelot_knights[*]}" -- "$cur") )
      return 0
      ;;
    --tier)
      COMPREPLY=( $(compgen -W "${_camelot_tiers[*]}" -- "$cur") )
      return 0
      ;;
    --system|-s)
      COMPREPLY=( $(compgen -f -- "$cur") )
      return 0
      ;;
    completion)
      COMPREPLY=( $(compgen -W "bash zsh fish powershell" -- "$cur") )
      return 0
      ;;
  esac

  # First arg: subcommands + global flags
  if [[ ${COMP_CWORD} -eq 1 ]]; then
    local opts="${_camelot_subcommands[*]} --knight --no-context --system --verbose --version -k -n -s -v -V"
    COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
    return 0
  fi

  # Sub-command specific completions
  local subcmd="${COMP_WORDS[1]}"
  case "$subcmd" in
    configure|config)
      COMPREPLY=( $(compgen -W "--verbose --no-keyring --secure" -- "$cur") )
      ;;
    status)
      COMPREPLY=( $(compgen -W "--json --knight" -- "$cur") )
      ;;
    build)
      COMPREPLY=( $(compgen -W "--platform --onefile --no-upx" -- "$cur") )
      ;;
    shell-setup)
      COMPREPLY=( $(compgen -W "--prompt-integration --no-completion --dry-run" -- "$cur") )
      ;;
    warp|"")
      COMPREPLY=( $(compgen -W "--knight -k --no-context -n --system -s --verbose -v" -- "$cur") )
      ;;
  esac
  return 0
}

complete -F _camelot_complete camelot
complete -F _camelot_complete ai
