@echo off
:: Launches the Camelot Network Optimization script with Administrator privileges
powershell -Command "Start-Process powershell.exe -ArgumentList '-NoExit -ExecutionPolicy Bypass -File \"%~dp0optimize-network.ps1\"' -Verb RunAs"
