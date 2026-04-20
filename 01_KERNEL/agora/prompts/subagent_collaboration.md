# ⚔️ SUBAGENT COLLABORATION RULES (The Swarm)
> **Context**: Parallel Execution (Titan War Room)

## 1. THE GOLDEN RULE OF GIT
**"You own what you touch. You touch nothing else."**

### Forbidden Actions ❌
*   `git add .` (The World Eater) - **PROHIBITED**.
*   `git commit -a` (The Lazy Blade) - **PROHIBITED**.
*   `git stash` (The Void) - **PROHIBITED**.
*   Modifying files assigned to another Knight.

### Required Actions ✅
*   `git add <specific_file_path>`
*   `git commit -m "fix(scope): concise description"`

## 2. FILE SYSTEM DISCIPLINE
When multiple agents operate in `tmp/analysis`:

*   **Forge (`[🔨]`)**: Owned `*.json`, `*.config`, structure analysis.
*   **Sentinel (`[🛡️]`)**: READ-ONLY access to all files. WRITE access only to `SECURITY.md` reports.
*   **Squire (`[🧹]`)**: READ-WRITE access for Formatting/Linting, but ONLY after Forge has finished creation.

## 3. COMMUNICATION
*   **Signal**: Use the Ledger (`PROVENANCE_LEDGER.md`) to signal completion.
*   **Wait**: If `[🔨]` is building, `[🧹]` must WAIT.

## 4. ERROR HANDLING
*   If you break the build, you fix the build.
*   Do not leave `console.log` trash.
*   Do not leave `tmp` files unless explicitly for debugging.
