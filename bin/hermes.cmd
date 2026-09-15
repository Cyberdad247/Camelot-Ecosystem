@echo off
REM Camelot-OS — Hermes Agent CLI Proxy
REM Connects directly to the NousResearch Hermes Agent running on VPS Hub KVM563
if "%~1"=="" (
    ssh -t root@162.35.107.134 "docker exec -it hermes hermes"
) else (
    ssh root@162.35.107.134 "docker exec -i hermes hermes %*"
)
