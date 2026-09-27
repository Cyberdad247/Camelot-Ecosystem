import { VfsFile } from '../types';

// Raw file imports via Vite
const agentFiles = import.meta.glob(['../../.agent/*.md', '/.agent/*.md'], { eager: true, query: '?raw', import: 'default' });
const rootDocFiles = import.meta.glob(['../*.md', '/*.md'], { eager: true, query: '?raw', import: 'default' });
const archDocFiles = import.meta.glob(['../docs/**/*.md', '/docs/**/*.md'], { eager: true, query: '?raw', import: 'default' });
const contractSchemaFiles = import.meta.glob(['../packages/contracts/*.json', '/packages/contracts/*.json'], { eager: true, query: '?raw', import: 'default' });
const receiptFiles = import.meta.glob(['../harness/golden-receipts/*.json', '/harness/golden-receipts/*.json'], { eager: true, query: '?raw', import: 'default' });

export function loadAllVfsFiles(): VfsFile[] {
  const result: VfsFile[] = [];
  const seenPaths = new Set<string>();

  // 1. Sovereign Agent VFS Files
  Object.entries(agentFiles).forEach(([path, content]) => {
    const filename = path.split('/').pop() || path;
    const cleanPath = `/.agent/${filename}`;
    if (seenPaths.has(cleanPath)) return;
    seenPaths.add(cleanPath);

    let domain = 'Sovereign VFS';
    if (filename.includes('Preflight') || filename.includes('protocols')) domain = 'Governance_&_Integrity';
    else if (filename.includes('task')) domain = 'DAG_Kinetic_Swarm';
    else if (filename.includes('verification')) domain = 'Formal_Z3_Verification';
    else if (filename.includes('agent') || filename.includes('knight')) domain = 'Swarm_Definitions';
    else if (filename.includes('skills')) domain = 'Execution_Capabilities';
    else if (filename.includes('harness') || filename.includes('mcp')) domain = 'Kinetic_Boundaries';
    else if (filename.includes('Merlin') || filename.includes('Anya')) domain = 'Cognitive_Kernel';
    else if (filename.includes('worldtree')) domain = 'Cloudbrain_Memory';
    else if (filename.includes('Artifacts')) domain = 'Ledger_Receipts';
    else if (filename.includes('workflows')) domain = 'Execution_Loops';
    else if (filename.includes('symbollect')) domain = 'Runic_Lexicon';
    else if (filename.includes('camelot-os max')) domain = 'OS_Architecture';
    else if (filename.includes('digitalfactory')) domain = 'Agentic_Operations';
    else if (filename.includes('Inspira')) domain = 'UI_UX_Design';
    else if (filename.includes('HiveIDE')) domain = 'Development_Environment';
    else if (filename.includes('Blueprint-os')) domain = 'Master_Ignition';
    else if (filename.includes('merlinss')) domain = 'Saga_Execution';
    else if (filename.includes('kickbox')) domain = 'Enterprise_Cartridge';

    let description = `Sovereign VFS Node: ${filename.replace('.md', '')}`;
    if (filename === 'task.md') description = 'VFS NODE 03: DAG Multi-Agent Kinetic Swarm Orchestration Lattice [SIR_CODEX]';
    else if (filename === 'verification.md') description = 'VFS NODE 04: Z3 & SymPy Formal Neurosymbolic Verification Engine [SIR_BORIS]';

    result.push({
      path: cleanPath,
      name: filename,
      domain,
      category: 'vfs-core',
      content: content as string,
      isMarkdown: true,
      description
    });
  });

  // 2. Core Architecture Documentation
  Object.entries({ ...rootDocFiles, ...archDocFiles }).forEach(([path, content]) => {
    const filename = path.split('/').pop() || path;
    const cleanPath = path.startsWith('/') ? path : `/${path.replace(/^(\.\.\/)+/, '')}`;
    if (cleanPath.includes('.agent/') || seenPaths.has(cleanPath)) return;
    seenPaths.add(cleanPath);

    result.push({
      path: cleanPath,
      name: filename,
      domain: 'Architecture_&_Specs',
      category: 'docs',
      content: content as string,
      isMarkdown: true,
      description: `System Document: ${filename}`
    });
  });

  // 3. Contract Schemas
  Object.entries(contractSchemaFiles).forEach(([path, content]) => {
    const filename = path.split('/').pop() || path;
    const cleanPath = `/packages/contracts/${filename}`;
    if (seenPaths.has(cleanPath)) return;
    seenPaths.add(cleanPath);

    let parsed = {};
    try {
      parsed = JSON.parse(content as string);
    } catch {
      // ignore
    }

    result.push({
      path: cleanPath,
      name: filename,
      domain: 'Contract_Schemas',
      category: 'contracts',
      content: content as string,
      isMarkdown: false,
      parsed,
      description: (parsed as any).title || `JSON Schema Contract: ${filename}`
    });
  });

  // 4. Golden Receipts
  Object.entries(receiptFiles).forEach(([path, content]) => {
    const filename = path.split('/').pop() || path;
    const cleanPath = `/harness/golden-receipts/${filename}`;
    if (seenPaths.has(cleanPath)) return;
    seenPaths.add(cleanPath);

    let parsed = {};
    try {
      parsed = JSON.parse(content as string);
    } catch {
      // ignore
    }

    result.push({
      path: cleanPath,
      name: filename,
      domain: 'Golden_Receipts',
      category: 'golden-receipts',
      content: content as string,
      isMarkdown: false,
      parsed,
      description: `Cryptographic Golden Anchor Receipt`
    });
  });

  // 5. HTMX Command Center Dispatched Files
  const htmxFiles: Array<{ path: string; name: string; content: string; isMarkdown: boolean; description: string }> = [
    {
      path: '/opt/camelot/htmx-center/main.go',
      name: 'main.go',
      content: `package main

import (
    "encoding/json"
    "fmt"
    "html/template"
    "log"
    "math/rand"
    "net/http"
    "sync"
    "time"
)

type SystemStatus struct {
    Status string  \`json:"status"\`
    CPU    float64 \`json:"cpu"\`
    Memory float64 \`json:"memory"\`
}

type Task struct {
    ID     string \`json:"id"\`
    Title  string \`json:"title"\`
    Status string \`json:"status"\`
    Risk   string \`json:"risk"\`
}

type Receipt struct {
    ID     string \`json:"id"\`
    Action string \`json:"action"\`
    Time   string \`json:"time"\`
    Hash   string \`json:"hash"\`
}

var (
    status = SystemStatus{Status: "CONVERGED", CPU: 42.5, Memory: 3.2}
    tasks  = []Task{
        {ID: "task_001", Title: "Draft response to Jane", Status: "approved", Risk: "R4"},
        {ID: "task_002", Title: "Create campaign plan", Status: "running", Risk: "R2"},
        {ID: "task_003", Title: "Review invoice #4092", Status: "pending", Risk: "R3"},
    }
    receipts = []Receipt{
        {ID: "0x9f4a", Action: "email.draft.created", Time: "10:23:11", Hash: "sha256:4f9d...e201"},
        {ID: "0x7c21", Action: "approval.granted", Time: "10:24:32", Hash: "sha256:1a8c...90b4"},
    }
    mu sync.Mutex
)

var indexTmpl = template.Must(template.ParseFiles("static/index.html"))

func main() {
    http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        indexTmpl.Execute(w, nil)
    })
    http.HandleFunc("/fragments/status", statusFragment)
    http.HandleFunc("/fragments/tasks", tasksFragment)
    http.HandleFunc("/fragments/receipts", receiptsFragment)
    http.HandleFunc("/stream", sseHandler)

    log.Println("⚜️ Camelot HTMX Center listening on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}`,
      isMarkdown: false,
      description: 'Native Go Standard Library Server + SSE Streamer'
    },
    {
      path: '/opt/camelot/htmx-center/static/index.html',
      name: 'index.html',
      content: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camelot-OS Command Center (HTMX + Go)</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="/static/js/htmx.min.js" defer></script>
</head>
<body>
    <header class="header">
        <div class="brand">
            <h1>⚜️ Camelot-OS</h1>
            <p>Omega Apex Singularity — Native Go + HTMX + SSE Command Deck</p>
        </div>
        <div class="anchor-tag">
            <span>EDGE: Cleveland, OH</span>
            <span>MEM_CAP: 256MB</span>
        </div>
    </header>

    <main class="grid">
        <div class="cell" hx-get="/fragments/status" hx-trigger="load, every 5s" hx-swap="innerHTML">
            <div id="status-panel" class="panel">
                <h2>Throne Room</h2>
                <p>System: <span class="status CONVERGED">CONVERGED</span></p>
                <p>CPU: 42.5%</p>
                <p>Memory: 3.2 GB</p>
            </div>
        </div>
        <div class="cell" hx-get="/fragments/tasks" hx-trigger="load, every 5s" hx-swap="innerHTML">
            <div id="tasks-panel" class="panel">
                <h2>Round Table</h2>
                <ul>
                    <li data-task-id="task_001">Draft response to Jane - <span class="risk">R4</span> [approved]</li>
                    <li data-task-id="task_002">Create campaign plan - <span class="risk">R2</span> [running]</li>
                    <li data-task-id="task_003">Review invoice - <span class="risk">R3</span> [pending]</li>
                </ul>
            </div>
        </div>
        <div class="cell" hx-get="/fragments/receipts" hx-trigger="load, every 5s" hx-swap="innerHTML">
            <div id="receipts-panel" class="panel">
                <h2>Ledger</h2>
                <table>
                    <tr><th>ID</th><th>Action</th><th>Time</th></tr>
                    <tr><td>0x9f4a</td><td>email.draft.created</td><td>10:23:11</td></tr>
                    <tr><td>0x7c21</td><td>approval.granted</td><td>10:24:32</td></tr>
                </table>
            </div>
        </div>
    </main>
</body>
</html>`,
      isMarkdown: false,
      description: 'Native HTMX Single-Page Application Shell'
    },
    {
      path: '/opt/camelot/htmx-center/static/css/style.css',
      name: 'style.css',
      content: `:root {
  --obsidian: #0A0710;
  --luxora-gold: #E4B24A;
  --royal-purple: #8E4EC6;
  --vellum: #F1EFF4;
  --garnet: #DE4258;
}

body {
  background: var(--obsidian);
  color: var(--vellum);
  font-family: 'Courier New', monospace;
  margin: 0;
  padding: 24px;
}

.header {
  border-bottom: 2px solid var(--luxora-gold);
  padding-bottom: 12px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.panel {
  border: 1px solid var(--royal-purple);
  background: #150c26;
  padding: 20px;
  border-radius: 8px;
}`,
      isMarkdown: false,
      description: 'Obsidian / Luxora Gold / Royal Purple CSS Sovereign Theme'
    },
    {
      path: '/opt/camelot/htmx-center/deploy/camelot-htmx.service',
      name: 'camelot-htmx.service',
      content: `[Unit]
Description=Camelot HTMX Command Center
After=network.target

[Service]
Type=simple
User=camelot-svc
WorkingDirectory=/opt/camelot/htmx-center
ExecStart=/usr/local/bin/camelot-htmx-center
Restart=always
MemoryMax=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target`,
      isMarkdown: false,
      description: 'Systemd Service Unit Configuration (MemoryMax=256M)'
    },
    {
      path: '/opt/camelot/htmx-center/deploy/install.sh',
      name: 'install.sh',
      content: `#!/bin/bash
set -euo pipefail

echo "⚜️ Forging HTMX Command Center..."
cd /opt/camelot/htmx-center
go build -o /usr/local/bin/camelot-htmx-center main.go
sudo cp deploy/camelot-htmx.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now camelot-htmx.service
curl -s http://localhost:8080/ | grep "Camelot-OS"
echo "✅ HTMX Center is live on port 8080."`,
      isMarkdown: false,
      description: 'Zero-touch Native Go Daemon Installer'
    },
    {
      path: '/opt/camelot/htmx-center/README.md',
      name: 'README.md',
      content: `# ⚜️ Camelot-OS HTMX Command Center

A pure **Go + HTMX + SSE** single-page application dashboard running 100% Docker-free as a native binary.

## Architecture
- **Backend:** Native Go standard library (\`net/http\`, \`html/template\`, \`sync\`)
- **Frontend:** HTMX with SSE streaming + Obsidian/Gold/Purple CSS theme
- **Footprint:** <= 256MB memory cap, low CPU overhead
- **Deployment:** Systemd service on \`/opt/camelot/htmx-center\`

## Commands
\`\`\`bash
# Build & run locally
go run main.go

# Install systemd service
sudo ./deploy/install.sh
\`\`\`

⚜️_SOVEREIGN_TRUTH`,
      isMarkdown: true,
      description: 'HTMX Command Center Sovereign Spec'
    }
  ];

  htmxFiles.forEach((file) => {
    if (seenPaths.has(file.path)) return;
    seenPaths.add(file.path);
    result.push({
      path: file.path,
      name: file.name,
      domain: 'HTMX_Command_Center',
      category: 'htmx-center',
      content: file.content,
      isMarkdown: file.isMarkdown,
      description: file.description
    });
  });

  // 6. A2UI Cartridge Hot-Swap Specifications & νKG Mantra Crystal
  const cartridgeFile = {
    path: '/etc/camelot/cartridges/A2UI_CARTRIDGE_V10000.54.json',
    name: 'A2UI_CARTRIDGE_V10000.54.json',
    content: JSON.stringify({
      "$schema": "https://camelot-os.invisioned.io/schemas/cartridge.v10000.54.json",
      "crystalId": "Ωv10000.54::NDR+S(GoT)",
      "themeIdentified": "Autonomous Agentic UI/UX Operating System",
      "mantraCrystal": "Ωv10000.54::NDR+S(GoT)⊢Z3(SAT)::Ouroboros(1.58b)→O(1)mem::QFT(R,Q,P)::A2UI(60:30:10|8pt)→Δt<400ms",
      "algorithmicVectors": {
        "vector1": {
          "name": "Ouroboros 1.58-bit State Space Model",
          "complexity": "O(1) memory recurrence",
          "quantization": "Ternary weights {-1, 0, +1}",
          "memoryClampMb": 250
        },
        "vector2": {
          "name": "Z3 Kahn's Topological Validator & SAT Gate",
          "invariant": "Acyclic DAG ⊢ 4 Constitutional Pillars",
          "pillars": ["Sovereignty", "Transparency", "Non-Malice", "Scarcity"]
        },
        "vector3": {
          "name": "Triple-QFT & Semantic Anchor Compression (SAC)",
          "pipeline": "Rescale -> Quench -> Perturb",
          "compressionFactor": "4.82x",
          "mountLatency": "Δt < 400ms"
        }
      },
      "leadKnights": ["MERLIN_Ω", "SIR_GIDEON", "SIR_HYDRON", "SIR_VISAGE", "ANYA_Ω"],
      "seal": "⚜️_SOVEREIGN_TRUTH"
    }, null, 2),
    isMarkdown: false,
    description: 'A2UI Hot-Swappable Cartridge νKG Specification'
  };

  if (!seenPaths.has(cartridgeFile.path)) {
    seenPaths.add(cartridgeFile.path);
    result.push({
      path: cartridgeFile.path,
      name: cartridgeFile.name,
      domain: 'Autonomous_Cartridges',
      category: 'vfs-core',
      content: cartridgeFile.content,
      isMarkdown: false,
      description: cartridgeFile.description
    });
  }

  // 7. VFS NODE 03 & 04 Shadow Forge Worktree Nodes
  const shadowNodes = [
    {
      path: '/.shadow_forge_worktree/task.md',
      name: 'task.md',
      domain: 'DAG_Kinetic_Swarm',
      category: 'vfs-core' as const,
      content: `# 💾 VFS NODE 03: \`task.md\` (DAG_BIO_KINETIC_SWARM)
**[AUTHOR]: SIR_CODEX (The Kinetic Hand)**

\`\`\`text
@dag|MULTI_AGENT_ORCHESTRATION_LATTICE
@mode|PARALLEL_FAN_OUT

[EXECUTION_NODES]
node_A|SIR_HELIO|INGEST_AND_PLAN|TRIPLE_QFT_DISTILLATION
node_B|SIR_CODEX|AST_SCAFFOLDING|GENERATE_CRUD_LOGIC_IN_SUB_30S [1]
node_C|SIR_BORIS|WORKTREE_SHADOW_SPAWN|COMPILE_VIABLE_PATCH_DIFF [2]
node_D|SIR_GIDEON|TEST_DRIVEN_DEV|MAP_FAILING_ASSERT_BLOCKS [2]

[LIFECYCLE_TOPOLOGY]
route|NDR+S_GENESIS_LOOP|Planning_to_Build
flow|User_Intent->Helio->Boris->Codex->Sentinel->Merge [3]
sandbox|ISOLATE_INSIDE_SHADOW_FORGE_WORKTREE|./.shadow_forge_worktree/ [1]
\`\`\``,
      isMarkdown: true,
      description: 'VFS NODE 03: DAG Multi-Agent Kinetic Swarm Orchestration Lattice [SIR_CODEX]'
    },
    {
      path: '/.shadow_forge_worktree/verification.md',
      name: 'verification.md',
      domain: 'Formal_Z3_Verification',
      category: 'vfs-core' as const,
      content: `# 💾 VFS NODE 04: \`verification.md\` (Z3_SATISFIABILITY)
**[AUTHOR]: SIR_BORIS (The Iron Anvil)**

\`\`\`text
@proof|Z3_SYMPY_NEUROSYMBOLIC_BRIDGE
@engine|FORMAL_VERIFICATION

[MATHEMATICAL_GUARANTEES]
V1|PROVABLE_GUARANTEE|Move security from reactive pattern-matching to provable mathematical guarantee [4].
V2|PDG_VERIFICATION|Mathematical Proofing of Program Dependency Graphs
V3|ERROR_THRESHOLD|Max_Error < 0.7%

[QUALITY_GATE_TELEMETRY]
metric_1|LLM_AS_A_JUDGE|Independent verification score required for every parallel patch [3].
metric_2|IOSM_ALIGNMENT|Require overall IOSM Alignment Index >= 0.85 before merging back into root [3].
metric_3|LCP_BOUNDARY|Largest Contentful Paint boundary limits check out under 1.1s over WebGL components [2].
\`\`\``,
      isMarkdown: true,
      description: 'VFS NODE 04: Z3 & SymPy Formal Neurosymbolic Verification Engine [SIR_BORIS]'
    }
  ];

  shadowNodes.forEach((node) => {
    if (!seenPaths.has(node.path)) {
      seenPaths.add(node.path);
      result.push(node);
    }
  });

  return result;
}
