'use client';

// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import React, { useState } from 'react';
import { InlineApprovalCard, PermissionRequestUI } from './InlineApprovalCard';

export interface SandboxMetricsUI {
  worker_id: string;
  knight_id: string;
  memory_rss_mb: number;
  memory_max_mb: number;
  memory_pct: number;
  cpu_usage_pct: number;
  cpu_quota_pct: number;
  vfs_files_count: number;
  vfs_bytes_used: number;
  status: string;
}

export interface MilestoneUI {
  milestone_id: string;
  title: string;
  description: string;
  assigned_knight: string;
  risk_tier: string;
  status: string;
  target_path?: string;
  error?: string;
}

export interface WorkerStatusUI {
  worker_id: string;
  goal_id: string;
  title: string;
  objective: string;
  lead_knight: string;
  status: string;
  current_milestone_index: number;
  total_milestones: number;
  progress_pct: number;
  milestones: MilestoneUI[];
  sandbox_metrics: SandboxMetricsUI;
  pending_hitl_requests: PermissionRequestUI[];
  updated_at: string;
}

export const NorthstarWorkerDashboard: React.FC = () => {
  const [activeWorkerId, setActiveWorkerId] = useState<string>('WRK-AUDIO-01');
  const [newGoalTitle, setNewGoalTitle] = useState<string>('');
  const [newGoalObjective, setNewGoalObjective] = useState<string>('');
  const [selectedLeadKnight, setSelectedLeadKnight] = useState<string>('MERLIN_Ω');

  // Initial mock / state representing workers in Personal CPU Sandboxes
  const [workers, setWorkers] = useState<WorkerStatusUI[]>([
    {
      worker_id: 'WRK-AUDIO-01',
      goal_id: 'GOAL-8F3A10BC',
      title: 'Zero-Copy Ringbuffer Audio Pipeline',
      objective: 'Synthesize low-latency zero-copy ringbuffer in Rust for multivoice bridge',
      lead_knight: 'SIR_SONUS',
      status: 'BLOCKED_ON_HITL',
      current_milestone_index: 2,
      total_milestones: 5,
      progress_pct: 40.0,
      sandbox_metrics: {
        worker_id: 'WRK-AUDIO-01',
        knight_id: 'SIR_SONUS',
        memory_rss_mb: 84.5,
        memory_max_mb: 350.0,
        memory_pct: 24.1,
        cpu_usage_pct: 18.2,
        cpu_quota_pct: 60.0,
        vfs_files_count: 7,
        vfs_bytes_used: 48290,
        status: 'RUNNING',
      },
      pending_hitl_requests: [
        {
          request_id: 'PR-8D19F0A2',
          worker_id: 'WRK-AUDIO-01',
          knight_id: 'SIR_CODEX',
          operation_type: 'VFS_WRITE',
          target: '04_KINETIC/multivoice/src/ringbuffer.rs',
          summary: 'Milestone WRK-AUDIO-01-M3: Kinetic Ringbuffer Implementation',
          details: { lines_count: 85, crate: 'multivoice' },
          risk_tier: 'R3_HIGH',
          status: 'PENDING',
          created_at: new Date().toISOString(),
        },
      ],
      milestones: [
        {
          milestone_id: 'WRK-AUDIO-01-M1',
          title: 'Telemetry & Pre-flight Inspection',
          description: 'Probe VFS mounts and initialize sandbox staging',
          assigned_knight: 'SIR_HELIOS',
          risk_tier: 'R0_SAFE',
          status: 'COMPLETED',
        },
        {
          milestone_id: 'WRK-AUDIO-01-M2',
          title: 'Specification Formulation',
          description: 'Draft memory alignment and lock-free concurrency design',
          assigned_knight: 'SIR_BORIS',
          risk_tier: 'R1_LOW',
          status: 'COMPLETED',
        },
        {
          milestone_id: 'WRK-AUDIO-01-M3',
          title: 'Kinetic Ringbuffer Implementation',
          description: 'Synthesize ringbuffer.rs under WASI bounds',
          assigned_knight: 'SIR_CODEX',
          risk_tier: 'R3_HIGH',
          status: 'BLOCKED_ON_HITL',
        },
        {
          milestone_id: 'WRK-AUDIO-01-M4',
          title: 'Formal Z3 Proof & Gate Clearance',
          description: 'Verify race-freedom and buffer bounds',
          assigned_knight: 'ANYA_Ω',
          risk_tier: 'R2_MEDIUM',
          status: 'PENDING',
        },
        {
          milestone_id: 'WRK-AUDIO-01-M5',
          title: 'Provenance Crystallization',
          description: 'Record sha256 hashes to Ledger',
          assigned_knight: 'LADY_MNEMOSYNE',
          risk_tier: 'R1_LOW',
          status: 'PENDING',
        },
      ],
      updated_at: new Date().toISOString(),
    },
    {
      worker_id: 'WRK-SQUIRE-09',
      goal_id: 'GOAL-41B099AA',
      title: 'Autonomous Secret Scanning & Ghost Vault Purge',
      objective: 'Sweep 03_VAULT for raw token patterns and quarantine to SIR_GHOST',
      lead_knight: 'SIR_GHOST',
      status: 'RUNNING',
      current_milestone_index: 3,
      total_milestones: 5,
      progress_pct: 60.0,
      sandbox_metrics: {
        worker_id: 'WRK-SQUIRE-09',
        knight_id: 'SIR_GHOST',
        memory_rss_mb: 42.1,
        memory_max_mb: 350.0,
        memory_pct: 12.0,
        cpu_usage_pct: 8.5,
        cpu_quota_pct: 60.0,
        vfs_files_count: 142,
        vfs_bytes_used: 1284900,
        status: 'RUNNING',
      },
      pending_hitl_requests: [],
      milestones: [
        {
          milestone_id: 'WRK-SQUIRE-09-M1',
          title: 'Pre-flight Vault Telemetry',
          description: 'Index file boundaries',
          assigned_knight: 'SIR_HELIOS',
          risk_tier: 'R0_SAFE',
          status: 'COMPLETED',
        },
        {
          milestone_id: 'WRK-SQUIRE-09-M2',
          title: 'Entropy Scan',
          description: 'Locate Shannon entropy spikes',
          assigned_knight: 'SIR_GHOST',
          risk_tier: 'R1_LOW',
          status: 'COMPLETED',
        },
        {
          milestone_id: 'WRK-SQUIRE-09-M3',
          title: 'Quarantine Redaction',
          description: 'Move matching keys into Air-Gap Vault',
          assigned_knight: 'SIR_GHOST',
          risk_tier: 'R2_MEDIUM',
          status: 'IN_PROGRESS',
        },
        {
          milestone_id: 'WRK-SQUIRE-09-M4',
          title: 'Verification',
          description: 'Ensure config.json flags match presence',
          assigned_knight: 'ANYA_Ω',
          risk_tier: 'R2_MEDIUM',
          status: 'PENDING',
        },
        {
          milestone_id: 'WRK-SQUIRE-09-M5',
          title: 'Ledger Inscription',
          description: 'Commit scan receipt',
          assigned_knight: 'LADY_MNEMOSYNE',
          risk_tier: 'R1_LOW',
          status: 'PENDING',
        },
      ],
      updated_at: new Date().toISOString(),
    },
  ]);

  const activeWorker = workers.find((w) => w.worker_id === activeWorkerId) || workers[0];

  const handleApprove = (requestId: string) => {
    setWorkers((prev) =>
      prev.map((w) => {
        const remainingReqs = w.pending_hitl_requests.filter((r) => r.request_id !== requestId);
        let updatedStatus = w.status;
        let updatedMilestones = [...w.milestones];

        if (w.status === 'BLOCKED_ON_HITL' && remainingReqs.length === 0) {
          updatedStatus = 'RUNNING';
          updatedMilestones = updatedMilestones.map((m) =>
            m.status === 'BLOCKED_ON_HITL' ? { ...m, status: 'IN_PROGRESS' } : m
          );
        }

        return {
          ...w,
          status: updatedStatus,
          milestones: updatedMilestones,
          pending_hitl_requests: remainingReqs,
        };
      })
    );
  };

  const handleDeny = (requestId: string) => {
    setWorkers((prev) =>
      prev.map((w) => ({
        ...w,
        status: 'FAILED',
        pending_hitl_requests: w.pending_hitl_requests.filter((r) => r.request_id !== requestId),
      }))
    );
  };

  const handleStepWorker = (workerId: string) => {
    setWorkers((prev) =>
      prev.map((w) => {
        if (w.worker_id !== workerId || w.status === 'BLOCKED_ON_HITL') return w;
        const nextIdx = w.current_milestone_index + 1;
        const isComplete = nextIdx >= w.total_milestones;

        const updatedMilestones = w.milestones.map((m, idx) => {
          if (idx === w.current_milestone_index) return { ...m, status: 'COMPLETED' };
          if (idx === nextIdx) return { ...m, status: 'IN_PROGRESS' };
          return m;
        });

        return {
          ...w,
          current_milestone_index: nextIdx,
          progress_pct: Math.min(100, Math.round((nextIdx / w.total_milestones) * 100)),
          status: isComplete ? 'COMPLETED' : 'RUNNING',
          milestones: updatedMilestones,
        };
      })
    );
  };

  const handleDispatchGoal = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGoalTitle.trim()) return;

    const newWorkerId = `WRK-${Math.random().toString(16).substring(2, 8).toUpperCase()}`;
    const newGoal: WorkerStatusUI = {
      worker_id: newWorkerId,
      goal_id: `GOAL-${Math.random().toString(16).substring(2, 10).toUpperCase()}`,
      title: newGoalTitle,
      objective: newGoalObjective || newGoalTitle,
      lead_knight: selectedLeadKnight,
      status: 'RUNNING',
      current_milestone_index: 0,
      total_milestones: 5,
      progress_pct: 0,
      sandbox_metrics: {
        worker_id: newWorkerId,
        knight_id: selectedLeadKnight,
        memory_rss_mb: 28.4,
        memory_max_mb: 350.0,
        memory_pct: 8.1,
        cpu_usage_pct: 12.0,
        cpu_quota_pct: 60.0,
        vfs_files_count: 3,
        vfs_bytes_used: 12400,
        status: 'RUNNING',
      },
      pending_hitl_requests: [],
      milestones: [
        {
          milestone_id: `${newWorkerId}-M1`,
          title: 'Telemetry Pre-flight',
          description: 'Audit runtime and mount sandbox root',
          assigned_knight: 'SIR_HELIOS',
          risk_tier: 'R0_SAFE',
          status: 'IN_PROGRESS',
        },
        {
          milestone_id: `${newWorkerId}-M2`,
          title: 'Blueprint Architecture',
          description: 'Synthesize formal milestone specification',
          assigned_knight: 'SIR_BORIS',
          risk_tier: 'R1_LOW',
          status: 'PENDING',
        },
        {
          milestone_id: `${newWorkerId}-M3`,
          title: 'Kinetic Code Synthesis',
          description: 'Synthesize verified artifact under sandbox bounds',
          assigned_knight: 'SIR_CODEX',
          risk_tier: 'R3_HIGH',
          status: 'PENDING',
        },
        {
          milestone_id: `${newWorkerId}-M4`,
          title: 'Formal Z3 Proof & Gate Verification',
          description: 'Anya Gate zero-bypass verification clearance',
          assigned_knight: 'ANYA_Ω',
          risk_tier: 'R2_MEDIUM',
          status: 'PENDING',
        },
        {
          milestone_id: `${newWorkerId}-M5`,
          title: 'Provenance Crystallization',
          description: 'Ledger inscription & Glass Observatory XP reward',
          assigned_knight: 'LADY_MNEMOSYNE',
          risk_tier: 'R1_LOW',
          status: 'PENDING',
        },
      ],
      updated_at: new Date().toISOString(),
    };

    setWorkers([newGoal, ...workers]);
    setActiveWorkerId(newWorkerId);
    setNewGoalTitle('');
    setNewGoalObjective('');
  };

  return (
    <div className="border border-gold/30 bg-smoke-900/90 p-6 rounded font-mono text-white/90 shadow-2xl backdrop-blur-md space-y-6">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gold/20 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-2xl">🛡️</span>
            <h2 className="text-lg font-bold uppercase tracking-wider text-gold-royal">
              Northstar Goal Background Workers
            </h2>
          </div>
          <p className="text-xs text-white/60 mt-1">
            Persistent autonomous background execution · Dedicated Personal CPU Sandboxes · Inline HITL Broker
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="border border-white/10 bg-black/40 px-3 py-1.5 rounded">
            <span className="text-white/40">Active Workers: </span>
            <span className="text-gold font-bold">{workers.length}</span>
          </div>
          <div className="border border-white/10 bg-black/40 px-3 py-1.5 rounded">
            <span className="text-white/40">Memory Cap: </span>
            <span className="text-cyan-400 font-bold">&lt;350MB RSS</span>
          </div>
          <div className="border border-white/10 bg-black/40 px-3 py-1.5 rounded">
            <span className="text-white/40">CPU Quota: </span>
            <span className="text-emerald-400 font-bold">60% Core</span>
          </div>
        </div>
      </div>

      {/* ── Top Grid: Contact Roster & Sandbox Gauges ───────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Contact Roster */}
        <div className="border border-gold/20 bg-smoke-950/70 rounded p-4 space-y-3">
          <div className="text-xs uppercase font-bold text-gold/80 flex items-center justify-between border-b border-white/10 pb-2">
            <span>Worker Roster</span>
            <span className="text-[10px] text-white/40">Select to inspect</span>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {workers.map((w) => {
              const isSelected = w.worker_id === activeWorkerId;
              const hasHitl = w.pending_hitl_requests.length > 0;
              return (
                <button
                  type="button"
                  key={w.worker_id}
                  onClick={() => setActiveWorkerId(w.worker_id)}
                  className={`w-full text-left p-3 rounded border transition-all ${
                    isSelected
                      ? 'border-gold bg-gold/10 text-white'
                      : 'border-white/10 bg-black/30 hover:border-gold/40 text-white/70'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-gold-royal">{w.worker_id}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold ${
                        hasHitl
                          ? 'border-amber-500/50 bg-amber-500/10 text-amber-300 animate-pulse'
                          : w.status === 'COMPLETED'
                          ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300'
                          : 'border-blue-500/50 bg-blue-500/10 text-blue-300'
                      }`}
                    >
                      {w.status}
                    </span>
                  </div>
                  <div className="text-xs font-semibold truncate text-white">{w.title}</div>
                  <div className="flex items-center justify-between text-[11px] text-white/50 mt-2">
                    <span>{w.lead_knight}</span>
                    <span className="text-gold font-bold">{w.progress_pct}%</span>
                  </div>
                  {/* Mini Progress Bar */}
                  <div className="w-full bg-white/10 h-1 rounded mt-1 overflow-hidden">
                    <div
                      className="bg-gold h-full transition-all duration-300"
                      style={{ width: `${w.progress_pct}%` }}
                    />
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Worker Sandbox Telemetry Gauges */}
        <div className="lg:col-span-2 border border-gold/20 bg-smoke-950/70 rounded p-4 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-2">
            <div>
              <div className="text-xs text-white/40">Inspecting Sandbox:</div>
              <div className="text-sm font-bold text-gold-royal flex items-center gap-2">
                <span>{activeWorker.worker_id}</span>
                <span className="text-xs px-2 py-0.5 rounded border border-white/10 bg-black/40 text-white/70">
                  {activeWorker.lead_knight}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handleStepWorker(activeWorker.worker_id)}
                disabled={activeWorker.status === 'BLOCKED_ON_HITL' || activeWorker.status === 'COMPLETED'}
                className="px-3 py-1 text-xs uppercase font-bold border border-gold bg-gold/20 text-gold-royal hover:bg-gold/30 rounded transition-all disabled:opacity-40"
              >
                ▶ Step Milestone
              </button>
            </div>
          </div>

          <div className="text-xs text-white/80">
            <span className="text-gold font-bold">Goal: </span>
            {activeWorker.title}
          </div>

          {/* Real-Time Hardware Gauges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-black/50 border border-white/10 p-2.5 rounded">
              <div className="text-[10px] text-white/40 uppercase">Memory (RSS)</div>
              <div className="text-sm font-bold text-cyan-400 mt-1">
                {activeWorker.sandbox_metrics.memory_rss_mb} MB
              </div>
              <div className="text-[10px] text-white/50">
                {activeWorker.sandbox_metrics.memory_pct}% of 350M cap
              </div>
            </div>

            <div className="bg-black/50 border border-white/10 p-2.5 rounded">
              <div className="text-[10px] text-white/40 uppercase">CPU Usage</div>
              <div className="text-sm font-bold text-emerald-400 mt-1">
                {activeWorker.sandbox_metrics.cpu_usage_pct}%
              </div>
              <div className="text-[10px] text-white/50">
                Quota: {activeWorker.sandbox_metrics.cpu_quota_pct}%
              </div>
            </div>

            <div className="bg-black/50 border border-white/10 p-2.5 rounded">
              <div className="text-[10px] text-white/40 uppercase">VFS Files</div>
              <div className="text-sm font-bold text-gold mt-1">
                {activeWorker.sandbox_metrics.vfs_files_count}
              </div>
              <div className="text-[10px] text-white/50 truncate">
                {(activeWorker.sandbox_metrics.vfs_bytes_used / 1024).toFixed(1)} KB staged
              </div>
            </div>

            <div className="bg-black/50 border border-white/10 p-2.5 rounded">
              <div className="text-[10px] text-white/40 uppercase">VFS Quarantine Root</div>
              <div className="text-[11px] font-mono text-white/80 mt-1 truncate">
                vfs://worldtree/...
              </div>
              <div className="text-[10px] text-white/50">Position-addressed</div>
            </div>
          </div>

          {/* Pending HITL Requests Section */}
          {activeWorker.pending_hitl_requests.length > 0 && (
            <div className="border border-amber-500/40 bg-amber-950/20 rounded p-3 space-y-3">
              <div className="text-xs uppercase font-bold text-amber-300 flex items-center gap-2">
                <span>⚠️</span>
                <span>Pending Human Gate Approvals ({activeWorker.pending_hitl_requests.length})</span>
              </div>
              {activeWorker.pending_hitl_requests.map((req) => (
                <InlineApprovalCard
                  key={req.request_id}
                  request={req}
                  onApprove={handleApprove}
                  onDeny={handleDeny}
                />
              ))}
            </div>
          )}

          {/* Milestone DAG Timeline */}
          <div className="space-y-2">
            <div className="text-xs uppercase font-bold text-gold/80">Merlin Ω Milestones DAG</div>
            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {activeWorker.milestones.map((m, idx) => {
                const isCurrent = idx === activeWorker.current_milestone_index;
                const isDone = m.status === 'COMPLETED';
                const isBlocked = m.status === 'BLOCKED_ON_HITL';

                return (
                  <div
                    key={m.milestone_id}
                    className={`flex items-center justify-between p-2 rounded border text-xs ${
                      isBlocked
                        ? 'border-amber-500/50 bg-amber-500/10 text-amber-300'
                        : isDone
                        ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-300'
                        : isCurrent
                        ? 'border-gold bg-gold/10 text-white'
                        : 'border-white/5 bg-black/20 text-white/40'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <span>{isDone ? '✓' : isBlocked ? '⏸' : isCurrent ? '▶' : '○'}</span>
                      <span className="font-semibold">{m.title}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/40 text-white/60">
                        {m.assigned_knight}
                      </span>
                      <span className="text-[10px] font-bold uppercase">{m.status}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* ── Bottom Section: Goal Dispatcher ─────────────────────────────── */}
      <div className="border border-gold/20 bg-smoke-950/70 rounded p-4">
        <div className="text-xs uppercase font-bold text-gold/80 mb-3 flex items-center gap-2">
          <span>⚡</span>
          <span>Decompose & Dispatch Autonomous Northstar Goal</span>
        </div>
        <form onSubmit={handleDispatchGoal} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="text-[11px] text-white/50 block mb-1">Goal Title</label>
            <input
              type="text"
              value={newGoalTitle}
              onChange={(e) => setNewGoalTitle(e.target.value)}
              placeholder="e.g. Audit all crates in 04_KINETIC with clippy and unit tests"
              className="w-full bg-black/60 border border-white/10 rounded px-3 py-1.5 text-xs text-white focus:border-gold outline-none"
            />
          </div>

          <div>
            <label className="text-[11px] text-white/50 block mb-1">Lead Knight</label>
            <select
              value={selectedLeadKnight}
              onChange={(e) => setSelectedLeadKnight(e.target.value)}
              className="w-full bg-black/60 border border-white/10 rounded px-3 py-1.5 text-xs text-white focus:border-gold outline-none"
            >
              <option value="MERLIN_Ω">MERLIN_Ω (Deep Reasoning)</option>
              <option value="SIR_CODEX">SIR_CODEX (Kinetic WASM)</option>
              <option value="SIR_GHOST">SIR_GHOST (Air-Gap Secrets)</option>
              <option value="SIR_SONUS">SIR_SONUS (Audio Routing)</option>
              <option value="SIR_HELIOS">SIR_HELIOS (Spire Sentinel)</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={!newGoalTitle.trim()}
              className="w-full px-4 py-2 text-xs uppercase font-bold border border-gold bg-gold/20 text-gold-royal hover:bg-gold/30 rounded transition-all shadow-[0_0_15px_rgba(212,175,55,0.3)] disabled:opacity-40"
            >
              🚀 Dispatch Goal
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
