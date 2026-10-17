import React, { useEffect, useState, useRef } from 'react';
import { cn } from '../../lib/utils';
import { Gauge } from 'lucide-react';

export interface MicroFPSMeterProps {
  targetFps?: 60 | 120;
  className?: string;
  showIcon?: boolean;
}

export const MicroFPSMeter: React.FC<MicroFPSMeterProps> = ({
  targetFps = 120,
  className,
  showIcon = true,
}) => {
  const [fps, setFps] = useState<number>(targetFps);
  const frameCount = useRef(0);
  const lastTime = useRef<number>(typeof performance !== 'undefined' ? performance.now() : Date.now());
  const rafId = useRef<number | null>(null);

  useEffect(() => {
    let active = true;

    const loop = (now: number) => {
      if (!active) return;
      frameCount.current += 1;
      const elapsed = now - lastTime.current;

      if (elapsed >= 500) {
        const calculatedFps = Math.round((frameCount.current * 1000) / elapsed);
        setFps(calculatedFps);
        frameCount.current = 0;
        lastTime.current = now;
      }

      rafId.current = requestAnimationFrame(loop);
    };

    rafId.current = requestAnimationFrame(loop);

    return () => {
      active = false;
      if (rafId.current !== null) {
        cancelAnimationFrame(rafId.current);
      }
    };
  }, []);

  const ratio = fps / (targetFps || 60);
  let fpsColor = 'text-[#00F0FF]';
  let badgeBorder = 'border-[#00F0FF]/30';

  if (ratio < 0.6) {
    fpsColor = 'text-[#DE4258]';
    badgeBorder = 'border-[#DE4258]/40';
  } else if (ratio < 0.85) {
    fpsColor = 'text-[#F59E0B]';
    badgeBorder = 'border-[#F59E0B]/30';
  } else if (fps >= 100) {
    fpsColor = 'text-[#D4AF37]';
    badgeBorder = 'border-[#D4AF37]/40';
  }

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded border bg-[#050510]/80 backdrop-blur-sm font-mono text-[10px] select-none',
        badgeBorder,
        className
      )}
      title={`Client rendering rate: ${fps} FPS (Target: ${targetFps}Hz)`}
    >
      {showIcon && <Gauge className="w-3 h-3 text-[#D4AF37]/80 shrink-0" />}
      <span className="text-[#9E9AA7]">FPS:</span>
      <span className={cn('font-bold', fpsColor)}>{fps}</span>
      <span className="text-[8px] text-[#9E9AA7]/60">/{targetFps}</span>
    </div>
  );
};
