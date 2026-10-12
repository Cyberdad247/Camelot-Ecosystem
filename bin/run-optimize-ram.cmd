@echo off
:: Launches the Camelot RAM Optimization script with Administrator privileges
powershell -Command "Start-Process powershell.exe -ArgumentList '-NoExit -ExecutionPolicy Bypass -File \"%~dp0..\scripts\ops\optimize_ram.ps1\" -Elevate' -Verb RunAs"
