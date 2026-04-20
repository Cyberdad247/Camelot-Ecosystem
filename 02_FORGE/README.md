# 02_FORGE: The Kinetic Workshop (L2)

## ⚒️ OVERVIEW

The **Forge Realm** contains the executable tools, applications, and binaries of Camelot OS. It is the "Hands" (Lukas) and "Builders" (Kai).

## 📂 STRUCTURE

- `apps/`: User-facing applications (Anya Lyte, Dashboards).
- `packages/`: Shared libraries (Pocket Squire, Anya Domain).
- `kinetic/`: High-performance binaries (RustDesk, Cribo, Rotel).
- `_templates/`: scaffolding for new projects.

## 🚀 AVAILABLE TOOLS

| Tool              | Path                      | Purpose                      |
| :---------------- | :------------------------ | :--------------------------- |
| **RustDesk**      | `kinetic/rustdesk-server` | Remote Access Infrastructure |
| **Anya Lyte**     | `apps/anya-lyte`          | Primary User Interface       |
| **Pocket Squire** | `packages/pocket-squire`  | CLI Utility Suite            |

## 🏗️ BUILD COMMANDS

```bash
# Build All
pnpm install
pnpm build

# Build Specific App
pnpm --filter anya-lyte build
```
