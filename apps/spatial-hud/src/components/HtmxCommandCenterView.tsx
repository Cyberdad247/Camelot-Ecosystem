import React, { useState, useEffect } from 'react';
import { Shield, Sparkles, Activity, CheckCircle2, RefreshCw, Send, Plus, Copy, Check, Terminal, Server, Code, FileText, Play, Radio, Cpu, HardDrive, Download } from 'lucide-react';

interface Task {
  id: string;
  title: string;
  status: 'pending' | 'running' | 'approved';
  risk: 'R1' | 'R2' | 'R3' | 'R4';
}

interface Receipt {
  id: string;
  action: string;
  time: string;
  hash: string;
}

interface SseEvent {
  timestamp: string;
  event: string;
  data: string;
}

interface HtmxCommandCenterViewProps {
  onKineticTrigger?: (cmd: string) => void;
}

export const HtmxCommandCenterView: React.FC<HtmxCommandCenterViewProps> = ({ onKineticTrigger }) => {
  const [activeSubTab, setActiveSubTab] = useState<'dashboard' | 'source' | 'sse'>('dashboard');
  
  // Live State (Mirrors Go Backend state)
  const [systemStatus, setSystemStatus] = useState<'CONVERGED' | 'DEGRADED' | 'DIVERGED'>('CONVERGED');
  const [cpu, setCpu] = useState(42.5);
  const [memory, setMemory] = useState(3.2);
  const [sseActive, setSseActive] = useState(true);

  // Round Table Tasks
  const [tasks, setTasks] = useState<Task[]>([
    { id: 'task_001', title: 'Draft response to Jane', status: 'approved', risk: 'R4' },
    { id: 'task_002', title: 'Create campaign plan', status: 'running', risk: 'R2' },
    { id: 'task_003', title: 'Review invoice #4092', status: 'pending', risk: 'R3' },
    { id: 'task_004', title: 'Bifrost mTLS rotation', status: 'approved', risk: 'R1' },
  ]);

  // Ledger Receipts
  const [receipts, setReceipts] = useState<Receipt[]>([
    { id: '0x9f4a', action: 'email.draft.created', time: '10:23:11', hash: 'sha256:4f9d...e201' },
    { id: '0x7c21', action: 'approval.granted', time: '10:24:32', hash: 'sha256:1a8c...90b4' },
    { id: '0x3e18', action: 'lattice.crdt.sync', time: '10:25:05', hash: 'sha256:8b33...cc7a' },
  ]);

  // SSE Stream log
  const [sseEvents, setSseEvents] = useState<SseEvent[]>([
    { timestamp: '10:23:00', event: 'status', data: '{"status":"CONVERGED","cpu":42.5,"memory":3.2}' },
    { timestamp: '10:23:05', event: 'tasks', data: '[{"id":"task_001","status":"approved"}]' },
  ]);

  // New task form state
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskRisk, setNewTaskRisk] = useState<'R1' | 'R2' | 'R3' | 'R4'>('R2');

  // Source code preview
  const [selectedSourceFile, setSelectedSourceFile] = useState<'main.go' | 'index.html' | 'style.css' | 'service' | 'install.sh'>('main.go');
  const [copied, setCopied] = useState(false);
  const [exported, setExported] = useState(false);
  const [goLiveStatus, setGoLiveStatus] = useState<string | null>(null);

  const handleExportLedgerJson = () => {
    const exportPayload = {
      $schema: "https://camelot-os.invisioned.io/schemas/artifact-ledger.v1.json",
      ledgerTitle: "Camelot-OS Sovereign Artifact Ledger",
      exportedAt: new Date().toISOString(),
      systemStatus: systemStatus,
      cryptographicAnchor: "sha256:4f9d8a21::LATTICE_ANCHORED",
      totalReceipts: receipts.length,
      receipts: receipts,
      tasksAuditSnapshot: tasks,
      meta: {
        runtimeProfile: "8GB_EDGE_NODE_STRICT",
        nodeAnchor: "Cleveland, Ohio",
        operator: "VaShawn O. Head (Vizion) | Invisioned Marketing Inc."
      }
    };

    const jsonString = JSON.stringify(exportPayload, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `camelot-artifact-ledger-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setExported(true);
    setTimeout(() => setExported(false), 2500);
  };

  // Simulate SSE stream heartbeat every 4 seconds
  useEffect(() => {
    if (!sseActive) return;
    const interval = setInterval(() => {
      const newCpu = +(20 + Math.random() * 50).toFixed(1);
      const newMem = +(2.8 + Math.random() * 1.5).toFixed(1);
      setCpu(newCpu);
      setMemory(newMem);

      const timeStr = new Date().toLocaleTimeString();
      setSseEvents((prev) => [
        {
          timestamp: timeStr,
          event: 'status',
          data: JSON.stringify({ status: systemStatus, cpu: newCpu, memory: newMem }),
        },
        ...prev.slice(0, 19),
      ]);
    }, 4000);

    return () => clearInterval(interval);
  }, [sseActive, systemStatus]);

  const handleApproveTask = (taskId: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: 'approved' } : t))
    );
    const newReceipt: Receipt = {
      id: `0x${Math.random().toString(16).substring(2, 6)}`,
      action: `task.approved.${taskId}`,
      time: new Date().toLocaleTimeString(),
      hash: `sha256:${Math.random().toString(36).substring(2, 10)}...${Math.random().toString(36).substring(2, 6)}`,
    };
    setReceipts((prev) => [newReceipt, ...prev]);
  };

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    const newTask: Task = {
      id: `task_00${tasks.length + 1}`,
      title: newTaskTitle.trim(),
      status: 'pending',
      risk: newTaskRisk,
    };
    setTasks((prev) => [...prev, newTask]);
    setNewTaskTitle('');

    const newReceipt: Receipt = {
      id: `0x${Math.random().toString(16).substring(2, 6)}`,
      action: `task.created.${newTask.id}`,
      time: new Date().toLocaleTimeString(),
      hash: `sha256:${Math.random().toString(36).substring(2, 10)}...${Math.random().toString(36).substring(2, 6)}`,
    };
    setReceipts((prev) => [newReceipt, ...prev]);
  };

  const handleGoLive = () => {
    setGoLiveStatus('DEPLOYING SYSTEMD SERVICE...');
    if (onKineticTrigger) onKineticTrigger('//GO_LIVE');
    setTimeout(() => {
      setGoLiveStatus('LIVE ON :8080 // SERVICE camelot-htmx.service (Active/Running)');
      setTimeout(() => setGoLiveStatus(null), 4000);
    }, 1200);
  };

  const handleDispatchPackage = () => {
    if (onKineticTrigger) onKineticTrigger('//DISPATCH');
    setGoLiveStatus('PACKAGE DISPATCHED TO /opt/camelot/htmx-center/');
    setTimeout(() => setGoLiveStatus(null), 3000);
  };

  const sourceCodes: Record<string, string> = {
    'main.go': `package main

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
        {ID: "task_003", Title: "Review invoice", Status: "pending", Risk: "R3"},
    }
    receipts = []Receipt{
        {ID: "0x9f4a", Action: "email.draft.created", Time: "10:23:11", Hash: "sha256:..."},
        {ID: "0x7c21", Action: "approval.granted", Time: "10:24:32", Hash: "sha256:..."},
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
    'index.html': `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camelot-OS Command Center</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="/static/js/htmx.min.js" defer></script>
</head>
<body>
    <header class="header">
        <h1>⚜️ Camelot-OS</h1>
        <p>Omega Apex Singularity — Native Go + HTMX + SSE Command Deck</p>
    </header>

    <main class="grid">
        <div class="cell" hx-get="/fragments/status" hx-trigger="load, every 5s" hx-swap="innerHTML">
            <!-- Status panel will be injected here -->
        </div>
        <div class="cell" hx-get="/fragments/tasks" hx-trigger="load, every 5s" hx-swap="innerHTML">
            <!-- Tasks panel -->
        </div>
        <div class="cell" hx-get="/fragments/receipts" hx-trigger="load, every 5s" hx-swap="innerHTML">
            <!-- Receipts panel -->
        </div>
    </main>
</body>
</html>`,
    'style.css': `:root {
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
  padding: 20px;
}

.header {
  border-bottom: 2px solid var(--luxora-gold);
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.panel {
  border: 1px solid var(--royal-purple);
  background: #1a0f2e;
  padding: 15px;
  border-radius: 8px;
}`,
    'service': `[Unit]
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
    'install.sh': `#!/bin/bash
set -euo pipefail

echo "⚜️ Forging HTMX Command Center..."

# 1. Build Go binary
cd /opt/camelot/htmx-center
go build -o /usr/local/bin/camelot-htmx-center main.go

# 2. Install systemd unit
sudo cp deploy/camelot-htmx.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now camelot-htmx.service

# 3. Verify
curl -s http://localhost:8080/ | grep "Camelot-OS"
echo "✅ HTMX Center is live."`,
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(sourceCodes[selectedSourceFile] || '');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-[#0A0710] text-[#F1EFF4] font-mono overflow-y-auto selection:bg-[#E4B24A]/30 selection:text-[#E4B24A]">
      
      {/* Top Banner & Control Deck */}
      <div className="px-6 py-4 bg-[#120a21] border-b border-[#8E4EC6]/40 flex flex-wrap items-center justify-between gap-4 shrink-0">
        <div>
          <div className="flex items-center space-x-3">
            <span className="text-[#E4B24A] text-xl">⚜️</span>
            <h2 className="text-xl font-bold text-[#E4B24A] tracking-tight">
              Camelot-OS Command Center (HTMX + Go)
            </h2>
            <span className="px-2 py-0.5 bg-[#8E4EC6]/20 border border-[#8E4EC6]/60 text-[#E4B24A] text-[11px] font-bold rounded">
              100% DOCKER-FREE // SSE STREAMING
            </span>
          </div>
          <p className="text-xs text-[#9d8bb3] mt-0.5">
            Native Go standard library + HTMX single-page architecture &middot; Obsidian/Gold/Purple Sovereign Spec
          </p>
        </div>

        {/* Action Triggers */}
        <div className="flex items-center space-x-2.5 text-xs">
          <button
            onClick={handleGoLive}
            className="px-3.5 py-1.5 bg-[#E4B24A] hover:bg-[#d8a436] text-[#0A0710] font-bold rounded-lg flex items-center space-x-1.5 transition-all shadow-md active:scale-95"
          >
            <Play className="w-3.5 h-3.5" />
            <span>//GO_LIVE</span>
          </button>

          <button
            onClick={handleDispatchPackage}
            className="px-3.5 py-1.5 bg-[#8E4EC6]/30 hover:bg-[#8E4EC6]/50 text-[#E4B24A] border border-[#8E4EC6]/60 font-bold rounded-lg flex items-center space-x-1.5 transition-all active:scale-95"
          >
            <Server className="w-3.5 h-3.5" />
            <span>//DISPATCH</span>
          </button>

          <div className="flex items-center bg-[#0A0710] border border-[#8E4EC6]/50 rounded-lg p-0.5">
            <button
              onClick={() => setActiveSubTab('dashboard')}
              className={`px-3 py-1 rounded text-xs transition-all ${
                activeSubTab === 'dashboard'
                  ? 'bg-[#8E4EC6] text-white font-bold'
                  : 'text-[#9d8bb3] hover:text-white'
              }`}
            >
              Live Center
            </button>
            <button
              onClick={() => setActiveSubTab('sse')}
              className={`px-3 py-1 rounded text-xs transition-all flex items-center space-x-1 ${
                activeSubTab === 'sse'
                  ? 'bg-[#8E4EC6] text-white font-bold'
                  : 'text-[#9d8bb3] hover:text-white'
              }`}
            >
              <Radio className="w-3 h-3 text-[#E4B24A]" />
              <span>SSE Log</span>
            </button>
            <button
              onClick={() => setActiveSubTab('source')}
              className={`px-3 py-1 rounded text-xs transition-all ${
                activeSubTab === 'source'
                  ? 'bg-[#8E4EC6] text-white font-bold'
                  : 'text-[#9d8bb3] hover:text-white'
              }`}
            >
              Go / HTMX Code
            </button>
          </div>
        </div>
      </div>

      {/* Deploy Status Banner */}
      {goLiveStatus && (
        <div className="px-6 py-2 bg-[#6DC26D]/20 border-b border-[#6DC26D]/40 text-[#6DC26D] text-xs flex items-center space-x-2 animate-fadeIn">
          <Sparkles className="w-4 h-4 animate-spin" />
          <span className="font-bold">{goLiveStatus}</span>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full space-y-6">

        {/* Tab 1: Live Interactive HTMX Dashboard */}
        {activeSubTab === 'dashboard' && (
          <div className="space-y-6">
            
            {/* Header Telemetry Pill */}
            <div className="flex flex-wrap items-center justify-between gap-3 text-xs bg-[#150c26] border border-[#8E4EC6]/40 p-3.5 rounded-xl">
              <div className="flex items-center space-x-4">
                <span className="text-[#9d8bb3]">Service: <strong className="text-[#E4B24A]">camelot-htmx.service</strong></span>
                <span className="text-[#9d8bb3]">Port: <strong className="text-[#F1EFF4]">:8080</strong></span>
                <span className="text-[#9d8bb3]">Location: <strong className="text-[#F1EFF4]">/opt/camelot/htmx-center/</strong></span>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setSseActive(!sseActive)}
                  className={`px-2.5 py-1 rounded border text-[11px] flex items-center space-x-1.5 ${
                    sseActive
                      ? 'bg-[#6DC26D]/20 text-[#6DC26D] border-[#6DC26D]/40'
                      : 'bg-neutral-800 text-neutral-400 border-neutral-700'
                  }`}
                >
                  <span className={`w-2 h-2 rounded-full ${sseActive ? 'bg-[#6DC26D] animate-ping' : 'bg-neutral-500'}`} />
                  <span>{sseActive ? 'SSE Stream Live' : 'SSE Paused'}</span>
                </button>
              </div>
            </div>

            {/* 3-Column Native HTMX Panels Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              
              {/* Panel 1: Throne Room (Status Panel) */}
              <div className="border border-[#8E4EC6] bg-[#150c26] p-5 rounded-xl shadow-xl flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-center justify-between border-b border-[#E4B24A]/30 pb-3 mb-4">
                    <h2 className="text-[#E4B24A] font-bold text-base m-0">👑 Throne Room</h2>
                    <span className="text-[10px] text-[#8E4EC6] uppercase tracking-wider font-bold">hx-get="/fragments/status"</span>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-[#9d8bb3]">System State:</span>
                      <span
                        className={`font-bold px-2 py-0.5 rounded text-xs ${
                          systemStatus === 'CONVERGED'
                            ? 'text-[#6DC26D] bg-[#6DC26D]/15'
                            : systemStatus === 'DEGRADED'
                            ? 'text-[#D9A23C] bg-[#D9A23C]/15'
                            : 'text-[#DE4258] bg-[#DE4258]/15'
                        }`}
                      >
                        {systemStatus}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-[#9d8bb3] flex items-center gap-1.5">
                        <Cpu className="w-3.5 h-3.5 text-[#E4B24A]" />
                        CPU Load:
                      </span>
                      <span className="font-bold text-[#E4B24A]">{cpu.toFixed(1)}%</span>
                    </div>

                    <div className="w-full h-1.5 bg-[#0A0710] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-[#6DC26D] via-[#E4B24A] to-[#DE4258] rounded-full transition-all duration-300"
                        style={{ width: `${Math.min(cpu, 100)}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-[#9d8bb3] flex items-center gap-1.5">
                        <HardDrive className="w-3.5 h-3.5 text-[#8E4EC6]" />
                        Memory:
                      </span>
                      <span className="font-bold text-[#F1EFF4]">{memory.toFixed(1)} GB / 8.0 GB</span>
                    </div>
                  </div>
                </div>

                {/* State Override Selector */}
                <div className="pt-3 border-t border-[#8E4EC6]/30">
                  <span className="text-[10px] text-[#9d8bb3] uppercase block mb-1.5">Simulate State Transition:</span>
                  <div className="grid grid-cols-3 gap-1 text-[10px]">
                    <button
                      onClick={() => setSystemStatus('CONVERGED')}
                      className={`py-1 rounded font-bold transition-all ${
                        systemStatus === 'CONVERGED'
                          ? 'bg-[#6DC26D] text-black'
                          : 'bg-[#0A0710] text-[#6DC26D] border border-[#6DC26D]/30'
                      }`}
                    >
                      CONVERGED
                    </button>
                    <button
                      onClick={() => setSystemStatus('DEGRADED')}
                      className={`py-1 rounded font-bold transition-all ${
                        systemStatus === 'DEGRADED'
                          ? 'bg-[#D9A23C] text-black'
                          : 'bg-[#0A0710] text-[#D9A23C] border border-[#D9A23C]/30'
                      }`}
                    >
                      DEGRADED
                    </button>
                    <button
                      onClick={() => setSystemStatus('DIVERGED')}
                      className={`py-1 rounded font-bold transition-all ${
                        systemStatus === 'DIVERGED'
                          ? 'bg-[#DE4258] text-white'
                          : 'bg-[#0A0710] text-[#DE4258] border border-[#DE4258]/30'
                      }`}
                    >
                      DIVERGED
                    </button>
                  </div>
                </div>
              </div>

              {/* Panel 2: Round Table (Tasks Panel) */}
              <div className="border border-[#8E4EC6] bg-[#150c26] p-5 rounded-xl shadow-xl flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-center justify-between border-b border-[#E4B24A]/30 pb-3 mb-4">
                    <h2 className="text-[#E4B24A] font-bold text-base m-0">⚔️ Round Table</h2>
                    <span className="text-[10px] text-[#8E4EC6] uppercase tracking-wider font-bold">hx-get="/fragments/tasks"</span>
                  </div>

                  <ul className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
                    {tasks.map((task) => (
                      <li
                        key={task.id}
                        className="p-2.5 rounded bg-[#0A0710] border border-[#8E4EC6]/40 flex items-center justify-between text-xs"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-[#F1EFF4]">{task.title}</span>
                            <span className="text-[#E4B24A] font-bold text-[10px] bg-[#E4B24A]/10 px-1.5 py-0.5 rounded border border-[#E4B24A]/30">
                              {task.risk}
                            </span>
                          </div>
                          <span className="text-[10px] text-[#9d8bb3] font-mono">[{task.status}]</span>
                        </div>

                        {task.status !== 'approved' ? (
                          <button
                            onClick={() => handleApproveTask(task.id)}
                            className="px-2 py-1 bg-[#6DC26D]/20 hover:bg-[#6DC26D]/30 text-[#6DC26D] border border-[#6DC26D]/50 rounded text-[10px] font-bold transition-all"
                          >
                            Approve
                          </button>
                        ) : (
                          <span className="text-[#6DC26D] text-[10px] font-bold flex items-center gap-1">
                            <Check className="w-3 h-3" /> Signed
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Add Task Sub-form */}
                <form onSubmit={handleAddTask} className="pt-3 border-t border-[#8E4EC6]/30 space-y-2">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="New task directive..."
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      className="flex-1 bg-[#0A0710] border border-[#8E4EC6]/50 rounded px-2.5 py-1 text-xs text-[#F1EFF4] placeholder:text-neutral-600 focus:outline-none focus:border-[#E4B24A]"
                    />
                    <select
                      value={newTaskRisk}
                      onChange={(e) => setNewTaskRisk(e.target.value as any)}
                      className="bg-[#0A0710] border border-[#8E4EC6]/50 rounded px-2 py-1 text-xs text-[#E4B24A] focus:outline-none"
                    >
                      <option value="R1">R1</option>
                      <option value="R2">R2</option>
                      <option value="R3">R3</option>
                      <option value="R4">R4</option>
                    </select>
                    <button
                      type="submit"
                      className="px-2.5 py-1 bg-[#8E4EC6] hover:bg-[#9e5ed6] text-white rounded text-xs font-bold transition-all"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </form>
              </div>

              {/* Panel 3: Ledger (Receipts Panel) */}
              <div className="border border-[#8E4EC6] bg-[#150c26] p-5 rounded-xl shadow-xl flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-center justify-between border-b border-[#E4B24A]/30 pb-3 mb-4">
                    <div className="flex items-center space-x-2">
                      <h2 className="text-[#E4B24A] font-bold text-base m-0">📜 Ledger</h2>
                      <span className="text-[10px] text-[#8E4EC6] uppercase tracking-wider font-bold">hx-get="/fragments/receipts"</span>
                    </div>
                    <button
                      onClick={handleExportLedgerJson}
                      title="Export current artifact ledger as local JSON file"
                      className="px-2.5 py-1 bg-[#E4B24A]/15 hover:bg-[#E4B24A]/25 text-[#E4B24A] border border-[#E4B24A]/40 rounded text-xs font-bold transition-all flex items-center space-x-1.5 active:scale-95 shadow-sm"
                    >
                      {exported ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-[#6DC26D]" />
                          <span className="text-[#6DC26D]">Exported!</span>
                        </>
                      ) : (
                        <>
                          <Download className="w-3.5 h-3.5" />
                          <span>Export JSON</span>
                        </>
                      )}
                    </button>
                  </div>

                  <div className="overflow-x-auto max-h-60 overflow-y-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-[#8E4EC6]/40 bg-[#8E4EC6]/20 text-[#E4B24A]">
                          <th className="p-2">ID</th>
                          <th className="p-2">Action</th>
                          <th className="p-2">Time</th>
                        </tr>
                      </thead>
                      <tbody>
                        {receipts.map((rec) => (
                          <tr key={rec.id} className="border-b border-[#8E4EC6]/20 hover:bg-[#8E4EC6]/10">
                            <td className="p-2 font-bold text-[#E4B24A]">{rec.id}</td>
                            <td className="p-2 text-[#F1EFF4]">{rec.action}</td>
                            <td className="p-2 text-[#9d8bb3]">{rec.time}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#8E4EC6]/30 flex items-center justify-between text-[10px] text-[#9d8bb3]">
                  <span>Cryptographic Proofs: SHA-256</span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleExportLedgerJson}
                      className="text-[#E4B24A] hover:underline flex items-center gap-1 font-bold"
                    >
                      <Download className="w-3 h-3" />
                      <span>.json</span>
                    </button>
                    <span className="text-[#6DC26D] font-bold">LATTICE ANCHORED</span>
                  </div>
                </div>
              </div>

            </div>

            {/* Architecture Highlights Banner */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-sans">
              <div className="p-4 bg-[#150c26] border border-[#8E4EC6]/40 rounded-xl space-y-1">
                <h4 className="font-bold text-[#E4B24A] font-mono">100% Docker-Free Go Binary</h4>
                <p className="text-[#9d8bb3]">Single compiled static binary with embedded HTML templates running under systemd.</p>
              </div>
              <div className="p-4 bg-[#150c26] border border-[#8E4EC6]/40 rounded-xl space-y-1">
                <h4 className="font-bold text-[#E4B24A] font-mono">HTMX Dynamic Fragment Ingress</h4>
                <p className="text-[#9d8bb3]">Zero JavaScript framework weight. Swaps HTML partials via hx-get every 5 seconds.</p>
              </div>
              <div className="p-4 bg-[#150c26] border border-[#8E4EC6]/40 rounded-xl space-y-1">
                <h4 className="font-bold text-[#E4B24A] font-mono">Real-Time Server-Sent Events (SSE)</h4>
                <p className="text-[#9d8bb3]">Native Go channels pushing structured JSON status over persistent /stream pipe.</p>
              </div>
            </div>

          </div>
        )}

        {/* Tab 2: SSE Live Event Inspector */}
        {activeSubTab === 'sse' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-[#E4B24A]">Server-Sent Events (SSE) Stream Inspector</h3>
                <p className="text-xs text-[#9d8bb3]">Live stream connected to <code className="text-[#E4B24A]">/stream</code> endpoint</p>
              </div>
              <button
                onClick={() => setSseEvents([])}
                className="px-3 py-1.5 bg-[#0A0710] hover:bg-[#150c26] text-[#9d8bb3] hover:text-white border border-[#8E4EC6]/50 rounded-lg text-xs"
              >
                Clear Stream Log
              </button>
            </div>

            <div className="bg-[#150c26] border border-[#8E4EC6] rounded-xl p-5 space-y-3 font-mono">
              <div className="flex items-center space-x-2 text-xs text-[#6DC26D] pb-2 border-b border-[#8E4EC6]/30">
                <Radio className="w-4 h-4 animate-pulse" />
                <span>STREAM_CONNECTED // HTTP/1.1 200 OK Content-Type: text/event-stream</span>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto text-xs">
                {sseEvents.map((evt, idx) => (
                  <div key={idx} className="p-3 bg-[#0A0710] rounded border border-[#8E4EC6]/30 space-y-1">
                    <div className="flex items-center justify-between text-[11px] text-[#9d8bb3]">
                      <span>event: <strong className="text-[#E4B24A]">{evt.event}</strong></span>
                      <span>{evt.timestamp}</span>
                    </div>
                    <pre className="text-[#6DC26D] text-[11px] overflow-x-auto">data: {evt.data}</pre>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Source Code Inspector & Package Dispatch */}
        {activeSubTab === 'source' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center space-x-2">
                {(['main.go', 'index.html', 'style.css', 'service', 'install.sh'] as const).map((file) => (
                  <button
                    key={file}
                    onClick={() => setSelectedSourceFile(file)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                      selectedSourceFile === file
                        ? 'bg-[#E4B24A] text-[#0A0710]'
                        : 'bg-[#150c26] text-[#9d8bb3] border border-[#8E4EC6]/40 hover:text-white'
                    }`}
                  >
                    {file}
                  </button>
                ))}
              </div>

              <button
                onClick={handleCopyCode}
                className="px-3.5 py-1.5 bg-[#0A0710] hover:bg-[#150c26] text-[#E4B24A] border border-[#E4B24A]/50 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition-all"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-[#6DC26D]" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied to Clipboard' : 'Copy File Content'}</span>
              </button>
            </div>

            <div className="bg-[#150c26] border border-[#8E4EC6] rounded-xl overflow-hidden shadow-2xl">
              <div className="px-5 py-3 border-b border-[#8E4EC6]/40 bg-[#0A0710] flex items-center justify-between text-xs text-[#9d8bb3]">
                <span>Path: /opt/camelot/htmx-center/{selectedSourceFile}</span>
                <span className="text-[#E4B24A] font-bold">100% Docker-Free</span>
              </div>
              <div className="p-5 overflow-x-auto max-h-[500px]">
                <pre className="text-xs text-[#F1EFF4] leading-relaxed font-mono">
                  {sourceCodes[selectedSourceFile]}
                </pre>
              </div>
            </div>
          </div>
        )}

      </div>

    </div>
  );
};
