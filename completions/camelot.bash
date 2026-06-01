# CAMELOT-OS Bash Tab Completion — WARP_GATE v1.0.0
# Install: source completions/camelot.bash
# Or:      camelot shell-setup --shell bash

_camelot_complete() {
    local cur prev words cword
    _init_completion || return

    local subcommands="configure config status install build update warp shell-setup keys"
    local knights="sir_boris sir_helio sir_forge sir_sentinel sir_alex sir_link sir_ghost sir_debug lady_apis lady_mnemosyne"
    local flags="--version --help --verbose --no-context --knight --system --route"

    case "$prev" in
        --knight|-k)
            COMPREPLY=( $(compgen -W "$knights" -- "$cur") )
            return ;;
        --system|-s)
            COMPREPLY=( $(compgen -f -- "$cur") )
            return ;;
        shell-setup)
            COMPREPLY=( $(compgen -W "--shell" -- "$cur") )
            return ;;
        --shell)
            COMPREPLY=( $(compgen -W "bash zsh fish powershell" -- "$cur") )
            return ;;
    esac

    # First positional arg — offer sub-commands
    if [[ "${words[1]}" == "$cur" || "${#words[@]}" -le 2 ]]; then
        COMPREPLY=( $(compgen -W "$subcommands $flags" -- "$cur") )
        return
    fi

    COMPREPLY=( $(compgen -W "$flags" -- "$cur") )
}

complete -F _camelot_complete camelot
complete -F _camelot_complete ai
