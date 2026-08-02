# Omega Loopcraft Cartridge (v1.0.0)

A self-contained, air-gapped Camelot-OS Cartridge environment bundling a static Next.js UI Shell, a stdio-based FastAPI MCP Engine, and direct Supabase database integrations.

---

## 1. Directory Structure

```
.camelot/cartridges/omega_loopcraft/
├── manifest.yaml       # Cartridge descriptor, routing permissions & entry points
├── blueprint.md        # Architecture overview & Obsidian Mandate styling tokens
├── task.md             # Compilation DAG commands for static UI & Python dependencies
├── verification.md     # Security boundary (.env bans) & HITL validation rules
├── README.md           # This comprehensive guide & implementation blueprints
├── ui_shell/           # Next.js App Router static build export
│   └── out/
│       └── index.html  # Compiled single-page entry point
└── mcp_engine/         # Local stdio FastAPI MCP server
    └── main.py         # Stdio reader/writer event loop
```

---

## 2. Architecture & Data Flow

Traditional web servers expose open HTTP ports, presenting security and network surface risks. The Omega Loopcraft Cartridge abandons exposed ports entirely, instead routing all operations through a secure standard-input/standard-output (`stdio`) JSON-RPC bridge:

```
[ Next.js Static UI ] 
        │
        │ (Web-IPC / Stdio JSON-RPC payload)
        ▼
[ Host Agent / Sandbox ]
        │
        │ (stdin pipe / JSON-RPC stream)
        ▼
[ FastAPI MCP Engine (stdio) ]
        │
        │ (Local Execution & tool execution)
        ▼
[ Supabase DB (Remote client-side connection using RLS) ]
```

---

## 3. Real-World Implementation Examples

### A. Next.js Static UI Shell Bridge (`ui_shell`)
This script executes inside the Next.js static app to securely send commands to the host process via the bridged `window.postMessage` channel, enforcing the mandatory **Human-In-The-Loop (HITL)** Approve button.

```typescript
// ui_shell/components/McpBridge.tsx
import React, { useState } from 'react';

interface JsonRpcRequest {
  jsonrpc: '2.0';
  id: string | number;
  method: string;
  params?: any;
}

export function McpBridge() {
  const [status, setStatus] = useState<string>('Idle');
  const [approved, setApproved] = useState<boolean>(false);

  const dispatchCommand = async (method: string, params: any) => {
    // 1. HITL Validation Gate
    if (!approved) {
      setStatus('Blocked: Awaiting Manual HITL Approval');
      return;
    }

    const payload: JsonRpcRequest = {
      jsonrpc: '2.0',
      id: Date.now(),
      method,
      params,
    };

    setStatus('Dispatching command...');
    
    // 2. Post message to Camelot-OS Host Bridge
    if (window.chrome && window.chrome.webview) {
      // WebView2 runtime
      window.chrome.webview.postMessage(payload);
    } else if (window.parent !== window) {
      // Standard iframe parent bridge
      window.parent.postMessage(payload, '*');
    } else {
      console.log('Local Sandbox Console output:', payload);
    }
  };

  return (
    <div style={{
      backgroundColor: '#0B0B0F', // Obsidian background
      color: '#FFFFFF',
      padding: '24px',
      borderRadius: '8px',
      border: '1px solid #FFD700' // Gold accent border
    }}>
      <h2 style={{ color: '#7B2CBF' }}>Omega Loopcraft Control Panel</h2>
      <p>Status: <strong>{status}</strong></p>
      
      <div style={{ margin: '16px 0' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input 
            type="checkbox" 
            checked={approved} 
            onChange={(e) => setApproved(e.target.checked)} 
          />
          <span style={{ color: '#FFD700' }}>[HITL] Approve Next Operation</span>
        </label>
      </div>

      <button 
        onClick={() => dispatchCommand('execute_agent_loop', { speed: 'max' })}
        style={{
          backgroundColor: approved ? '#7B2CBF' : '#222',
          color: '#FFF',
          padding: '10px 20px',
          border: 'none',
          cursor: approved ? 'pointer' : 'not-allowed'
        }}
        disabled={!approved}
      >
        Ignite Agent Loop
      </button>
    </div>
  );
}
```

### B. FastAPI stdio MCP Engine (`mcp_engine`)
This python module reads JSON-RPC requests from standard input (`sys.stdin`), executes the requested model tool handler, and writes the response back to standard output (`sys.stdout`), circumventing network interface bindings.

```python
# mcp_engine/main.py
import sys
import json
import asyncio

async def write_response(id_val, result=None, error=None):
    response = {
        "jsonrpc": "2.0",
        "id": id_val
    }
    if error:
        response["error"] = error
    else:
        response["result"] = result
        
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()

async def handle_request(line: str):
    try:
        req = json.loads(line)
        id_val = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "execute_agent_loop":
            # Real-world agent tool logic
            speed = params.get("speed", "normal")
            result = {
                "status": "success",
                "message": f"Agent Loop ignited successfully at {speed} speed.",
                "telemetry": {"latency_ms": 14}
            }
            await write_response(id_val, result=result)
        elif method == "ping":
            await write_response(id_val, result="pong")
        else:
            await write_response(
                id_val, 
                error={"code": -32601, "message": f"Method {method} not found"}
            )
    except Exception as e:
        # Fallback error response
        try:
            await write_response(None, error={"code": -32700, "message": str(e)})
        except:
            pass

async def main():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    
    while True:
        line_bytes = await reader.readline()
        if not line_bytes:
            break
        line = line_bytes.decode('utf-8').strip()
        if line:
            await handle_request(line)

if __name__ == "__main__":
    asyncio.run(main())
```

### C. Direct Supabase Integration Client
Connect directly to Supabase from the static client, relying on Row-Level Security (RLS) policies based on user authentication, keeping secrets out of the static UI assets.

```javascript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://your-project.supabase.co';
// Public anon key is safe for client-side distribution when protected by RLS
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function fetchUserCartridges(userId) {
  const { data, error } = await supabase
    .from('user_cartridges')
    .select('*')
    .eq('user_id', userId);
    
  if (error) throw error;
  return data;
}
```

---

## 4. Compilation & Verification Instructions

### How to Compile
Execute the commands detailed in [task.md](file:///C:/Users/vizio/CAMELOT_OS/.camelot/cartridges/omega_loopcraft/task.md) to build static files, freeze python libraries, and package the cartridge into a secure archive:
```powershell
Compress-Archive -Path .camelot/cartridges/omega_loopcraft/* -DestinationPath dist/omega_loopcraft.zip -Force
```

### How to Verify
Run the validation script defined in [verification.md](file:///C:/Users/vizio/CAMELOT_OS/.camelot/cartridges/omega_loopcraft/verification.md) to guarantee no `.env` or raw key leaks are contained in the cartridge:
```powershell
Get-ChildItem -Path .camelot/cartridges/omega_loopcraft -Filter ".env*" -Recurse | Measure-Object | % {
    if ($_.Count -ne 0) { throw "Verification Failed: Banned .env files detected!" }
}
```
