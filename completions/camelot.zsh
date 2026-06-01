#compdef camelot ai
# CAMELOT-OS Zsh Tab Completion — WARP_GATE v1.0.0
# Install: fpath=(path/to/completions $fpath); compinit
# Or:      camelot shell-setup --shell zsh

_camelot() {
    local state

    local -a subcommands
    subcommands=(
        'configure:Run auto-configuration engine'
        'config:Alias for configure'
        'status:Probe all services and show health matrix'
        'install:First-time install guide'
        'build:Build portable binary via PyInstaller'
        'update:Pull latest CLAUDE.md and cartridges'
        'warp:Warp into Camelot-OS REPL (default)'
        'shell-setup:Install tab completion for your shell'
        'keys:Manage API keys in system keyring'
    )

    local -a knights
    knights=(
        'sir_boris:Lead architect, orchestration, Crucible'
        'sir_helio:1M context, cloud burst, Gemini'
        'sir_forge:Code gen, kinetic toolchain'
        'sir_sentinel:Security, audit, AgentArmor'
        'sir_alex:Cognitive cartridge, reasoning chains'
        'sir_link:Bridge coordination, Switchboard ATC'
        'sir_ghost:Air-gapped, privacy-critical, zero-cloud'
        'sir_debug:Testing, PIV self-healing'
        'lady_apis:Research, foraging, BASHR loop'
        'lady_mnemosyne:Long-term memory, Living Notebook'
    )

    _arguments -C \
        '(-V --version)'{-V,--version}'[Print version and exit]' \
        '(-h --help)'{-h,--help}'[Show help]' \
        '(-v --verbose)'{-v,--verbose}'[Show routing and context details]' \
        '(-n --no-context)'{-n,--no-context}'[Skip CLAUDE.md injection]' \
        '(-k --knight)'{-k,--knight}'[Force specific knight]:knight:->knight' \
        '(-s --system)'{-s,--system}'[Override system prompt]:file:_files' \
        '--route[Show routing decision and exit]' \
        '1:subcommand:->subcommand' \
        '*::args:->args'

    case "$state" in
        subcommand)
            _describe 'subcommand' subcommands ;;
        knight)
            _describe 'knight' knights ;;
        args)
            case "${words[1]}" in
                shell-setup)
                    _arguments '--shell[Shell type]:shell:(bash zsh fish powershell)' ;;
                keys)
                    _arguments '1:action:(set get delete list)' ;;
            esac
            ;;
    esac
}

_camelot "$@"
