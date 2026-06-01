# CAMELOT-OS Fish Tab Completion — WARP_GATE v1.0.0
# Install: cp camelot.fish ~/.config/fish/completions/
# Or:      camelot shell-setup --shell fish

# Disable file completion by default
complete -c camelot -f
complete -c ai      -f

# Sub-commands
complete -c camelot -n '__fish_use_subcommand' -a configure  -d 'Auto-configure environment'
complete -c camelot -n '__fish_use_subcommand' -a config     -d 'Alias for configure'
complete -c camelot -n '__fish_use_subcommand' -a status     -d 'Probe all services'
complete -c camelot -n '__fish_use_subcommand' -a install    -d 'First-time install guide'
complete -c camelot -n '__fish_use_subcommand' -a build      -d 'Build portable binary'
complete -c camelot -n '__fish_use_subcommand' -a update     -d 'Pull latest config'
complete -c camelot -n '__fish_use_subcommand' -a warp       -d 'Warp into Camelot-OS REPL'
complete -c camelot -n '__fish_use_subcommand' -a shell-setup -d 'Install tab completion'
complete -c camelot -n '__fish_use_subcommand' -a keys       -d 'Manage API keys in keyring'

# Global flags
complete -c camelot -s V -l version    -d 'Print version'
complete -c camelot -s h -l help       -d 'Show help'
complete -c camelot -s v -l verbose    -d 'Verbose routing/context'
complete -c camelot -s n -l no-context -d 'Skip CLAUDE.md injection'
complete -c camelot -s k -l knight     -d 'Force knight' -r -a '
    sir_boris\t"Lead architect"
    sir_helio\t"1M context / Gemini"
    sir_forge\t"Code gen"
    sir_sentinel\t"Security audit"
    sir_alex\t"Reasoning chains"
    sir_link\t"Switchboard ATC"
    sir_ghost\t"Air-gapped / privacy"
    sir_debug\t"Self-healing tests"
    lady_apis\t"Research / BASHR"
    lady_mnemosyne\t"Long-term memory"
'
complete -c camelot -s s -l system    -d 'Override system prompt' -r -F
complete -c camelot -l route           -d 'Show routing and exit'

# shell-setup --shell completion
complete -c camelot -n '__fish_seen_subcommand_from shell-setup' -l shell -r -a '
    bash\t"Bash"
    zsh\t"Zsh"
    fish\t"Fish"
    powershell\t"PowerShell"
'

# keys sub-command
complete -c camelot -n '__fish_seen_subcommand_from keys' -a 'set get delete list'

# Mirror all completions for `ai` alias
complete -c ai -f
for c in (complete -c camelot)
    eval "complete -c ai $c"
end
