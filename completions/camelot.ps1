# CAMELOT-OS PowerShell Tab Completion — WARP_GATE v1.0.0
# Install: Add-Content $PROFILE (Get-Content camelot.ps1 -Raw)
# Or:      camelot shell-setup --shell powershell

$_CamelotSubCommands = @(
    'configure', 'config', 'status', 'install', 'build',
    'update', 'warp', 'shell-setup', 'keys', 'cockpit'
)

$_CamelotKnights = @(
    'sir_boris', 'sir_helio', 'sir_forge', 'sir_sentinel',
    'sir_alex', 'sir_link', 'sir_ghost', 'sir_debug',
    'lady_apis', 'lady_mnemosyne'
)

$_CamelotFlags = @(
    '--version', '--help', '--verbose', '--no-context',
    '--knight', '--system', '--route'
)

Register-ArgumentCompleter -Native -CommandName @('camelot', 'ai') -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $tokens = $commandAst.CommandElements
    $tokenCount = $tokens.Count

    # First arg position — complete sub-commands
    if ($tokenCount -le 2) {
        $all = $_CamelotSubCommands + $_CamelotFlags
        $all | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new(
                $_, $_, 'ParameterValue', $_
            )
        }
        return
    }

    # After --knight flag — complete knight names
    $prev = $tokens[$tokenCount - 2].ToString()
    if ($prev -in @('--knight', '-k')) {
        $_CamelotKnights | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new(
                $_, $_, 'ParameterValue', $_
            )
        }
        return
    }

    # After shell-setup — complete shell types
    if ($tokens[1].ToString() -eq 'shell-setup') {
        @('powershell', 'bash', 'zsh', 'fish') |
            Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new(
                "--shell $_ ", "--shell $_", 'ParameterValue', "$_ shell"
            )
        }
        return
    }

    if ($tokens[1].ToString() -eq 'cockpit' -and $tokenCount -le 3) {
        @('prompt', 'exec', 'refresh', 'chat') |
            Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
            [System.Management.Automation.CompletionResult]::new(
                $_, $_, 'ParameterValue', $_
            )
        }
        return
    }

    # Generic flags
    $_CamelotFlags | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new(
            $_, $_, 'ParameterValue', $_
        )
    }
}
