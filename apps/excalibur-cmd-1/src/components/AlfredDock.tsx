import { Mic, Settings2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { cn } from '../lib/utils';
import { triggerHaptic } from '../lib/haptics';

export function AlfredDock() {
  const [isListening, setIsListening] = useState(false);
  const mediaStream = useRef<MediaStream | null>(null);

  const startListening = async () => {
    try {
      if (!mediaStream.current) {
        mediaStream.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      }
      setIsListening(true);
      triggerHaptic('success');
    } catch (err) {
      console.error('Mic access denied.', err);
      triggerHaptic('error');
    }
  };

  const stopListening = () => {
    if (isListening) {
      setIsListening(false);
      triggerHaptic('tick');
    }
  };

  useEffect(() => {
    return () => {
      if (mediaStream.current) {
        mediaStream.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <aside
      role="complementary"
      aria-label="Alfred Audio Controller"
      className="h-20 sm:h-24 border-t border-[#D4AF37]/40 bg-[#050510]/95 backdrop-blur-xl flex items-center justify-between px-3 sm:px-8 shrink-0 relative shadow-[0_-5px_30px_rgba(75,0,130,0.3)] z-50 select-none"
    >
      {/* Background ambient glow for Alfred */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#4B0082]/15 to-transparent pointer-events-none" />

      {/* Left side: Alfred Status */}
      <div className="flex-1 flex items-center justify-start gap-3 sm:gap-4 z-10">
        <div className="w-10 h-10 sm:w-11 sm:h-11 border border-[#D4AF37] rounded-lg flex items-center justify-center bg-black/60 shadow-[0_0_15px_rgba(212,175,55,0.25)]">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="#D4AF37"
            strokeWidth="1.5"
            className={cn("w-6 h-6", isListening ? "animate-pulse" : "opacity-85")}
            aria-hidden="true"
          >
            <path d="M12 2a4 4 0 0 0-4 4v5a4 4 0 0 0 8 0V6a4 4 0 0 0-4-4z" />
            <path d="M19 10v1a7 7 0 0 1-14 0v-1" />
            <line x1="12" y1="18" x2="12" y2="22" />
            <line x1="8" y1="22" x2="16" y2="22" />
          </svg>
        </div>
        <div className="text-[10px] sm:text-xs font-mono text-[#D4AF37] flex flex-col">
          <span className="font-bold tracking-widest text-[#F1EFF4]">ALFRED AUDIO DSP</span>
          <span className={cn("opacity-90 font-medium", isListening ? "text-[#10B981]" : "text-[#D4AF37]/80")}>
            {isListening ? '> STREAMING TO VPS STT/TTS...' : '> WASM WAKE-WORD STANDBY'}
          </span>
        </div>
      </div>

      {/* Center: Push-to-Talk Button (Thumb Zone Anchor) */}
      <div className="flex-1 flex justify-center z-10">
        <button
          type="button"
          onPointerDown={startListening}
          onPointerUp={stopListening}
          onPointerLeave={stopListening}
          aria-label={isListening ? "Release to stop voice transmission" : "Push and hold to talk to Alfred"}
          aria-pressed={isListening}
          className={cn(
            "min-h-[56px] min-w-[56px] sm:min-h-[64px] sm:min-w-[64px] rounded-xl flex items-center justify-center transition-all duration-200 shadow-[0_0_20px_rgba(212,175,55,0.25)] touch-none cursor-pointer border-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D4AF37]",
            isListening 
              ? "bg-[#D4AF37] text-[#050510] border-[#F1EFF4] scale-105 shadow-[0_0_40px_rgba(212,175,55,0.7)]" 
              : "bg-black/80 text-[#D4AF37] border-[#D4AF37] hover:bg-[#D4AF37]/15 active:scale-95"
          )}
          title="Push and hold to talk"
        >
          <Mic className={cn("w-6 h-6 sm:w-7 sm:h-7", isListening && "animate-pulse")} />
        </button>
      </div>

      {/* Right side: Waveform & Settings */}
      <div className="flex-1 flex items-center justify-end gap-3 sm:gap-4 z-10">
        <div className="flex items-end gap-1 sm:gap-1.5 h-8 px-2 sm:px-4" aria-hidden="true">
          {[...Array(8)].map((_, i) => (
            <div 
              key={i} 
              className={cn(
                "w-1 sm:w-1.5 bg-[#D4AF37] rounded-full transition-all duration-100",
                isListening ? "animate-pulse opacity-100" : "h-1 opacity-40"
              )}
              style={{
                height: isListening ? `${Math.max(25, ((i * 17 + 31) % 80) + 20)}%` : '4px',
                boxShadow: isListening ? '0 0 8px rgba(212,175,55,0.8)' : 'none'
              }}
            />
          ))}
        </div>
        <button
          type="button"
          aria-label="Audio DSP Configuration Settings"
          className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg border border-[#4B0082] text-[#D4AF37] hover:bg-[#4B0082]/30 transition-colors bg-black/60 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D4AF37]"
        >
          <Settings2 className="w-5 h-5" />
        </button>
      </div>
    </aside>
  );
}
