# Bare-Metal Client Node Deployment Checklist

> **STOP — these files cannot be executed from this Windows dev host.** They
> are deployment-side templates authored on Windows and meant to be applied to
> the target Linux client node by an authorized operator. The Linux runtime
> paths (`/opt/camelot/...`, `/etc/systemd/system/...`, `/var/run/camelot/...`)
> do not exist on this Windows machine and `systemctl` is not available here.
> Invoke `camelotd.sh` directly on the Linux host, not via WSL or PowerShell.

This checklist implements the **Bare-Metal Client Node (Docker Purge)** plan
on a Linux client node. Docker is purged and replaced with native `systemd`
services + `cgroups v2` resource isolation. The 4GB Scarcity Protocol is
enforced directly by the kernel, not by daemon bloat.

## 1. Preflight

- [ ] Confirm cgroups v2 is mounted: `mount | grep cgroup2` → expect
      `/sys/fs/cgroup ... cgroup2 cgroup2 ...`. If only cgroup v1 is mounted,
      the operator must migrate (see kernel docs for `cgroup_no_v1=` boot
      parameter).
- [ ] Confirm systemd ≥ 230: `systemctl --version | head -1`. The
      `MemoryMax=` / `MemorySwapMax=` / `CPUWeight=` directives are silently
      ignored on older systemd, which means the 4GB Scarcity Protocol would
      effectively be disabled even though the units install cleanly.
- [ ] Confirm `User=camelot` exists and owns `/opt/camelot`.
- [ ] Confirm `/var/run/camelot` and `/var/log/camelot` are writable by
      `camelot` (the daemon writes PID files + log streams there).
- [ ] Confirm `/opt/camelot/cartridges/kba-executive-assistant/www/` exists.
- [ ] Confirm `/opt/camelot/os/lib/bus.js` and
      `/opt/camelot/system/gateway/server.js` exist (these are open-items — see §6).

## 2. Install the systemd units

```sh
# From the deploy artifact root (this Windows-authored cmd/pulse/ops/ tree,
# copied onto the Linux node).
sudo install -m 0644 \
    cmd/pulse/ops/systemd/camelot-kickbox.service \
    /etc/systemd/system/camelot-kickbox.service
sudo install -m 0644 \
    cmd/pulse/ops/systemd/camelot-openmontage.service \
    /etc/systemd/system/camelot-openmontage.service

sudo systemctl daemon-reload
sudo systemctl enable --now camelot-kickbox camelot-openmontage
```

Verify the kernel actually received the cgroup caps:

```sh
systemctl show camelot-kickbox.service -p MemoryMax -p MemorySwapMax -p CPUWeight
#   MemoryMax=2147483648
#   MemorySwapMax=536870912
#   CPUWeight=80

systemctl show camelot-openmontage.service -p MemoryMax -p MemorySwapMax -p CPUWeight
#   MemoryMax=1073741824
#   MemorySwapMax=268435456
#   CPUWeight=50
```

## 3. Install the daemon orchestrator

```sh
sudo install -m 0755 \
    cmd/pulse/ops/camelotd.sh \
    /opt/camelot/os/bin/camelotd
```

**Run interactively as root or under sudo** (`sudo bash /opt/camelot/os/bin/camelotd`)
for first-boot verification. The script internally shells `sudo systemctl start …`
for both units — if invoked without root/sudo, those calls block on auth prompts
partway through (after `bus.js` is already running with a PID file but before
the systemd kickbox check fires), leaving the daemon in a half-started state.
Then convert to an operator-level process if long-running
supervision is needed (the systemd units themselves are the long-running
supervisor for camelot-kickbox / camelot-openmontage; the bash script is
typically only used at bootstrap or in a tmux for live log tailing).

## 4. Smoke-tests

- [ ] `curl -fsS http://127.0.0.1:8001/<healthcheck>` → 200 (kickbox audio kernel).
      The actual healthcheck path is owned by `main.py`'s contract — `main.py`
      is OUT-OF-REPO (see §6), so the operator confirms the path against the
      actual server source before relying on this test.
- [ ] `curl -fsS http://127.0.0.1:8002/<healthcheck>` → 200 (openmontage video
      synthesizer; same caveat — `server.py` is OUT-OF-REPO).
- [ ] `cat /sys/fs/cgroup/system.slice/camelot-kickbox.service/memory.max`
      → `2147483648`
- [ ] `cat /sys/fs/cgroup/system.slice/camelot-openmontage.service/memory.max`
      → `1073741824`
- [ ] `ss -tlnp | grep -E ':(8001|8002|8443)'` → all three sockets present
      (8001/8002 service ports, 8443 cartridge gateway WSS)

## 5. Rollback (return to Docker)

If an operator flags a regression and the Docker compose tree is still on the
host, restore it cleanly:

```sh
sudo systemctl disable --now camelot-kickbox camelot-openmontage
sudo rm -f /etc/systemd/system/camelot-kickbox.service \
         /etc/systemd/system/camelot-openmontage.service
sudo systemctl daemon-reload
sudo mv /opt/camelot/system/kickbox-audio/docker-compose.yml.bak.baremetal \
       /opt/camelot/system/kickbox-audio/docker-compose.yml
# Operator then runs the previous docker-compose workflow.
```

If the Docker compose tree is NOT present on this host, the rollback path is
to restore from a backup or re-pull the previous image. The `*service` files
are inert once `disable` + `rm` run, so there is no kernel-state leak.

## 6. Open items (runtime dependencies)

These runtime paths are referenced by the unit files + daemon script but are
**not in this repo**. The operator must materialize them on the Linux client
node before `systemctl start` succeeds:

| Path                                                         | Owner   | Status      |
| ------------------------------------------------------------ | ------- | ----------- |
| `/opt/camelot/system/kickbox-audio/main.py`                  | camelot | OUT-OF-REPO |
| `/opt/camelot/system/kickbox-audio/.venv/bin/python`         | camelot | OUT-OF-REPO |
| `/opt/camelot/system/openmontage/server.py`                 | camelot | OUT-OF-REPO |
| `/opt/camelot/system/openmontage/.venv/bin/python`           | camelot | OUT-OF-REPO |
| `/opt/camelot/os/lib/bus.js`                                 | camelot | OUT-OF-REPO |
| `/opt/camelot/system/gateway/server.js`                      | camelot | OUT-OF-REPO |
| `/opt/camelot/cartridges/kba-executive-assistant/www/`       | camelot | OUT-OF-REPO |

The Node.js `Kickbox-audio` monorepo checked into this workspace is the
**browser-side audio kernel** (PWA + Bifrost API); it is not the Python-side
audio kernel referenced by the systemd unit. When the operator materializes
the Python kernel they should either (a) port the existing PWA logic to a
Python audio engine and compile to `main.py`, or (b) treat the PWA as a
remote client and run a new server-side Python audio engine next to it.

## 7. Secret handling

`Environment=` directives in the systemd units carry non-secret config
(`PORT`, `STT_MODEL`, `TTS_MODEL`, `KICKBOX_MODE`). API keys, operator
tokens, JWT signing secrets, and DB credentials MUST be sourced from
`/etc/camelot/secrets.env` (mode 0600, owner `camelot`), which the service
loads via `EnvironmentFile=-/etc/camelot/secrets.env`. The leading `-`
marks the file **optional at boot**: systemd starts the service even if
`secrets.env` is missing, and the operator can populate it later without
restarting the unit. Without the `-`, missing secrets would surface as
`status=2/INVALIDARGUMENT` at first boot, which is too noisy for an
operator who wants to bootstrap the service and populate keys
incrementally. Never paste secrets into the `.service` files themselves —
they end up in `systemctl show` output which is world-readable by
default, mode 0600 on `secrets.env` keeps the values confined to the
`camelot` runtime user.
