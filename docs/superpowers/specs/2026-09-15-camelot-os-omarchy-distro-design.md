# Camelot-OS on Omarchy — Distro Design

## Status

Proposed architecture. This document defines the implementation boundary for
building **Camelot-OS** as a bootable x86_64 distribution derived from the
Omarchy stack. It is a design boundary, not an execution instruction, and it
contains no credentials.

Anya Gate triage of the originating intent returned:

```
priority=HIGH  hitl_tier=PROMPT  risk_entropy=0.45
assigned_knight=sir_link  cartridge_hint=BEAVER
requires_z3_verification=False  auto_dispatchable=False
```

`PROMPT` means the plan travels to the operator for approval before any
task executes. `HIGH` means no task in this plan may self-approve a publish step.

## Goal

Ship a bootable, unattended-installable x86_64 distribution that boots into the
Omarchy desktop and comes up already running the Camelot-OS agent stack as native
systemd services, on consumer hardware down to a 4 GB floor and 8 GB target, with
**zero Docker anywhere** in the build, runtime, or hub path.

The installed machine is a sovereign node. The VPS hub (KVM563) remains the
policy and artifact authority. Hermes consumes sealed release artifacts.

## Non-goals

- aarch64 / ARM SBC / Raspberry Pi support. x86_64 only for this release line.
- Running any container runtime on the installed node, the builder, or the hub.
- Replacing the VPS Bifrost gateway, runic router, or the S26 command center.
- Rebranding the Omarchy desktop shell beyond a theme/profile layer.
- Publishing the ISO publicly. That is an open question, not an assumed default.
- Fixing pre-existing container usage outside the distro path. Those surfaces are
  inventoried and tracked as debt, not silently rewritten.

## Findings that shaped this design

Each finding below was read out of the live tree. Evidence class is assigned per
the root `AGENTS.md` scheme.

| # | Finding | Evidence | Class |
| --- | --- | --- | --- |
| F1 | Prior Omarchy work exists but is fragmentary: a sealed cartridge, an agent-name matrix, and two headless verifiers. There is no spec and no plan. | `03_VAULT/runtime_state/cartridges/omarchy-vps-hermes-v1.json`, `control_plane/dispatch/omarchy_agent_matrix.py`, `control_plane/runners/omarchy_headless_verifier.py`, `apps/camelot-vps-hub/infra/scripts/verify-omarchy-headless.sh` | confirmed |
| F2 | No `archiso`, `mkarchiso`, `devtools`, or `archbuild` reference exists anywhere in the tree, and no inventory entry describes an Arch-capable build host. | repo-wide search returned zero distro-toolchain matches | confirmed |
| F3 | `omarchy-pkgs` uses containers to build. Upstream README states foreign-arch builds run under QEMU via rootful Docker or rootless Podman, and that each channel builds "in its own image against its own base mirror". | `omacom/omarchy-pkgs` README | confirmed |
| F4 | `control_plane/cartridges/qr_bridge.py` advertises Ed25519 signing but produces a keyless digest. `encode_and_sign_artifact` computes `signature = hashlib.sha256(raw_msg).hexdigest()` and `verify_qr_payload` recomputes the same keyless hash. There is no private key and no signature. | `control_plane/cartridges/qr_bridge.py:57`, `:90-103` | confirmed defect |
| F5 | Existing agent-name matrix routes Hermes by shelling into a container: `ssh root@162.35.107.134 "docker exec -i hermes hermes ..."`. | `control_plane/dispatch/omarchy_agent_matrix.py:generate_omarchy_mise_stub` | confirmed |
| F6 | The "no Docker" northstar is already latent in the repo's own governance templates, which name "Zero Docker footprint (100% bare-metal systemd/WASM/Rust)" as a success criterion and "Strict compliance with Rule 7 zero-hotpath bare-metal doctrine" as an architecture gate. | `control_plane/03_VAULT/Missions/verification_ledger.jsonl` entries 322-324 | confirmed |
| F7 | Anya Gate routes a distro-build intent to `sir_link` (A2A bridge, SkillGraph S4), not to `SIR_KAY` (who owns `//ENGINEERING_SPRINT` and `//DIRECT_BUILD` per the root roster). `sir_link` is a real router knight but is absent from the root `AGENTS.md` roster table. | `control_plane/core/soul_router.py:93`, root `AGENTS.md` roster | confirmed drift |

F1 scopes the work: this is largely greenfield against a fragmentary base.

F2 is the schedule risk. `mkarchiso` requires a privileged Arch environment with
loop-device access. It cannot run on this Windows workstation and it cannot run
directly on the Ubuntu hub. **A builder host is a prerequisite task, not an
assumption.** Treating it as an assumption is the single most likely way this plan
stalls.

F4 is why the seal design in this spec is specified by *test behaviour* rather
than by field name. See "Seal requirements".

F7 is a routing decision for the operator: either the roster gains `sir_link` or
the distro intent lane is repointed at `SIR_KAY`. This spec does not silently pick.

## Topology

```text
builder host (Arch x86_64, systemd-nspawn root)
  nspawn build roots: edge, rc, stable
    makepkg / makechrootpkg per channel      -> camelot-*.pkg.tar.zst
  omarchy-iso-make (forked as camelot-iso)
    --local-source <omarchy fork> <camelot-pkgs>
    -> release/camelot-1.0.0-*.iso + .sha256 + .sig
  iso acceptance harness (QMP + OCR, headless VM)
          |
          | camelot-distro-manifest.json (Ed25519 sealed)
          | Tailscale only, no public WAN
          v
KVM563 VPS hub  (162.35.107.134 / tailnet)
  /srv/camelot/distro/inbox/        <- pushed here
  path unit verifies sha256 + seal, atomically renames
  /srv/camelot/distro/releases/<version>/
  /srv/camelot/distro/current       <- symlink
  hermes-agent.service (native, no container)
          |
          | reads current/manifest.json
          v
installed Camelot-OS node (consumer x86_64)
  Hyprland desktop (Omarchy quattro base)
  systemd slices: camelot-critical / control / data / workers
  bifrost, runic router, hermes agent  -- all native units
  docker: not installed, not required
```

The builder pushes. The hub never reaches back into the builder. Hermes reads a
local path and never fetches from the internet.

## The one primitive that replaces Docker

`systemd-nspawn`.

Upstream `omarchy-pkgs` uses Docker/Podman for two reasons: per-channel base
isolation, and QEMU emulation of foreign architectures. The chosen scope is
x86_64-only, which **deletes the second reason entirely** — there is no foreign
architecture to emulate. The first reason is satisfied by per-channel nspawn
roots under `/var/lib/camelot-build/<channel>-x86_64` using Arch `devtools`
(`mkarchroot`, `arch-nspawn`, `makechrootpkg`), which is the Arch project's own
packaging toolchain and is nspawn-based by construction.

The same primitive covers the ISO build: `mkarchiso` runs inside a privileged
nspawn container on the builder host, which is how archiso is built on hosts that
are not bare Arch.

So one already-installed systemd component, requiring no daemon, no registry, no
image store, and no privileged third-party runtime, replaces Docker in both
places. This is the whole no-Docker argument, and it is why the constraint is
affordable rather than heroic.

`archiso` itself uses `mkarchiso`, not containers. The ISO pipeline is therefore
Docker-free by nature; only the package repo was ever container-dependent.

## Upstream fork map

| Fork | Upstream | Owns | Pinned ref |
| --- | --- | --- | --- |
| `Cyberdad247/omarchy` | `omacom/omarchy` | runtime commands, configs, setup scripts, themes, shell, migrations | `quattro` (already forked) |
| `Cyberdad247/camelot-pkgs` | `omacom/omarchy-pkgs` | `pkgbuilds/camelot-*`, `.omarchy/package.json` metadata, nspawn builder replacing the container builder | new, extracted from upstream release channel |
| `Cyberdad247/camelot-iso` | `omacom/omarchy-iso` | installer, cidata autoinstall, `camelot` release profile | new |

Fork names are load-bearing: every build command, manifest source entry, and
runbook step references them. Renaming later is a cross-repo change.

`CAMELOT_OS` holds the **source of truth** for our profile PKGBUILDs and systemd
units under `05_INFRASTRUCTURE/distro/`. A sync tool copies them into
`camelot-pkgs`. This keeps review and provenance in the main repository and keeps
the fork a build surface rather than a second place to think.

## Versioning and channels

Distro version is `"<upstream omarchy version>+camelot.<patch>"`, for example
`4.0.2+camelot.1`. The upstream base is explicit in the version string, so a
bug report always identifies the Omarchy base it descends from. This is
deliberate: it prevents the most common downstream-distro failure, where the
base is unknowable six months later.

Channels reuse upstream names so `bin/omarchy-release` keeps working:

```
edge -> rc -> stable      forward-only, as upstream
```

Our packages carry the `camelot-` prefix and are pinned to `edge` for development
and promoted through the same train. `camelot-os-profile` and the agent tether
units are the only packages that must exist for a node to be a Camelot node.

## Hardware floor and memory budget

| Tier | Cores | RAM | Disk | Expectation |
| --- | --- | --- | --- | --- |
| Floor | 2 | 4 GB | 40 GB | desktop + agent stack boots, workers throttled |
| Target | 4 | 8 GB | 80 GB | desktop + full agent stack concurrent |

The agent stack is bounded by cgroups v2 slices, reusing the slice layout already
checked in under `apps/camelot-vps-hub/infra/systemd/`:

| Slice | Members | MemoryMax (8 GB) | MemoryMax (4 GB profile) |
| --- | --- | --- | --- |
| `camelot-critical.slice` | Bifrost gateway, Heimdall perimeter | 512 M | 384 M |
| `camelot-control.slice` | runic router, Anya gate | 512 M | 384 M |
| `camelot-data.slice` | SQLite, Graphiti, VFS | 1 G | 512 M |
| `camelot-workers.slice` | agent workers, Hermes | 2 G | 1 G |

Agent ceiling is 4 G on an 8 GB box and 2.25 G on the 4 GB profile, leaving the
remainder to Hyprland and user applications. A `MemoryHigh` soft limit one step
below each `MemoryMax` gives PSI-driven reclaim before the hard cap is hit, so
the desktop degrades smoothly instead of being OOM-killed.

These numbers are a **design ceiling, not a measurement.** Task 5 emits the units
carrying them; Task 7 measures real usage in the acceptance VM and updates them.
Nothing in this spec claims the budget has been observed.

## Seal requirements

The distro manifest is the artifact Hermes trusts, so its seal is specified by
behaviour rather than by field name. This is a direct response to F4, where a
field named `signature` held a forgeable digest.

The seal is valid only if all of the following hold:

1. Signing requires a private key that is not present in the repository.
2. Verification with a **different** public key fails.
3. Flipping any signed byte fails verification.
4. Verification is reproducible from canonical bytes alone.

Requirement 2 is the discriminator. A keyless hash cannot fail under a different
public key because it has no public key, so **a test asserting requirement 2 is
unsatisfiable by the F4 pattern.** Writing that test first is what prevents the
defect from being reproduced a fourth time.

Canonical bytes: JSON, keys sorted, separators `(",", ":")`, UTF-8, with the
`seal` object excluded from the signed bytes. The android edge spec reached the
same rule independently ("never serialize the signature field into the bytes
being verified"), so this is a house convention, not a new invention.

Algorithm `ed25519` via the `cryptography` package, which the repo already depends
on. Public keys are distributed to the hub out of band and pinned at
`/etc/camelot/distro-signing.pub`.

## Hub contract

Manifest, at `/srv/camelot/distro/current/manifest.json`:

```json
{
  "schema_version": 1,
  "release": {
    "version": "4.0.2+camelot.1",
    "channel": "stable",
    "base_upstream": "omacom/omarchy@4.0.2"
  },
  "arch": "x86_64",
  "artifacts": [
    {"name": "camelot-4.0.2+camelot.1.iso", "kind": "iso",
     "sha256": "…", "size_bytes": 0, "path": "releases/4.0.2+camelot.1/"}
  ],
  "packages": [{"name": "camelot-os-profile", "version": "1.0.0-1", "sha256": "…"}],
  "sources": [
    {"repo": "Cyberdad247/omarchy", "ref": "quattro", "commit": "…"},
    {"repo": "Cyberdad247/camelot-iso", "ref": "main", "commit": "…"},
    {"repo": "Cyberdad247/camelot-pkgs", "ref": "main", "commit": "…"}
  ],
  "builder": {"host": "…", "arch": "x86_64", "method": "systemd-nspawn",
              "nsleep_root": "/var/lib/camelot-build", "built_at_utc": "…"},
  "hotpath": {"container_runtime_required": false,
              "python_in_hotpath": false, "node_in_hotpath": false},
  "evidence_class": "confirmed",
  "seal": {"algorithm": "ed25519", "key_id": "…",
           "public_key": "base64…", "signature": "base64…"}
}
```

`hotpath` is a machine-readable assertion that the release satisfies Rule 7. It is
produced by the Task 0 inventory, not asserted by hand. If the inventory finds a
container requirement in the release path, the build fails rather than emitting
`false`.

Ingest on the hub is a systemd path unit watching `inbox/`. It verifies sha256 and
the seal against the pinned key, then atomically renames into `releases/<version>/`
and repoints `current`. A failed verification leaves the artifact in `inbox/` and
writes a rejection receipt. The ingest path contains no container runtime.

Push and ingest are Tailscale-only. The hub's existing UFW policy already denies
incoming by default and permits specific ports in on `tailscale0`; the distro
ingest adds no inbound port because the builder pushes outward over SSH.

## Governance map

| Action | Tier | Mechanism |
| --- | --- | --- |
| Write repos, docs, tests, slices | AUTO/PROMPT | plan approval satisfies this |
| Build packages or ISO on the builder | PROMPT | builder task is operator-initiated |
| De-Dockerize Hermes on the hub | HUMAN_GATE | mutates VPS unit state |
| Publish a release to the hub | HUMAN_GATE | `CAMELOT_DASHBOARD_OPERATOR_TOKEN` required |
| Publish the ISO publicly | HUMAN_GATE | open question, not defaulted |

`HUMAN_GATE` handling mirrors `control_plane/core/soul_oversight.py`, which
already suspends rather than proceeding when the operator token is absent. The
distro release gate reuses that precedent instead of inventing a second one.

- **Anya** owns entry and exit: triage of the release intent, and `validate_output`
  before a manifest leaves the system.
- **Merlin** owns the adversarial ruling on the two decisions with real downside:
  the builder isolation model and the memory ceiling. Both are CRITICAL-lane and
  route through `ColMAD().crucible`, which `anya_gate._stage_colmad` already
  invokes for CRITICAL or HUMAN_GATE intents.
- **Sir Codex** owns kinetic implementation and the TDD loop.
- **Sir Sentinel / Heimdall** own the perimeter: no public listener, tailnet-only
  transport, pinned public key.

## Open questions

1. **Builder host placement.** Bare-metal Arch node on the tailnet, a VM, or a
   privileged nspawn root on the Ubuntu hub. Nothing in the tree currently answers
   this. It is Task 3 and it gates Tasks 4-7.
2. **Is the ISO published publicly?** A public download makes the distro real and
   makes every future release a public commitment. Not defaulted here.
3. **F7 routing.** Add `sir_link` to the root roster, or repoint the distro lane at
   `SIR_KAY`. Operator's call.
4. **Desktop rebrand depth.** Theme-layer only, or a renamed shell. This spec
   assumes theme-layer only and says so explicitly so the assumption is visible.
5. **F4 remediation.** `qr_bridge.py` is out of scope for this plan but is a live
   forgeable-verification defect in a cartridge. It should get its own task.

## Evidence classes

Status of every claim in this document, per the root `AGENTS.md` scheme.

| Claim | Class |
| --- | --- |
| Findings F1-F7 | confirmed, each with a file path above |
| `systemd-nspawn` replaces Docker in both build paths | planned |
| x86_64-only removes the foreign-arch container need | planned |
| Memory ceiling table | aspirational until Task 7 measures it |
| Unattended cidata install reaches a logged-in desktop | planned |
| Hermes reads a sealed manifest from the hub | planned |
| Anything already built, shipped, or published | none claimed |
