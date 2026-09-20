import { useState } from 'react';
import { QrCode, Scan, CheckCircle2, RefreshCw, Smartphone } from 'lucide-react';
import { GlassPanel } from '../ui/GlassPanel';

interface Props {
  onScanned?: (signature: string) => void;
}

export function QRScanner({ onScanned }: Props) {
  const [scanning, setScanning] = useState(false);
  const [scannedNonce, setScannedNonce] = useState<string | null>(null);

  const simulateScan = () => {
    setScanning(true);
    setTimeout(() => {
      const generatedSig = `KNOX_S26_0x${Math.random().toString(16).substring(2, 10).toUpperCase()}`;
      setScannedNonce(generatedSig);
      setScanning(false);
      if (onScanned) {
        onScanned(generatedSig);
      }
    }, 1000);
  };

  return (
    <GlassPanel glow="gold" className="space-y-4 text-center">
      <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-2">
        <div className="flex items-center gap-2 text-xs font-['Cinzel'] font-bold text-[#D4AF37]">
          <Smartphone className="w-4 h-4" />
          <span>S26 ULTRA HARDWARE ATTESTATION</span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 border border-emerald-500/50 text-emerald-400 bg-emerald-950/30">
          KNOX PRF 2026
        </span>
      </div>

      <div className="relative mx-auto w-44 h-44 border-2 border-dashed border-[#D4AF37]/60 bg-black/60 rounded-xl p-3 flex flex-col items-center justify-center overflow-hidden">
        {/* Animated scanline */}
        {scanning && (
          <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent animate-bounce" />
        )}

        <div className="grid grid-cols-6 gap-1 p-2 bg-white rounded-lg">
          {Array.from({ length: 36 }).map((_, i) => (
            <div
              key={i}
              className={`w-4 h-4 ${
                (i % 7 === 0 || i % 5 === 0 || i < 6 || i > 30 || i % 6 === 0)
                  ? 'bg-black'
                  : i % 2 === 0
                  ? 'bg-[#4B0082]'
                  : 'bg-black/90'
              } rounded-[1px]`}
            />
          ))}
        </div>

        <div className="mt-2 text-[9px] font-mono text-[#F1EFF4]/70">
          ED25519 QR CHALLENGE NONCE
        </div>
      </div>

      {scannedNonce ? (
        <div className="p-2 border border-emerald-500/60 bg-emerald-950/20 text-xs font-mono text-emerald-300 flex items-center justify-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>SEALED: {scannedNonce}</span>
        </div>
      ) : (
        <button
          id="initiate-qr-scan-btn"
          type="button"
          onClick={simulateScan}
          disabled={scanning}
          className="w-full py-2.5 px-4 bg-[#D4AF37]/20 border border-[#D4AF37] hover:bg-[#D4AF37] hover:text-black text-[#D4AF37] text-xs font-['Cinzel'] font-bold rounded-lg transition-all flex items-center justify-center gap-2"
        >
          {scanning ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>HANDSHAKING ENCLAVE...</span>
            </>
          ) : (
            <>
              <Scan className="w-3.5 h-3.5" />
              <span>PAIR S26 ULTRA QR</span>
            </>
          )}
        </button>
      )}
    </GlassPanel>
  );
}
