import { Mic, Settings2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { cn } from '../lib/utils';

export function AlfredDock() {
  const [isListening, setIsListening] = useState(false);
  const mediaStream = useRef<MediaStream | null>(null);

  const startListening = async () => {
    try {
      if (!mediaStream.current) {
        mediaStream.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      }
      setIsListening(true);
      if ('vibrate' in navigator) {
        navigator.vibrate([50, 50, 50]);
      }
    } catch (err) {
      console.error('Mic access denied.', err);
    }
  };

  const stopListening = () => {
    setIsListening(false);
  };

  useEffect(() => {
    return () => {
      if (mediaStream.current) {
        mediaStream.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <section className="h-24 sm:h-28 border-t border-[#D4AF37]/40 bg-[#050510] flex items-center justify-between px-4 sm:px-8 shrink-0 relative shadow-[0_-5px_30px_rgba(75,0,130,0.3)] z-50">
      
      {/* Background ambient glow for Alfred */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#4B0082]/10 to-transparent pointer-events-none" />

      {/* Left side: Alfred Status */}
      <div className="flex-1 flex items-center justify-start gap-4 z-10">
        <div className="hidden sm:flex w-12 h-12 border border-[#D4AF37] rounded-none items-center justify-center bg-black shadow-[0_0_15px_rgba(212,175,55,0.2)]">
          {/* Wireframe Silhouette Placeholder */}
          <svg viewBox="0 0 24 24" fill="none" stroke="#D4AF37" strokeWidth="1.5" className={cn("w-8 h-8", isListening ? "animate-pulse" : "opacity-80")}>
            <path d="M12 2a4 4 0 0 0-4 4v5a4 4 0 0 0 8 0V6a4 4 0 0 0-4-4z" />
            <path d="M19 10v1a7 7 0 0 1-14 0v-1" />
            <line x1="12" y1="18" x2="12" y2="22" />
            <line x1="8" y1="22" x2="16" y2="22" />
          </svg>
        </div>
        <div className="text-[10px] sm:text-xs font-['JetBrains_Mono'] text-[#D4AF37] flex flex-col">
           <span className="font-bold tracking-widest text-[#F1EFF4]">ALFRED AUDIO DSP</span>
           <span className={cn("opacity-80", isListening ? "text-green-400" : "text-[#D4AF37]")}>
             {isListening ? '> STREAMING TO VPS STT/TTS...' : '> WASM WAKE-WORD STANDBY'}
           </span>
        </div>
      </div>
      
      {/* Center: Push-to-Talk */}
      <div className="flex-1 flex justify-center z-10">
        <button
          onPointerDown={startListening}
          onPointerUp={stopListening}
          onPointerLeave={stopListening}
          className={cn(
            "min-h-[64px] min-w-[64px] rounded-none flex items-center justify-center transition-all duration-300 shadow-[0_0_20px_rgba(212,175,55,0.2)] touch-none select-none border-2",
            isListening 
              ? "bg-[#D4AF37] text-[#050510] border-[#F1EFF4] scale-110 shadow-[0_0_40px_rgba(212,175,55,0.6)]" 
              : "bg-black text-[#D4AF37] border-[#D4AF37] hover:bg-[#D4AF37]/10"
          )}
          title="Push to Talk"
        >
          <Mic className={cn("w-7 h-7", isListening && "animate-bounce")} />
        </button>
      </div>

      {/* Right side: Waveform & Settings */}
      <div className="flex-1 flex items-center justify-end gap-4 z-10">
         <div className="flex items-end gap-1.5 h-10 px-4">
            {[...Array(8)].map((_, i) => (
              <div 
                key={i} 
                className={cn(
                  "w-1.5 bg-[#D4AF37] rounded-none",
                  isListening ? "animate-pulse" : "h-1 opacity-50"
                )}
                style={{
                  height: isListening ? `${Math.max(20, Math.random() * 100)}%` : '4px',
                  transition: 'height 0.1s ease',
                  boxShadow: isListening ? '0 0 8px rgba(212,175,55,0.8)' : 'none'
                }}
              />
            ))}
         </div>
         <button className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-none border border-[#4B0082] text-[#D4AF37] hover:bg-[#4B0082]/20 transition-colors bg-black">
           <Settings2 className="w-5 h-5" />
         </button>
      </div>
    </section>
  );
}
