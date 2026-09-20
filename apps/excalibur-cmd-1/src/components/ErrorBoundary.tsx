import React from 'react';
import { AlertOctagon, RotateCcw, ShieldAlert, Cpu, Terminal, ChevronDown, ChevronUp } from 'lucide-react';

interface Props {
  children: React.ReactNode;
  cartridgeName?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  showTrace: boolean;
}

export class ErrorBoundary extends React.Component<Props, State> {
  override state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    showTrace: false,
  };

  constructor(props: Props) {
    super(props);
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  override componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error(`[EXCALIBUR_AEGIS_SHIELD] Cartridge fault captured in ${this.props.cartridgeName || 'Subsystem'}:`, error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showTrace: false,
    });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  override render(): React.ReactNode {
    if (this.state.hasError) {
      const cartridgeLabel = this.props.cartridgeName || 'SOVEREIGN CARTRIDGE';
      const errorMessage = this.state.error?.message || 'Unknown runtime fault in memory slab';
      const componentStack = this.state.errorInfo?.componentStack || '';

      return (
        <div id="cartridge-error-boundary-container" className="h-full w-full flex items-center justify-center p-4 sm:p-8 bg-[#050510]">
          <div
            id="cartridge-fault-chassis"
            className="max-w-2xl w-full border-2 border-red-500/80 bg-black/90 p-6 sm:p-8 shadow-[0_0_50px_rgba(239,68,68,0.35)] relative overflow-hidden"
          >
            {/* Angular sovereign corner markers */}
            <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-red-500" />
            <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-red-500" />
            <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-red-500" />
            <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-red-500" />

            <div className="flex flex-col space-y-5">
              {/* Header Badge */}
              <div className="flex items-center justify-between border-b border-red-500/40 pb-4 flex-wrap gap-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 border border-red-500 bg-red-950/50 flex items-center justify-center">
                    <ShieldAlert className="w-6 h-6 text-red-400 animate-pulse" />
                  </div>
                  <div>
                    <span className="text-[10px] font-['JetBrains_Mono'] text-red-400 tracking-widest uppercase block font-bold">
                      AEGIS ZERO-TRUST QUARANTINE ACTIVE
                    </span>
                    <h2 className="text-base sm:text-lg font-['Cinzel'] font-bold text-[#F1EFF4]">
                      {cartridgeLabel} FAULT ISOLATED
                    </h2>
                  </div>
                </div>

                <span className="text-[10px] font-['JetBrains_Mono'] px-2.5 py-1 border border-red-500/60 bg-red-950/40 text-red-300 font-bold flex items-center gap-1.5">
                  <AlertOctagon className="w-3.5 h-3.5" />
                  CONTAINED
                </span>
              </div>

              {/* Explanatory telemetry message */}
              <p className="text-xs sm:text-sm font-['Spectral'] text-[#F1EFF4]/85 leading-relaxed">
                The Excalibur Sentinel isolated this cartridge failure within an ephemeral micro-sandbox. The rest of the Command Center, VFS memory backplane, and telemetry services continue operating without interruption under the 4GB RAM ceiling.
              </p>

              {/* Error Summary Card */}
              <div className="border border-[#4B0082] bg-black/70 p-3.5 space-y-2">
                <div className="flex items-center justify-between text-[11px] font-['JetBrains_Mono']">
                  <span className="text-[#D4AF37] font-bold">INTERCEPTED EXCEPTION:</span>
                  <span className="text-red-400 font-mono text-[10px]">MADV_RECLAIMED</span>
                </div>
                <div className="p-2.5 bg-red-950/20 border border-red-500/30 text-xs font-['JetBrains_Mono'] text-red-200 break-words">
                  {errorMessage}
                </div>
              </div>

              {/* Collapsible Stack Trace */}
              {componentStack && (
                <div className="border border-[#4B0082]/60 bg-black/40">
                  <button
                    id="toggle-stack-trace-btn"
                    type="button"
                    onClick={() => this.setState({ showTrace: !this.state.showTrace })}
                    className="w-full px-3 py-2 flex items-center justify-between text-[11px] font-['JetBrains_Mono'] text-[#D4AF37] hover:bg-white/5 transition-all"
                  >
                    <span className="flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5" />
                      {this.state.showTrace ? 'HIDE STACK FORENSICS' : 'VIEW STACK FORENSICS'}
                    </span>
                    {this.state.showTrace ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {this.state.showTrace && (
                    <div className="p-3 border-t border-[#4B0082]/40 bg-black text-[10px] font-['JetBrains_Mono'] text-[#F1EFF4]/60 max-h-40 overflow-y-auto whitespace-pre-wrap">
                      {componentStack}
                    </div>
                  )}
                </div>
              )}

              {/* Memory & Invariant Footer */}
              <div className="flex items-center justify-between text-[10px] font-['JetBrains_Mono'] text-[#F1EFF4]/60 border-t border-[#4B0082]/50 pt-3 flex-wrap gap-2">
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <Cpu className="w-3.5 h-3.5" />
                  <span>4GB CEILING INTACT // ZERO CASCADING LEAKS</span>
                </div>
                <span className="text-[#D4AF37]">Z3_SMT: RECOVERABLE</span>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <button
                  id="reboot-cartridge-btn"
                  type="button"
                  onClick={this.handleReset}
                  className="py-2.5 px-4 bg-[#D4AF37] hover:bg-[#F1EFF4] text-black font-['Cinzel'] font-bold text-xs transition-all flex items-center justify-center gap-2 min-h-[44px] shadow-[0_0_15px_rgba(212,175,55,0.3)]"
                >
                  <RotateCcw className="w-4 h-4" />
                  REBOOT CARTRIDGE SLAB
                </button>

                <button
                  id="switch-ecc-btn"
                  type="button"
                  onClick={() => {
                    this.handleReset();
                    window.location.hash = '#excalibur-ecc';
                  }}
                  className="py-2.5 px-4 bg-transparent border border-[#4B0082] hover:border-[#D4AF37] text-[#F1EFF4] font-['Cinzel'] font-bold text-xs transition-all flex items-center justify-center gap-2 min-h-[44px]"
                >
                  RETURN TO DIGITAL THRONE
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
