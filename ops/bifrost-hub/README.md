# Bifrost Hub — OCI control-plane bootstrap

Bootstrap for the Camelot control plane on Oracle Cloud **Always Free**
`VM.Standard.A1.Flex` (ARM64), per the deployment plan:

- **OS:** Ubuntu 24.04 LTS ARM64
- **Shape:** VM.Standard.A1.Flex — 2 OCPU / 8 GB (within the 4-OCPU / 24-GB
  Always Free allowance; a 50 GB boot volume also fits the 200-GB free tier)
- **Roles:** Bifrost, Sentinel, task scheduler, cartridge/node registry,
  receipt service, SQLite WAL, encrypted backups, Tailscale, PWA/API backend
- **Access:** private/Tailscale-only — **no public ingress after bootstrap**

## Explicitly excluded (per plan)

No Docker/Kubernetes, no local LLM inference (Ollama, vLLM), no Neo4j/Weaviate,
no engineering build workers. This is the control plane, not a compute host.

## Launching the instance (OCI console)

1. Availability domain — any (AD 1 first; retry AD 2/3 on "out of capacity").
2. Capacity type — **On-demand** (the only Always Free-eligible option).
3. Image — **Ubuntu 24.04** (ARM64). Shape — **VM.Standard.A1.Flex**,
   2 OCPU / 8 GB. Boot volume 50 GB.
4. SSH keys — paste the public key from `~/.ssh/camelot_oci_ed25519.pub`.
5. VCN — quick-create default is fine; a public subnet is needed only for the
   bootstrap connection.
6. User data (Advanced options → Management) — paste the cloud-init block below.

## Cloud-init user data (paste into the instance at launch)

```yaml
#cloud-config
package_update: true
packages:
  - git
runcmd:
  - curl -fsSL https://raw.githubusercontent.com/Cyberdad247/Camelot-Ecosystem/main/ops/bifrost-hub/bootstrap.sh -o /root/bootstrap.sh
  - chmod +x /root/bootstrap.sh
  # Replace <TS_AUTHKEY> with a Tailscale auth key:
  # https://login.tailscale.com/admin/settings/keys
  - TS_AUTHKEY=<TS_AUTHKEY> /root/bootstrap.sh
```

> The raw URL only works after `ops/bifrost-hub/` lands on `main`. Until then,
> copy the whole dir up with `scp -r ops/bifrost-hub oci-admin:` and run
> `sudo TS_AUTHKEY=... ./bootstrap.sh` from inside it — bootstrap phase 6 wires
> `init-receipt-db.sh` and `receipt-service.service` in when they sit next to it
> (a lone `bootstrap.sh` skips them with a warning).

## After bootstrap

- Grab the Tailscale IP: `tailscale ip -4` on the box (or in the admin console).
- In `~/.ssh/config` set `oci-admin-ts` `HostName` to that IP.
- Admin over `ssh oci-admin-ts`; the public IP path is for bootstrap only.
- **Back up `/root/.config/age/bifrost-key.txt` offline** — the nightly backups
  are encrypted to it and are unrecoverable without it.
- **Receipt service** — bootstrap phase 6 already ran `init-receipt-db.sh`
  (creating `data/receipts.db` in WAL mode, tables mirroring
  `packages/contracts/receipt.schema.json` / `receipt-chain.schema.json`) and
  installed + enabled `receipt-service.service`. The unit stays inactive until
  the service binary is deployed to `/opt/camelot/bifrost-hub/bin/receipt-service`,
  then `sudo systemctl restart receipt-service`.

## Local SSH config (already in place)

```sshconfig
Host oci-admin
    HostName REPLACE_WITH_OCI_INSTANCE_PUBLIC_IP   # public IP — bootstrap only
    User ubuntu

Host oci-admin-ts
    HostName REPLACE_WITH_TAILSCALE_IP             # 100.x.y.z
    User ubuntu
    IdentityFile ~/.ssh/camelot_oci_ed25519
    IdentitiesOnly yes
```

## Verify

```bash
bash -n ops/bifrost-hub/bootstrap.sh          # syntax check
bash -n ops/bifrost-hub/init-receipt-db.sh
sudo TS_AUTHKEY=tskey-auth-XXXX ./bootstrap.sh
sudo /usr/local/bin/camelot-init-receipt-db   # idempotent; re-run any time
sqlite3 /opt/camelot/bifrost-hub/data/receipts.db 'PRAGMA journal_mode;'  # wal
sudo /usr/local/bin/camelot-backup && ls -l /opt/camelot/backups/
systemctl status receipt-service              # inactive until binary deployed
```
