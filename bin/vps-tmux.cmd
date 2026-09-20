@echo off
REM Camelot-OS - VPS Hub Tmux Multiplexer Bus Connector
ssh -i "%USERPROFILE%\.ssh\camelot_oci_ed25519" -o StrictHostKeyChecking=no -t root@100.110.180.18 "tmux a -t camelot-bus || tmux new-session -s camelot-bus"
