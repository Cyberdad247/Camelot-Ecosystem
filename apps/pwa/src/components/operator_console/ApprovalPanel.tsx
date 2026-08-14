// SPDX-License-Identifier: MIT

'use client';

export function ApprovalPanel({ approval }: { approval: Record<string, unknown>; taskId: string }) {
  return (
    <p className="text-xs text-white/50">Approval state: {JSON.stringify(approval.state ?? 'unknown')}</p>
  );
}
