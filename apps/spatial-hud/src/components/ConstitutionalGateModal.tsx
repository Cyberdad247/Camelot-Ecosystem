import React from 'react';
import { Shield, AlertTriangle, Check, X, Lock } from 'lucide-react';

interface ConstitutionalGateModalProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title?: string;
  description?: string;
}

export const ConstitutionalGateModal: React.FC<ConstitutionalGateModalProps> = ({
  isOpen,
  onConfirm,
  onCancel,
  title = "HITL Iron Gate Authorization Required",
  description = "A high-risk mutation or kinetic sovereign directive requires explicit [y/N] Human-In-The-Loop confirmation from the Operator."
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 font-mono animate-fadeIn">
      <div className="bg-neutral-900 border-2 border-red-500/60 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
        
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-red-950/80 border border-red-800/80 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-5 h-5 text-red-400 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white font-sans">{title}</h3>
            <span className="text-[11px] text-red-400 font-bold tracking-wider uppercase">
              [CONSTITUTIONAL_PILLAR_IV_ENFORCED]
            </span>
          </div>
        </div>

        <p className="text-xs text-neutral-300 font-sans leading-relaxed bg-neutral-950 p-4 rounded-xl border border-neutral-800">
          {description}
        </p>

        <div className="p-3 bg-neutral-950 rounded-xl border border-neutral-800 text-[11px] text-neutral-400 space-y-1">
          <div>• Operator: <span className="text-neutral-200">VaShawn O. Head (Vizion)</span></div>
          <div>• Node: <span className="text-neutral-200">Cleveland, OH Edge Node</span></div>
          <div>• Verdict Engine: <span className="text-emerald-400">Gideon Gate Sentinel</span></div>
        </div>

        <div className="flex items-center justify-end space-x-3 pt-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 border border-neutral-700 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all"
          >
            <X className="w-4 h-4" />
            <span>Reject [N]</span>
          </button>

          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all shadow-lg active:scale-95"
          >
            <Check className="w-4 h-4" />
            <span>Authorize [y]</span>
          </button>
        </div>

      </div>
    </div>
  );
};
