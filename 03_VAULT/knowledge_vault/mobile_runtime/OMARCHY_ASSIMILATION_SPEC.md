# CAMELOT-OS Knowledge Vault // Sovereign Mobile Runtime Assimilation
## Assimilation Spec: Omarchy Desktop & Omarchy-Android (ARM64 Rootless)
**Artifact ID:** `UKG-SPEC-OMARCHY-ASSIMILATION-V1`  
**Classification:** `ARCHITECTURAL_CRYSTAL // SOVEREIGN_MOBILE_COMPUTE`  
**Target Device:** `vashawns-s26-ultra` (Samsung Galaxy S26 Ultra / Snapdragon 8 Elite / Adreno 840)  
**Tailscale Coordinate:** `100.106.246.126`  
**Canonical Sources:**  
- `https://github.com/Cyberdad247/omarchy` (quattro branch)
- `https://github.com/Cyberdad247/omarchy-android` (main branch)

---

### 1. Executive Summary

This specification codifies the formal assimilation of the **Omarchy Desktop** agent-native Linux distribution and the **Omarchy-Android** rootless ARM64 port into Camelot-OS. The objective is to elevate the **Excalibur Mobile Sentinel** (`vashawns-s26-ultra`) from a remote screen mirroring client (via scrcpy) into an autonomous, sovereign mobile edge node executing native ARM64 workloads under hardware-accelerated Vulkan/Turnip rendering at 120 Hz.

---

### 2. Upstream Architecture & Invariants

#### 2.1 The Omarchy Desktop Invariants
* **Agent-First Native Integration:** Symlinks skills across Claude Code, OpenAI Codex, Antigravity/Gemini, and Nous Hermes.
* **Crash Telemetry Loop:** Hooks `systemd-coredump` into `omarchy agent crash <pid>` triggering the `diagnose-crash` agent skill for instantaneous root-cause analysis.
* **Agent Panel Telemetry:** Live top bar polling of token balances, session limits, and provider rate limits.

#### 2.2 The Omarchy-Android Graphics & Container Stack
```text
Android Display (Termux:X11 Nightly)
       ^
       | (Wayland presentation)
Patched Weston (Nested Wayland Parent with accurate XRandR refresh timing)
       ^
       | (DRM-less Wayland socket)
Patched Hyprland & Aquamarine (Buffer pipeline handling Android ashmem/dmabuf)
       ^
       | (Turnip Vulkan driver -> /dev/kgsl-3d0)
Qualcomm Adreno 840 GPU (Snapdragon 8 Elite Direct Hardware Acceleration)
```

1. **Rootless PRoot Isolation:** Native ARM64 userspace inside Termux without requiring root or unlocked bootloaders.
2. **Direct KGSL/Turnip Acceleration:** Direct ioctl communication with `/dev/kgsl-3d0` avoiding DRM subsystem emulation.
3. **555-Package Closure:** Digest-pinned Arch Linux ARM rootfs with locked dependencies (`manifest/*.lock`).

---

### 3. Camelot-OS System Governance Laws

1. **Global Law 03 (RAM Scarcity & Node Ceiling):**
   * The mobile guest container is bounded to $\le 3.5\text{ GB}$ (3,584 MB) RAM.
   * This strictly honors the **4 GB Node Ceiling** and prevents Android's Low Memory Killer (LMK) from reaping the Termux parent process.
2. **Global Law 04 (Warp Gate Agentic Ingress):**
   * The Excalibur mobile agent must possess an authentic `AlexandriaKeypassVault` Forever Keypass (`KP-EXCALIBUR_MOBILE-*`).
   * Unauthenticated agent calls from the phone are rejected at the Bifrost boundary with `AgenticIngressDeniedError`.
3. **Security Perimeter (Chromium Sandbox):**
   * PRoot cannot provide unprivileged user namespaces (`CLONE_NEWUSER`), necessitating `--no-sandbox` for Chromium.
   * All browser workloads inside the guest container are air-gapped from private keys and Camelot secrets.

---

### 4. Patch Series Ledger

* `patches/aquamarine/0001-wayland-carry-proven-Android-KGSL-buffer-pipeline.patch`: Eliminates DRM node requirement, routing buffer allocation directly through KGSL ashmem buffers.
* `patches/hyprland/0001-render-carry-proven-Android-KGSL-presentation-path.patch`: Patches Aquamarine render loop for non-blocking XRandR sync under Termux:X11.
* `patches/weston/0001-backend-x11-carry-proven-Android-nested-fixes.patch`: Hardens Weston X11 backend against Android input focus drops.
* `runtime/host/src/process-guard.c`: Replaces systemd supervisor with lightweight C watchdog to monitor Weston, Hyprland, and D-Bus processes under PRoot.

Sealed by MERLIN_Ω, ANYA_Ω, and SIR_HELIOS on 2026-10-04.
