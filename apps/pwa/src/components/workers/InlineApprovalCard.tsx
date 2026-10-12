'use client';

// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import React, { useState } from 'react';

export interface PermissionRequestUI {
  request_id: string;
  worker_id: string;
  knight_id: string;
  operation_type: string;
  target: string;
  summary: string;
  details: Record<string, unknown>;
  risk_tier: string;
  status: string;
  created_at: string;
}

interface InlineApprovalCardProps {
  request: PermissionRequestUI;
  onApprove: (requestId: string) => void;
  onDeny: (requestId: string) => void;
}

export const InlineApprovalCard: React.FC<InlineApprovalCardProps> = ({
  request,
  onApprove,
  onDeny,
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const isCritical = request.risk_tier === 'R4_CRITICAL';
  const isHigh = request.risk_tier === 'R3_HIGH';

  const riskBadgeClass = isCritical
    ? 'border-red-500/50 bg-red-500/10 text-red-400'
    : isHigh
    ? 'border-amber-500/50 bg-amber-500/10 text-amber-300'
    : 'border-blue-500/50 bg-blue-500/10 text-blue-300';

  const handleApprove = () => {
    setIsProcessing(true);
    onApprove(request.request_id);
  };

  const handleDeny = () => {
    setIsProcessing(true);
    onDeny(request.request_id);
  };

  return (
    <div className="border border-gold/40 bg-smoke-900/90 rounded p-4 font-mono shadow-lg transition-all hover:border-gold">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gold/20 pb-2 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-gold font-bold">🛡️ HITL APPROVAL REQUIRED</span>
          <span className="text-xs px-2 py-0.5 rounded border border-gold/30 bg-gold/10 text-gold-royal">
            {request.request_id}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs uppercase px-2 py-0.5 rounded border font-bold ${riskBadgeClass}`}>
            {request.risk_tier}
          </span>
          <span className="text-xs text-white/50">{request.operation_type}</span>
        </div>
      </div>

      <div className="text-sm text-white/90 mb-2">
        <div className="font-semibold text-white mb-1">{request.summary}</div>
        <div className="text-xs text-white/60 truncate">Target: {request.target}</div>
      </div>

      {expanded && (
        <div className="bg-black/50 border border-white/10 rounded p-3 mb-3 text-xs space-y-1">
          <div className="text-gold/80 font-bold">Request Context:</div>
          <div>Worker ID: <span className="text-white/80">{request.worker_id}</span></div>
          <div>Knight ID: <span className="text-white/80">{request.knight_id}</span></div>
          <div>Created: <span className="text-white/80">{request.created_at}</span></div>
          {Object.keys(request.details).length > 0 && (
            <div className="mt-2">
              <span className="text-gold/80">Details Payload:</span>
              <pre className="mt-1 p-2 bg-black/60 rounded overflow-x-auto text-[11px] text-white/70">
                {JSON.stringify(request.details, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-gold/70 hover:text-gold underline"
        >
          {expanded ? '▲ Hide Payload' : '▼ Inspect Context & Diff'}
        </button>

        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={isProcessing}
            onClick={handleDeny}
            className="px-3 py-1 text-xs uppercase font-bold border border-red-500/50 bg-red-950/40 text-red-300 hover:bg-red-900/60 rounded transition-all disabled:opacity-50"
          >
            Deny
          </button>
          <button
            type="button"
            disabled={isProcessing}
            onClick={handleApprove}
            className="px-4 py-1 text-xs uppercase font-bold border border-gold bg-gold/20 text-gold-royal hover:bg-gold/30 rounded transition-all shadow-[0_0_10px_rgba(212,175,55,0.3)] disabled:opacity-50"
          >
            Allow Once
          </button>
        </div>
      </div>
    </div>
  );
};
