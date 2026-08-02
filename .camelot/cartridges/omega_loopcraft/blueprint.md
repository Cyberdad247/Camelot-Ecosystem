# Blueprint — omega_loopcraft

## Architecture & Data Flow
The Omega Loopcraft cartridge runs as a self-contained, air-gapped environment within Camelot-OS. No external ports or public HTTP listeners are spawned. All execution pathways are bounded by standard input/output streaming (`stdio`) and secure client-side database connections.

```
+-------------------------------------------------------------------+
|                       CAMELOT-OS SANDBOX                          |
|                                                                   |
|  +-------------------+              +-------------------------+   |
|  |   Next.js UI      |              |   FastAPI MCP Engine    |   |
|  |   (Static HTML)   |              |   (Local stdio service) |   |
|  +---------+---------+              +------------+------------+   |
|            |                                     ^                |
|            | Web-IPC (stdio JSON-RPC bridge)     |                |
|            +-------------------------------------+                |
|            |                                                      |
|            v                                                      |
|  +---------+---------+                                            |
|  |    Supabase DB    |                                            |
|  | (Direct Client Srv|                                            |
|  +-------------------+                                            |
+-------------------------------------------------------------------+
```

1. **Next.js UI (Static HTML)**: The frontend compiles to client-only static assets. Communication with the backend occurs entirely via JSON-RPC bridged through `stdio` or Web-IPC.
2. **FastAPI MCP Engine (stdio)**: The backend is spawned as a sub-process of the Camelot-OS execution frame. It listens strictly to `stdio` commands via the Model Context Protocol (MCP) and executes tasks locally.
3. **Supabase Integration**: Data persistence is achieved via direct client-side integration to Supabase using standard Row-Level Security (RLS) policies.

## Aesthetic Laws (The Obsidian Mandate)
All user interface panels, status dashboards, and interactive modules within the cartridge shell must strictly bind to the Obsidian Mandate color palette:

```css
:root {
  --background-obsidian: #0B0B0F; /* Deep Charcoal Background */
  --accent-gold:         #FFD700; /* Liquid Gold Primary Highlights */
  --highlight-purple:    #7B2CBF; /* Royal Neon Purple Secondary Accents */
  
  --text-primary:        #FFFFFF;
  --text-muted:          #8E9296;
}
```
