import React, { useState, useRef } from 'react';
import {
  Smartphone,
  Wifi,
  Battery,
  Zap,
  Terminal,
  RotateCw,
  Power,
  ChevronLeft,
  Circle,
  Square,
  Volume2,
  VolumeX,
} from 'lucide-react';

interface ExcaliburDeviceProps {
  tailscaleIp?: string;
  model?: string;
  status?: 'ONLINE' | 'STANDBY' | 'DISCONNECTED';
  batteryPct?: number;
}

interface TouchPoint {
  x: number;
  y: number;
  nativeX: number;
  nativeY: number;
  id: number;
}

export default function ExcaliburCockpit({
  tailscaleIp = '100.106.246.126',
  model = 'Samsung Galaxy S26 Ultra (SM-S948U)',
  status = 'ONLINE',
  batteryPct = 94,
}: ExcaliburDeviceProps) {
  const [isStreaming, setIsStreaming] = useState(true);
  const [touchLog, setTouchLog] = useState('ADB WireGuard ready on :5555');
  const [touchPoints, setTouchPoints] = useState<TouchPoint[]>([]);
  const [activeApp, setActiveApp] = useState('Camelot-OS Mobile Shell');
  const screenRef = useRef<HTMLDivElement>(null);

  // Native S26 Ultra display dimensions
  const NATIVE_W = 1440;
  const NATIVE_H = 3120;

  const handleScreenClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!screenRef.current) return;
    const rect = screenRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    // Normalize and scale to native 1440x3120 resolution
    const normX = Math.max(0, Math.min(1, clickX / rect.width));
    const normY = Math.max(0, Math.min(1, clickY / rect.height));
    const nativeX = Math.floor(normX * NATIVE_W);
    const nativeY = Math.floor(normY * NATIVE_H);

    const newPoint: TouchPoint = {
      x: clickX,
      y: clickY,
      nativeX,
      nativeY,
      id: Date.now(),
    };

    setTouchPoints((prev) => [...prev.slice(-3), newPoint]);
    setTouchLog(`⚡ TAP: (${clickX.toFixed(0)}, ${clickY.toFixed(0)}) ➔ Native: (${nativeX}, ${nativeY}) [ADB ACK]`);

    setTimeout(() => {
      setTouchPoints((prev) => prev.filter((p) => p.id !== newPoint.id));
    }, 600);
  };

  const handleHardwareKey = (keyName: string) => {
    setTouchLog(`🔘 KEYEVENT: ${keyName} dispatched via ADB`);
    if (keyName === 'HOME') setActiveApp('Camelot-OS Mobile Shell');
    if (keyName === 'APP_SWITCH') setActiveApp('Task Switcher (3 Apps Active)');
  };

  return (
    <div className="border border-camelot-violet/40 bg-obsidian-smoke/70 p-4 rounded backdrop-blur font-mono text-xs">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 border-b border-gray-800 pb-2">
        <div className="flex items-center gap-2">
          <Smartphone className="h-4 w-4 text-camelot-violet animate-pulse" />
          <h2 className="text-camelot-violet font-semibold tracking-wider uppercase text-xs">
            Excalibur 120Hz Mobile Glass
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/60 text-camelot-cyan border border-camelot-cyan/30">
            Adreno 840
          </span>
          <span className="px-2 py-0.5 text-[10px] bg-green-500/10 text-green-400 border border-green-500/30 rounded-sm">
            {status}
          </span>
        </div>
      </div>

      {/* Hardware Telemetry Bar */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="bg-black/50 border border-gray-800 p-1.5 rounded">
          <div className="text-[9px] text-gray-500">REFRESH</div>
          <div className="text-xs font-bold text-yellow-400 flex items-center justify-center gap-1">
            <Zap className="h-3 w-3 text-yellow-400" /> 120Hz
          </div>
        </div>
        <div className="bg-black/50 border border-gray-800 p-1.5 rounded">
          <div className="text-[9px] text-gray-500">BATTERY</div>
          <div className="text-xs font-bold text-green-400 flex items-center justify-center gap-1">
            <Battery className="h-3 w-3 text-green-400" /> {batteryPct}%
          </div>
        </div>
        <div className="bg-black/50 border border-gray-800 p-1.5 rounded">
          <div className="text-[9px] text-gray-500">MESH IP</div>
          <div className="text-[10px] font-bold text-camelot-cyan truncate">
            {tailscaleIp.replace('100.106.', '...')}
          </div>
        </div>
      </div>

      {/* Interactive Mobile Screen Mirror Viewport */}
      <div className="relative mb-3 flex flex-col items-center">
        <div
          ref={screenRef}
          onClick={handleScreenClick}
          className="relative w-full h-52 bg-gradient-to-b from-gray-950 via-black to-obsidian-void border-2 border-camelot-violet/50 rounded-lg overflow-hidden cursor-crosshair shadow-lg shadow-camelot-violet/10 select-none flex flex-col justify-between p-2"
        >
          {/* Mobile Status Bar */}
          <div className="flex justify-between items-center text-[9px] text-gray-400 border-b border-gray-800/80 pb-1">
            <span>12:00</span>
            <div className="w-12 h-2 rounded-full bg-black border border-gray-700 mx-auto" />
            <div className="flex items-center gap-1 text-[8px]">
              <Wifi className="h-2.5 w-2.5 text-camelot-cyan" />
              <span>5G</span>
              <span>{batteryPct}%</span>
            </div>
          </div>

          {/* Screen Content Mockup / Live Stream Canvas */}
          <div className="flex-1 flex flex-col items-center justify-center text-center px-2 py-1">
            <div className="text-xs font-bold text-camelot-gold mb-1">{activeApp}</div>
            <div className="text-[10px] text-gray-500 mb-2">Snapdragon 8 Elite Direct KGSL</div>
            <div className="grid grid-cols-3 gap-1.5 w-full max-w-[200px]">
              {['Telemetry', 'Shell', 'Camera', 'Sensors', 'Mesh', 'Termux'].map((app) => (
                <div
                  key={app}
                  onClick={(e) => {
                    e.stopPropagation();
                    setActiveApp(app);
                    setTouchLog(`📱 Launched App: ${app}`);
                  }}
                  className="p-1 bg-black/60 border border-camelot-violet/30 hover:border-camelot-gold/60 rounded text-[9px] text-gray-300 transition hover:scale-105 cursor-pointer"
                >
                  {app}
                </div>
              ))}
            </div>
          </div>

          {/* Animated Touch Visualizer */}
          {touchPoints.map((pt) => (
            <div
              key={pt.id}
              className="absolute w-6 h-6 rounded-full border-2 border-camelot-gold bg-camelot-gold/30 pointer-events-none transform -translate-x-1/2 -translate-y-1/2 animate-ping"
              style={{ left: pt.x, top: pt.y }}
            />
          ))}

          {/* Bottom Gesture Bar */}
          <div className="w-20 h-1 bg-gray-600 rounded-full mx-auto" />
        </div>
      </div>

      {/* Android Hardware Navigation Keypad */}
      <div className="flex items-center justify-between gap-1 mb-2">
        <button
          onClick={() => handleHardwareKey('BACK')}
          title="Back"
          className="flex-1 py-1 bg-black/50 hover:bg-camelot-violet/20 border border-gray-800 hover:border-camelot-violet/40 rounded flex items-center justify-center transition"
        >
          <ChevronLeft className="h-3.5 w-3.5 text-gray-300" />
        </button>
        <button
          onClick={() => handleHardwareKey('HOME')}
          title="Home"
          className="flex-1 py-1 bg-black/50 hover:bg-camelot-gold/20 border border-gray-800 hover:border-camelot-gold/40 rounded flex items-center justify-center transition"
        >
          <Circle className="h-3 w-3 text-camelot-gold" />
        </button>
        <button
          onClick={() => handleHardwareKey('APP_SWITCH')}
          title="Recent Apps"
          className="flex-1 py-1 bg-black/50 hover:bg-camelot-cyan/20 border border-gray-800 hover:border-camelot-cyan/40 rounded flex items-center justify-center transition"
        >
          <Square className="h-3 w-3 text-camelot-cyan" />
        </button>
        <button
          onClick={() => handleHardwareKey('POWER')}
          title="Power / Screen Toggle"
          className="py-1 px-2.5 bg-black/50 hover:bg-red-500/20 border border-gray-800 hover:border-red-500/40 rounded flex items-center justify-center transition"
        >
          <Power className="h-3 w-3 text-red-400" />
        </button>
      </div>

      {/* Real-time Digitizer Log */}
      <div className="text-[10px] text-gray-400 truncate bg-black/40 p-1.5 rounded border border-gray-800">
        <span className="text-camelot-violet">&gt;</span> {touchLog}
      </div>
    </div>
  );
}
