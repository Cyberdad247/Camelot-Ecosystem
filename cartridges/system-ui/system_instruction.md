# SYSTEM INSTRUCTION: Sovereign System UI Cartridge
@ctx|camelot-os.dev/ukg/v10001/cartridges/system_ui id|Ω_CARTRIDGE_SYSTEM_UI_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `system-ui`
- **Sovereign Knights**: `SIR_STITCH`, `LADY_GUINEVERE`, `SIR_BORIS`
- **Primary Substrates**: Vite, React 18, Tailwind CSS, WebGPU Three.js Canvas, Zustand
- **Supported Node Profiles**: `experience`, `cockpit`, `pwa`

## 2. Authorized Entrypoints
- `dev`: Start high-frequency local development server.
- `build`: Compile production assets with Biome validation and Luxora Gold (`#D4AF37`) theming.
- `preview`: Run isolated local bundle preview.

## 3. Capability Boundary Constraints
- **Granted**: `vfs.read`, `ui.render`.
- **Strictly Denied**: `secret.export`, `direct_main_branch_write`.
- **Design Law**: Strict adherence to Camelot Rule 1: Tailwind CSS + Luxora Gold highlights with zero unnarrowed `as any` masks.
