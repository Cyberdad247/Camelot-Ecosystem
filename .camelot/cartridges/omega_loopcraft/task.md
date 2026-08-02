# Task DAG — omega_loopcraft

This document represents the execution DAG for compiling, packaging, and verifying the `omega_loopcraft` cartridge.

## Compilation & Packaging Sequence

```
  [Compile UI] ------> [Export Static HTML] --+
                                               |--> [Package Cartridge Zip]
  [Freeze Python] ---> [Collect stdio Deps] --+
```

### 1. Compile and Export Static Frontend
Compiles the Next.js App Router project into a static, serverless directory structure under `/ui_shell/out`:
```bash
# Navigate to UI directory
cd ui_shell

# Install node dependencies
npm install

# Build & export static assets
npm run build
```
*(Ensure `next.config.js` is configured with `output: 'export'`)*

### 2. Freeze Python dependencies
Packages the FastAPI stdio MCP engine dependencies into a standard requirements file:
```bash
# Navigate to MCP engine directory
cd ../mcp_engine

# Activate virtual environment
.venv\Scripts\activate

# Freeze dependencies
pip freeze > requirements.txt
```

### 3. Compress Cartridge Package
Create the final deployable zip package containing the static assets, stdio engine, and manifest metadata:
```powershell
# Run from repository root C:\Users\vizio\CAMELOT_OS
Compress-Archive -Path .camelot/cartridges/omega_loopcraft/* -DestinationPath dist/omega_loopcraft.zip -Force
```
