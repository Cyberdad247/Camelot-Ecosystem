import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Plus,
  X,
  BrainCircuit,
  Filter,
  Clock,
  CheckCircle2,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { CARTRIDGES, CARTRIDGE_MAP } from '@/features/cartridges/registry';
import { bifrostFetch } from '@/lib/bifrostClient';
import { runtimeConfig } from '@/config/runtime';
import { useAnyaSocket } from '@/features/brain/useAnyaSocket';
import type { CamelotTask, TaskStatus, TaskPriority, CartridgeId } from '@/types/camelot';

const STORAGE_KEY = 'camelot_tasks_v1';

function loadTasks(): CamelotTask[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
  } catch {
    return [];
  }
}

function saveTasks(tasks: CamelotTask[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function newId() {
  return `task_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

const PRIORITY_COLOR: Record<TaskPriority, string> = {
  low: 'text-slate-400 border-slate-700',
  medium: 'text-blue-400 border-blue-700',
  high: 'text-amber-400 border-amber-700',
  critical: 'text-red-400 border-red-700',
};

const STATUS_COLS: { status: TaskStatus; label: string; icon: React.ElementType; color: string }[] =
  [
    { status: 'pending', label: 'Pending', icon: Clock, color: 'text-slate-400' },
    { status: 'in_progress', label: 'In Progress', icon: Loader2, color: 'text-blue-400' },
    { status: 'completed', label: 'Completed', icon: CheckCircle2, color: 'text-emerald-400' },
  ];

interface CreateForm {
  title: string;
  description: string;
  cartridge: CartridgeId;
  priority: TaskPriority;
}

const BLANK: CreateForm = {
  title: '',
  description: '',
  cartridge: 'COGNITIVE',
  priority: 'medium',
};

export default function AlexTaskManager() {
  const [tasks, setTasks] = useState<CamelotTask[]>(loadTasks);
  const [form, setForm] = useState<CreateForm>(BLANK);
  const [showCreate, setShowCreate] = useState(false);
  const [filterCartridge, setFilterCartridge] = useState<CartridgeId | 'ALL'>('ALL');
  const [dispatching, setDispatching] = useState<string | null>(null);
  const { events } = useAnyaSocket();

  useEffect(() => {
    saveTasks(tasks);
  }, [tasks]);

  // Auto-complete tasks when WS signals dispatch done
  useEffect(() => {
    const last = events[events.length - 1];
    if (!last) return;
    if (last.event?.includes('complete') || last.event?.includes('done')) {
      setTasks((prev) =>
        prev.map((t) =>
          t.dispatch_id && last.detail?.includes(t.dispatch_id)
            ? { ...t, status: 'completed', updated_at: Date.now(), result: last.detail }
            : t,
        ),
      );
    }
  }, [events]);

  const addTask = useCallback(() => {
    if (!form.title.trim()) return;
    const cartridgeMeta = CARTRIDGE_MAP[form.cartridge];
    const task: CamelotTask = {
      id: newId(),
      title: form.title.trim(),
      description: form.description.trim(),
      status: 'pending',
      priority: form.priority,
      cartridge: form.cartridge,
      knight: cartridgeMeta.knight,
      created_at: Date.now(),
      updated_at: Date.now(),
    };
    setTasks((t) => [task, ...t]);
    setForm(BLANK);
    setShowCreate(false);
  }, [form]);

  const dispatch = useCallback(async (task: CamelotTask) => {
    setDispatching(task.id);
    setTasks((prev) =>
      prev.map((t) =>
        t.id === task.id ? { ...t, status: 'in_progress', updated_at: Date.now() } : t,
      ),
    );
    try {
      const res = await bifrostFetch(runtimeConfig.bifrost.dispatchUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: task.description || task.title,
          cartridge: task.cartridge,
          preferred_knight: task.knight,
        }),
      });
      if (res.ok) {
        const data = await res.json().catch(() => ({}));
        setTasks((prev) =>
          prev.map((t) =>
            t.id === task.id
              ? { ...t, dispatch_id: data.dispatch_id, result: data.result, updated_at: Date.now() }
              : t,
          ),
        );
      }
    } catch {
      /* bifrost dark — task stays in_progress */
    } finally {
      setDispatching(null);
    }
  }, []);

  const updateStatus = useCallback((id: string, status: TaskStatus) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status, updated_at: Date.now() } : t)),
    );
  }, []);

  const deleteTask = useCallback((id: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const filtered = useMemo(
    () =>
      filterCartridge === 'ALL' ? tasks : tasks.filter((t) => t.cartridge === filterCartridge),
    [tasks, filterCartridge],
  );

  return (
    <div className="min-h-full p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <BrainCircuit className="h-6 w-6 text-indigo-400" />
        <div>
          <h1 className="text-2xl font-black text-slate-100">SIR_ALEX — Task Manager</h1>
          <p className="text-xs text-slate-500">
            Cognitive orchestration · {tasks.length} tasks total
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {/* Filter */}
          <div className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5">
            <Filter className="h-3.5 w-3.5 text-slate-500" />
            <select
              value={filterCartridge}
              onChange={(e) => setFilterCartridge(e.target.value as CartridgeId | 'ALL')}
              className="bg-transparent text-xs text-slate-300 outline-none"
            >
              <option value="ALL">All Cartridges</option>
              {CARTRIDGES.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 text-sm font-semibold text-white transition-colors"
          >
            <Plus className="h-4 w-4" /> New Task
          </button>
        </div>
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl border border-indigo-500/30 bg-[#0a0514] p-6 shadow-2xl shadow-indigo-950/50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-black text-slate-100">New Task</h2>
              <button
                onClick={() => setShowCreate(false)}
                className="text-slate-500 hover:text-slate-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="space-y-3">
              <input
                autoFocus
                placeholder="Task title…"
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-indigo-500"
              />
              <textarea
                placeholder="Description / intent (dispatched to knight)…"
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                rows={3}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-indigo-500 resize-none"
              />
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-500 mb-1 block">Cartridge</label>
                  <select
                    value={form.cartridge}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, cartridge: e.target.value as CartridgeId }))
                    }
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-slate-300 outline-none"
                  >
                    {CARTRIDGES.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-500 mb-1 block">Priority</label>
                  <select
                    value={form.priority}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, priority: e.target.value as TaskPriority }))
                    }
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-slate-300 outline-none"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>
              <button
                onClick={addTask}
                disabled={!form.title.trim()}
                className="w-full rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 py-2 text-sm font-semibold text-white transition-colors"
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Kanban */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {STATUS_COLS.map((col) => {
          const Icon = col.icon;
          const colTasks = filtered.filter((t) => t.status === col.status);
          return (
            <div key={col.status} className="flex flex-col gap-3">
              {/* Column header */}
              <div className="flex items-center gap-2 px-1">
                <Icon className={cn('h-4 w-4', col.color)} />
                <span className="text-sm font-semibold text-slate-300">{col.label}</span>
                <span className="ml-auto rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-500">
                  {colTasks.length}
                </span>
              </div>
              {/* Cards */}
              <div className="space-y-2 min-h-[120px]">
                {colTasks.length === 0 && (
                  <div className="rounded-xl border border-dashed border-slate-800 py-6 text-center text-xs text-slate-700">
                    empty
                  </div>
                )}
                {colTasks.map((task) => {
                  const cartridge = CARTRIDGE_MAP[task.cartridge];
                  const CartIcon = cartridge.icon;
                  return (
                    <div
                      key={task.id}
                      className={cn(
                        'rounded-xl border p-3 space-y-2 transition-all',
                        cartridge.borderClass,
                        cartridge.bgClass,
                      )}
                    >
                      <div className="flex items-start gap-2">
                        <CartIcon
                          className={cn('h-3.5 w-3.5 mt-0.5 shrink-0', cartridge.textClass)}
                        />
                        <p className="flex-1 text-sm font-semibold text-slate-200 leading-tight">
                          {task.title}
                        </p>
                        <button
                          onClick={() => deleteTask(task.id)}
                          className="text-slate-700 hover:text-red-400 shrink-0"
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </div>
                      {task.description && (
                        <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                          {task.description}
                        </p>
                      )}
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className={cn(
                            'rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase',
                            PRIORITY_COLOR[task.priority],
                          )}
                        >
                          {task.priority}
                        </span>
                        <span className="text-[10px] text-slate-600">{task.knight}</span>
                        {task.result && (
                          <span className="ml-auto" title={task.result} aria-label={task.result}>
                            <AlertCircle className="h-3 w-3 text-emerald-400" />
                          </span>
                        )}
                      </div>
                      {/* Actions */}
                      <div className="flex gap-1.5">
                        {task.status === 'pending' && (
                          <button
                            onClick={() => dispatch(task)}
                            disabled={dispatching === task.id}
                            className="flex-1 rounded bg-indigo-700/50 hover:bg-indigo-600/60 px-2 py-1 text-xs font-semibold text-indigo-300 transition-colors disabled:opacity-50"
                          >
                            {dispatching === task.id ? 'Dispatching…' : 'Dispatch →'}
                          </button>
                        )}
                        {task.status === 'in_progress' && (
                          <button
                            onClick={() => updateStatus(task.id, 'completed')}
                            className="flex-1 rounded bg-emerald-900/40 hover:bg-emerald-800/50 px-2 py-1 text-xs font-semibold text-emerald-400 transition-colors"
                          >
                            Mark Done
                          </button>
                        )}
                        {task.status === 'completed' && (
                          <button
                            onClick={() => updateStatus(task.id, 'pending')}
                            className="flex-1 rounded bg-slate-800/50 hover:bg-slate-700/50 px-2 py-1 text-xs font-semibold text-slate-400 transition-colors"
                          >
                            Reopen
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
