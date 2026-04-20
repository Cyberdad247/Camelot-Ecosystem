@echo off
REM ============================================================
REM  Camelot Apex OS — Local Ollama Launcher (Cybertron Iron)
REM  Wraps Claude Code CLI to use local Ollama models.
REM  CPU/GPU fallback: detects CUDA, falls back to CPU-only.
REM ============================================================

setlocal enabledelayedexpansion

REM ── Configuration ──────────────────────────────────────────
set "CLAUDE_OLLAMA_MODEL=qwen2.5-coder:3b"
set "OLLAMA_HOST=http://127.0.0.1:11434"
set "CAMELOT_OS=%~dp0"

REM ── GPU Detection & Fallback ───────────────────────────────
REM Check if nvidia-smi is available (CUDA GPU present)
where nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [CYBERTRON] No NVIDIA GPU detected. Forcing CPU-only mode.
    set "CUDA_VISIBLE_DEVICES=-1"
    set "OLLAMA_NUM_GPU=0"
    goto :check_ram
)

REM GPU found — check VRAM
for /f "tokens=*" %%i in ('nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2^>nul') do (
    set "VRAM_FREE=%%i"
)

REM If less than 2GB VRAM free, fall back to CPU
if defined VRAM_FREE (
    if !VRAM_FREE! lss 2048 (
        echo [CYBERTRON] Low VRAM: !VRAM_FREE!MB free. Forcing CPU-only to prevent OOM.
        set "CUDA_VISIBLE_DEVICES=-1"
        set "OLLAMA_NUM_GPU=0"
    ) else (
        echo [CYBERTRON] GPU active: !VRAM_FREE!MB VRAM free. CUDA enabled.
        set "OLLAMA_NUM_GPU=999"
    )
) else (
    echo [CYBERTRON] Could not query VRAM. Defaulting to CPU-only.
    set "CUDA_VISIBLE_DEVICES=-1"
    set "OLLAMA_NUM_GPU=0"
)

:check_ram
REM ── RAM Ceiling Check (8GB Titanium Law) ───────────────────
for /f "tokens=2 delims==" %%a in ('wmic OS get FreePhysicalMemory /value 2^>nul') do (
    set /a "FREE_RAM_MB=%%a / 1024"
)

if defined FREE_RAM_MB (
    if !FREE_RAM_MB! lss 1024 (
        echo [CYBERTRON] WARNING: Only !FREE_RAM_MB!MB RAM free. Model may swap.
        echo [CYBERTRON] Consider closing applications or using a smaller model.
    ) else (
        echo [CYBERTRON] RAM: !FREE_RAM_MB!MB free. Within 8GB ceiling.
    )
)

REM ── Ollama Health Check ────────────────────────────────────
echo [CYBERTRON] Checking Ollama at %OLLAMA_HOST%...
curl -sf "%OLLAMA_HOST%/api/tags" >nul 2>&1
if %errorlevel% neq 0 (
    echo [CYBERTRON] Ollama not running. Starting...
    start /b ollama serve >nul 2>&1
    timeout /t 3 /nobreak >nul
    curl -sf "%OLLAMA_HOST%/api/tags" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [CYBERTRON] ERROR: Cannot reach Ollama. Install from https://ollama.com
        exit /b 1
    )
)

REM ── Model Pull Check ───────────────────────────────────────
echo [CYBERTRON] Verifying model: %CLAUDE_OLLAMA_MODEL%
curl -sf "%OLLAMA_HOST%/api/tags" | findstr /i "%CLAUDE_OLLAMA_MODEL%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [CYBERTRON] Model not found locally. Pulling %CLAUDE_OLLAMA_MODEL%...
    ollama pull %CLAUDE_OLLAMA_MODEL%
    if %errorlevel% neq 0 (
        echo [CYBERTRON] ERROR: Failed to pull model.
        exit /b 1
    )
)

REM ── Launch ─────────────────────────────────────────────────
echo [CYBERTRON] Launching Claude Code with local Ollama backend.
echo [CYBERTRON] Model: %CLAUDE_OLLAMA_MODEL% @ %OLLAMA_HOST%
echo.

REM Set environment for Claude Code Ollama integration
set "ANTHROPIC_BASE_URL=%OLLAMA_HOST%/v1"
set "ANTHROPIC_MODEL=%CLAUDE_OLLAMA_MODEL%"

REM Pass through all arguments to claude
if "%~1"=="" (
    echo Usage: claude-ollama.cmd [--help ^| --print "prompt" ^| chat]
    echo.
    echo Environment:
    echo   CLAUDE_OLLAMA_MODEL = %CLAUDE_OLLAMA_MODEL%
    echo   OLLAMA_HOST         = %OLLAMA_HOST%
    echo   CUDA_VISIBLE_DEVICES= %CUDA_VISIBLE_DEVICES%
    echo   OLLAMA_NUM_GPU      = %OLLAMA_NUM_GPU%
    exit /b 0
)

claude %*

endlocal
