// SPDX-License-Identifier: MIT

'use client';

import { useEffect, useState } from 'react';
import { subscribe } from '../../lib/operator_console/operator-events';
import { fetchSnapshot, OperatorApiError } from '../../lib/operator_console/operator-api';
import type { OperatorTaskSnapshot } from '../../lib/operator_console/schemas';
import { ageLabel } from '../../lib/operator_console/formatters';
import { OperatorConsoleHeader } from './OperatorConsoleHeader';
import { StaleEvidenceNotice } from './StaleEvidenceNotice';
import { EmptyEvidenceState } from './EmptyEvidenceState';
// Panels (Tasks 8-10) fill these slots:
import { IntentPanel } from './IntentPanel';
import { ApprovalPanel } from './ApprovalPanel';
import { TaskGraphPanel } from './TaskGraphPanel';
import { DiffStreamPanel } from './DiffStreamPanel';
import { TestsPanel } from './TestsPanel';
import { ReceiptsPanel } from './ReceiptsPanel';

export function OperatorConsole({ taskId }: { taskId: string }) {
  const [snapshot, setSnapshot] = useState<OperatorTaskSnapshot | null>(null);
  const [lastVerifiedAt, setLastVerifiedAt] = useState<string | null>(null);
  const [bifrostDown, setBifrostDown] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchSnapshot(taskId)
      .then((s) => {
        if (mounted) {
          setSnapshot(s);
          setLastVerifiedAt(s.generatedAt);
        }
      })
      .catch((err) => {
        if (mounted && err instanceof OperatorApiError && err.status === 401) {
          // Session required — leave panel in UNAVAILABLE state.
        }
        if (mounted) setBifrostDown(true);
      });
    const unsubscribe = subscribe(taskId, (s) => {
      if (mounted) {
        setSnapshot(s);
        setLastVerifiedAt(s.generatedAt);
        setBifrostDown(false);
      }
    });
    return () => {
      mounted = false;
      unsubscribe();
    };
  }, [taskId]);

  const integrity = snapshot?.integrity ?? 'unavailable';
  const integrityFailed = integrity === 'integrity_failed';

  return (
    <main className="min-h-screen bg-obsidian px-6 py-8 font-mono">
      <OperatorConsoleHeader taskId={taskId} integrity={integrity} />
      {bifrostDown && (
        <StaleEvidenceNotice ageLabel={lastVerifiedAt ? ageLabel(lastVerifiedAt) : 'never'} />
      )}
      {integrityFailed && (
        <div role="alert" className="mt-4 border border-red-400/60 bg-red-400/5 p-3">
          <p className="font-mono text-[11px] uppercase tracking-widest text-red-300">
            INTEGRITY FAILED — evidence cannot satisfy any promotion gate.
          </p>
          <p className="mt-1 text-[11px] text-white/50">
            The affected record is preserved for investigation. Approval and promotion paths are
            disabled.
          </p>
        </div>
      )}
      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <section className="rounded-sm border border-white/10 p-4" aria-label="Intent">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Intent</h2>
          {snapshot ? (
            <IntentPanel intent={snapshot.intent} />
          ) : (
            <EmptyEvidenceState panel="Intent" />
          )}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Approval">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Approval</h2>
          {snapshot ? (
            <ApprovalPanel
              taskId={taskId}
              approval={snapshot.approval}
              forceDisabled={bifrostDown || integrityFailed}
            />
          ) : (
            <EmptyEvidenceState panel="Approval" />
          )}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Task Graph">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Task Graph</h2>
          {snapshot ? (
            <TaskGraphPanel nodes={snapshot.taskGraph} />
          ) : (
            <EmptyEvidenceState panel="Task Graph" />
          )}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Diffs">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Diffs</h2>
          {snapshot ? (
            <DiffStreamPanel diffs={snapshot.diffs} />
          ) : (
            <EmptyEvidenceState panel="Diffs" />
          )}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Tests">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Tests</h2>
          {snapshot ? <TestsPanel tests={snapshot.tests} /> : <EmptyEvidenceState panel="Tests" />}
        </section>
        <section className="rounded-sm border border-white/10 p-4" aria-label="Receipts">
          <h2 className="mb-3 text-xs uppercase tracking-widest text-gold-light">Receipts</h2>
          {snapshot ? (
            <ReceiptsPanel receipts={snapshot.receipts} taskId={taskId} />
          ) : (
            <EmptyEvidenceState panel="Receipts" />
          )}
        </section>
      </div>
    </main>
  );
}
