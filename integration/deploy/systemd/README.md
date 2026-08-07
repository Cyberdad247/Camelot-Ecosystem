# Optional systemd --user units

These are **examples only** — development needs nothing but
`make dev-up` / `make dev-down`. Use them if you want the slice supervised
across logins on a Linux box.

Install:

```bash
# 1. Build once so .run/bin exists
cd ~/Camelot-Ecosystem/integration && make build

# 2. Adjust WorkingDirectory in the units if your checkout is elsewhere,
#    then link and start
mkdir -p ~/.config/systemd/user
cp integration/deploy/systemd/*.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now camelot-gateway camelot-node-agent camelot-console

# Status / logs
systemctl --user status camelot-gateway
journalctl --user -u camelot-gateway -f
```

Units declare `After=`/`Requires=` so the startup order matches
`dev-up.sh` (gateway → node-agent → console). Both services exit cleanly on
SIGTERM (systemd's default stop signal). On Termux or anywhere without
systemd, a tmux session running `make dev-up` is an equally valid supervisor.
