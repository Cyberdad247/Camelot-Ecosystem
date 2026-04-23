# [SYSTEM_CALL] :: Ω_FORGE_CLI_INTERCEPTOR
# [ARCHITECT] :: SIR_FORGE (The Builder)
# [CONTEXT] :: Camelot Apex v209.0 Kinetic Stack

<🏆> THE PRIME DIRECTIVE
Write the complete Python script for `camelot_cli.py` to serve as the Read-Eval-Print Loop (REPL) entry point for the Camelot-OS architecture.

### ⚙️ CORE REQUIREMENTS (The Logic)

1. **The REPL Loop:**
   - Implement an interactive `while True:` loop that accepts user input via a styled terminal prompt (e.g., `[👑 Sovereign Input]: `).

2. **The Interception Engine (Runic Routing):**
   - The parser must intercept any command starting with `//` or `Ω_`.
   - **Condition 1 (`//FORGE`):** If the input starts with `//FORGE`, bypass the LLM entirely. Use Python's `subprocess.run` to directly execute the local Rust bundler: `cribo --entry src/main.py --output bundle.py`. Print a success or error message based on the kinetic execution.
   - **Condition 2 (`Ω_SYNC` or other runes):** Add a stub for `Ω_SYNC` that prints "[Ouroboros Sync Triggered]".

3. **The Saltare Gateway (Natural Language):**
   - If the input does NOT start with `//` or `Ω_` (standard text), treat it as a natural language query.
   - Do not process it locally. Forward the prompt to the Saltare MCP Gateway using the `requests` library.
   - POST the input to `http://localhost:8080/route` with the JSON payload: `{"query": user_input}`.
   - Print the resulting `tool_to_call` or textual response from the gateway.

### 📜 CONSTRAINTS
- Use pure Python (`sys`, `subprocess`, `requests`).
- Add robust error handling (e.g., `requests.exceptions.ConnectionError` if Saltare is down).
- Ensure the REPL handles `Ctrl+C` or `exit` gracefully to terminate the OS.

Execute this immediately and output the full `camelot_cli.py` code block.

--------------------------------------------------------------------------------