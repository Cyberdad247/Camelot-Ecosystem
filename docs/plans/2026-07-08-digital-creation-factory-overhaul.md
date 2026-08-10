# Digital Creation Factory & Voice Router Overhaul Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Unify the multi-persona voice routing service, Kickbox audio controls, OpenPersona visualizers, and the Digital Creation Factory dashboard into a multi-tabular PWA hub steered by edge node S26.

**Architecture:** 
We will construct a layered React client using local state management to route voice packet payloads to the Chatterbox and Multivoice router services on the Bifrost Bridge. The interface will segment operational controls into a Sovereign PWA control deck (monitoring bridge node endpoints) and a Digital Creation Factory panel (auditing agent workspaces and Kahn's DAG files). Strict memory disposal is enforced via WebGL context release on unmount to satisfy the 150MB scarcity envelope.

**Tech Stack:** React 18, Vite PWA, Tailwind CSS, Three.js/R3F, HTML5 Web Audio API.

---

### Task 1: Multivoice & Chatterbox Proxy Integration

**Files:**
*   Modify: `cartridges/system-ui/vite.config.ts`
*   Test: `cartridges/system-ui/vite-proxy.test.ts`

**Step 1: Write the failing test**

Create the file `cartridges/system-ui/vite-proxy.test.ts` and add:
```typescript
import { describe, it, expect } from 'vitest';
import config from './vite.config';

describe('Vite Proxy Configuration', () => {
  it('should map Chatterbox TTS server to port 8300', () => {
    const proxy = (config as any).server?.proxy;
    expect(proxy['/api/chatterbox']?.target).toBe('http://127.0.0.1:8300');
  });

  it('should map Multivoice router to port 8001', () => {
    const proxy = (config as any).server?.proxy;
    expect(proxy['/api/multivoice']?.target).toBe('http://127.0.0.1:8001');
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```powershell
npx vitest run cartridges/system-ui/vite-proxy.test.ts
```
Expected output:
`FAIL: target expected 'http://127.0.0.1:8300' but got undefined`

**Step 3: Write minimal implementation**

Modify `cartridges/system-ui/vite.config.ts` (lines 55-75) to append target endpoints:
```typescript
    proxy: {
      '/bifrost': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true,
      },
      '/goRouter': {
        target: 'http://127.0.0.1:8077',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/goRouter/, ''),
      },
      '/api/chatterbox': {
        target: 'http://127.0.0.1:8300',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/chatterbox/, ''),
      },
      '/api/multivoice': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/multivoice/, ''),
      },
      '/api': {
        target: 'http://127.0.0.1:3000',
        changeOrigin: true,
      },
    },
```

**Step 4: Run test to verify it passes**

Run:
```powershell
npx vitest run cartridges/system-ui/vite-proxy.test.ts
```
Expected output:
`PASS: 2 tests passed`

**Step 5: Commit**

Run:
```bash
git add cartridges/system-ui/vite.config.ts cartridges/system-ui/vite-proxy.test.ts
git commit -m "feat(system-ui): add Chatterbox and Multivoice endpoints to dev proxy"
```

---

### Task 2: Kickbox Audio Web Audio API Controller

**Files:**
*   Create: `cartridges/system-ui/src/core/audioContext.ts`
*   Create: `cartridges/system-ui/src/core/audioContext.test.ts`

**Step 1: Write the failing test**

Create `cartridges/system-ui/src/core/audioContext.test.ts`:
```typescript
import { describe, it, expect, vi } from 'vitest';
import { KickboxAudioController } from './audioContext';

describe('KickboxAudioController', () => {
  it('should initialize AudioContext and set gain node volume', () => {
    const controller = new KickboxAudioController();
    controller.init();
    expect(controller.ctx).not.toBeNull();
    
    controller.setVolume(0.7);
    expect(controller.getVolume()).toBe(0.7);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/audioContext.test.ts
```
Expected output:
`FAIL: KickboxAudioController is not defined`

**Step 3: Write minimal implementation**

Create `cartridges/system-ui/src/core/audioContext.ts`:
```typescript
export class KickboxAudioController {
  public ctx: AudioContext | null = null;
  private gainNode: GainNode | null = null;
  private volume: number = 1.0;

  public init() {
    const AudioContextClass = (window.AudioContext || (window as any).webkitAudioContext);
    this.ctx = new AudioContextClass();
    this.gainNode = this.ctx.createGain();
    this.gainNode.gain.setValueAtTime(this.volume, this.ctx.currentTime);
    this.gainNode.connect(this.ctx.destination);
  }

  public setVolume(val: number) {
    this.volume = Math.max(0, Math.min(1, val));
    if (this.gainNode && this.ctx) {
      this.gainNode.gain.setValueAtTime(this.volume, this.ctx.currentTime);
    }
  }

  public getVolume() {
    return this.volume;
  }
}
```

**Step 4: Run test to verify it passes**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/audioContext.test.ts
```
Expected output:
`PASS: 1 test passed`

**Step 5: Commit**

Run:
```bash
git add cartridges/system-ui/src/core/audioContext.ts cartridges/system-ui/src/core/audioContext.test.ts
git commit -m "feat(system-ui): implement Kickbox audio controller class and vitest wrapper"
```

---

### Task 3: Persona.js Voice Character State Manager

**Files:**
*   Create: `cartridges/system-ui/src/core/personaState.ts`
*   Create: `cartridges/system-ui/src/core/personaState.test.ts`

**Step 1: Write the failing test**

Create `cartridges/system-ui/src/core/personaState.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';
import { PersonaStateManager } from './personaState';

describe('PersonaStateManager', () => {
  it('should change active character profile and fetch corresponding attributes', () => {
    const manager = new PersonaStateManager();
    expect(manager.getActivePersona()).toBe('Anya');
    
    manager.setPersona('Merlin');
    expect(manager.getActivePersona()).toBe('Merlin');
    expect(manager.getAttributes().emotion).toBe('LOGIC_STRICT');
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/personaState.test.ts
```
Expected output:
`FAIL: PersonaStateManager not defined`

**Step 3: Write minimal implementation**

Create `cartridges/system-ui/src/core/personaState.ts`:
```typescript
interface PersonaConfig {
  name: string;
  emotion: string;
  voicePitch: number;
  voiceSpeed: number;
}

export class PersonaStateManager {
  private activePersona: string = 'Anya';
  private configs: Record<string, PersonaConfig> = {
    Anya: { name: 'Anya', emotion: 'CREATIVE_BRUTALIST', voicePitch: 1.2, voiceSpeed: 1.1 },
    Merlin: { name: 'Merlin', emotion: 'LOGIC_STRICT', voicePitch: 0.8, voiceSpeed: 0.95 },
    Boris: { name: 'Boris', emotion: 'RESOURCE_CONCENTRATE', voicePitch: 0.9, voiceSpeed: 1.0 },
  };

  public getActivePersona(): string {
    return this.activePersona;
  }

  public setPersona(name: string) {
    if (this.configs[name]) {
      this.activePersona = name;
    }
  }

  public getAttributes(): PersonaConfig {
    return this.configs[this.activePersona];
  }
}
```

**Step 4: Run test to verify it passes**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/personaState.test.ts
```
Expected output:
`PASS: 1 test passed`

**Step 5: Commit**

Run:
```bash
git add cartridges/system-ui/src/core/personaState.ts cartridges/system-ui/src/core/personaState.test.ts
git commit -m "feat(system-ui): implement Persona.js active state configuration engine"
```

---

### Task 4: Aion UI Temporal State Timeline

**Files:**
*   Create: `cartridges/system-ui/src/core/aionTimeline.ts`
*   Create: `cartridges/system-ui/src/core/aionTimeline.test.ts`

**Step 1: Write the failing test**

Create `cartridges/system-ui/src/core/aionTimeline.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';
import { AionTimelineCache } from './aionTimeline';

describe('AionTimelineCache', () => {
  it('should cache state frames and recall state at specific timeline timestamp', () => {
    const timeline = new AionTimelineCache(3);
    timeline.push({ cpu: 15, ram: 42 });
    timeline.push({ cpu: 25, ram: 43 });
    
    expect(timeline.getHistory().length).toBe(2);
    expect(timeline.getFrame(0)?.cpu).toBe(15);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/aionTimeline.test.ts
```
Expected output:
`FAIL: AionTimelineCache not defined`

**Step 3: Write minimal implementation**

Create `cartridges/system-ui/src/core/aionTimeline.ts`:
```typescript
export class AionTimelineCache {
  private frames: any[] = [];
  private limit: number;

  constructor(limit: number = 20) {
    this.limit = limit;
  }

  public push(state: any) {
    this.frames.push({
      ...state,
      timestamp: Date.now(),
    });
    if (this.frames.length > this.limit) {
      this.frames.shift();
    }
  }

  public getHistory() {
    return this.frames;
  }

  public getFrame(index: number) {
    if (index >= 0 && index < this.frames.length) {
      return this.frames[index];
    }
    return null;
  }
}
```

**Step 4: Run test to verify it passes**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/aionTimeline.test.ts
```
Expected output:
`PASS: 1 test passed`

**Step 5: Commit**

Run:
```bash
git add cartridges/system-ui/src/core/aionTimeline.ts cartridges/system-ui/src/core/aionTimeline.test.ts
git commit -m "feat(system-ui): implement Aion UI timeline state caching engine"
```

---

### Task 5: Herdr Swarm Mesh Topology Mapper

**Files:**
*   Create: `cartridges/system-ui/src/core/herdrMesh.ts`
*   Create: `cartridges/system-ui/src/core/herdrMesh.test.ts`

**Step 1: Write the failing test**

Create `cartridges/system-ui/src/core/herdrMesh.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';
import { HerdrMeshRouter } from './herdrMesh';

describe('HerdrMeshRouter', () => {
  it('should track active nodes and link connections', () => {
    const mesh = new HerdrMeshRouter();
    mesh.registerNode('s26', 'EDGE');
    mesh.registerNode('nC', 'ROUTER');
    mesh.connectNodes('s26', 'nC');
    
    expect(mesh.isConnected('s26', 'nC')).toBe(true);
    expect(mesh.isConnected('s26', 'nonexistent')).toBe(false);
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/herdrMesh.test.ts
```
Expected output:
`FAIL: HerdrMeshRouter not defined`

**Step 3: Write minimal implementation**

Create `cartridges/system-ui/src/core/herdrMesh.ts`:
```typescript
export class HerdrMeshRouter {
  private nodes: Map<string, string> = new Map();
  private edges: Set<string> = new Set();

  public registerNode(id: string, type: string) {
    this.nodes.set(id, type);
  }

  public connectNodes(source: string, target: string) {
    this.edges.add(`${source}->${target}`);
  }

  public isConnected(source: string, target: string): boolean {
    return this.edges.has(`${source}->${target}`) || this.edges.has(`${target}->${source}`);
  }

  public getNodes() {
    return Array.from(this.nodes.entries()).map(([id, type]) => ({ id, type }));
  }
}
```

**Step 4: Run test to verify it passes**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/herdrMesh.test.ts
```
Expected output:
`PASS: 1 test passed`

**Step 5: Commit**

Run:
```bash
git add cartridges/system-ui/src/core/herdrMesh.ts cartridges/system-ui/src/core/herdrMesh.test.ts
git commit -m "feat(system-ui): implement Herdr mesh node routing tracker"
```

---

### Task 6: Complete Multi-Tab PWA Overhaul Layout

**Files:**
*   Modify: `cartridges/system-ui/src/core/CamelotLayout.tsx`
*   Test: `cartridges/system-ui/src/core/CamelotLayout.test.tsx`

**Step 1: Write the failing test**

Create `cartridges/system-ui/src/core/CamelotLayout.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import CamelotLayout from './CamelotLayout';

describe('CamelotLayout Component', () => {
  it('should render headers and tabs for Sovereign, Vox, and Forge Factory', () => {
    render(<CamelotLayout />);
    expect(screen.getByText('EXCALIBUR')).toBeInTheDocument();
    expect(screen.getByText('🜲 COMMAND')).toBeInTheDocument();
    expect(screen.getByText('🛠️ FORGE')).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/CamelotLayout.test.tsx
```
Expected output:
`FAIL: Elements not found`

**Step 3: Write minimal implementation**

Overhaul `cartridges/system-ui/src/core/CamelotLayout.tsx` to read dynamic states from `audioContext.ts`, `personaState.ts`, `aionTimeline.ts`, and `herdrMesh.ts`, construct the 4-column retro dashboard layout, configure approval gate actions, and link all bridge endpoints. Ensure WebGL buffers are deallocated properly on unmount via the `VramGovernor` component.

**Step 4: Run test to verify it passes**

Run:
```powershell
npx vitest run cartridges/system-ui/src/core/CamelotLayout.test.tsx
```
Expected output:
`PASS: 1 test passed`

**Step 5: Commit**

Run:
```bash
git add cartridges/system-ui/src/core/CamelotLayout.tsx cartridges/system-ui/src/core/CamelotLayout.test.tsx
git commit -m "feat(system-ui): finalize multi-tab Sovereign Command and Creation Factory layout"
```
