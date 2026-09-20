@echo off
title CAMELOT-OS VPS Hub Tmux Bus (KVM563)
echo ===================================================
echo   CAMELOT-OS VPS HUB TMUX BUS - ROOT SESSION
echo   Connecting to root@100.110.180.18 (camelot-bus)...
echo ===================================================
ssh -i "%USERPROFILE%\.ssh\camelot_oci_ed25519" -o StrictHostKeyChecking=no -t root@100.110.180.18 "tmux a -t camelot-bus"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo SSH connection ended with code %ERRORLEVEL%.
    pause
)
