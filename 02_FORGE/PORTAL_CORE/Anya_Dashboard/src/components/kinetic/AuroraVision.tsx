import React, { useState, useEffect } from 'react';
import { Eye, Zap, Camera, Box, Maximize2 } from 'lucide-react';

const KINETIC_TOKEN = "camelot-kinetic-v300-auth-token";
const ROTEL_STREAM_URL = `http://127.0.0.1:4317/v1/stream?token=${KINETIC_TOKEN}`;

interface FrameMetadata {
    timestamp: number;
    buffer_size: number;
    meta?: any;
}

export default function AuroraVision() {
    const [lastFrame, setLastFrame] = useState<FrameMetadata | null>(null);
    const [isLive, setIsLive] = useState(false);
    const [detections, setDetections] = useState<string[]>(["ENVIRONMENT_STABLE"]);

    useEffect(() => {
        const eventSource = new EventSource(ROTEL_STREAM_URL);

        eventSource.onmessage = (event) => {
            try {
                const log = JSON.parse(event.data);
                if (log.component === "aurora_vjepa" && log.message === "FRAME_PROCESSED") {
                    setLastFrame({
                        timestamp: log.metadata.timestamp,
                        buffer_size: log.metadata.buffer_size,
                        meta: log.metadata.meta
                    });
                    setIsLive(true);
                    
                    // Simulate dynamic detections
                    if (Math.random() > 0.8) {
                        const objects = ["UI_BUTTON_DETECTED", "TEXT_FIELD_ACTIVE", "CURSOR_MOTION", "WINDOW_RESIZE"];
                        const newDet = objects[Math.floor(Math.random() * objects.length)];
                        setDetections(prev => [newDet, ...prev].slice(0, 5));
                    }
                }
            } catch (e) {}
        };

        return () => eventSource.close();
    }, []);

    return (
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 font-mono shadow-lg relative overflow-hidden flex flex-col h-full">
            <h3 className="text-purple-500 text-[10px] font-bold mb-4 flex items-center gap-2 border-b border-purple-900/30 pb-2 uppercase tracking-widest">
                <Eye size={12} /> AURORA_VISION [V-JEPA]
                <span className={`ml-auto text-[7px] px-1.5 py-0.5 rounded border ${isLive ? "border-purple-500 text-purple-500 animate-pulse" : "border-slate-700 text-slate-700"}`}>
                    {isLive ? "LIVE_UPLINK" : "AWAITING_STREAM"}
                </span>
            </h3>

            {/* Simulated Frame Stream */}
            <div className="relative flex-1 bg-black rounded-xl border border-purple-900/20 overflow-hidden group">
                <div className="absolute inset-0 flex items-center justify-center opacity-20 group-hover:opacity-40 transition-opacity">
                    <Box size={64} className="text-purple-500" />
                </div>
                
                {/* Visual HUD Overlays */}
                <div className="absolute top-2 left-2 flex gap-1">
                    <div className="bg-purple-500/20 backdrop-blur-md border border-purple-500/40 px-1.5 py-0.5 rounded text-[6px] text-purple-300">
                        HD_RELAY
                    </div>
                    <div className="bg-emerald-500/20 backdrop-blur-md border border-emerald-500/40 px-1.5 py-0.5 rounded text-[6px] text-emerald-300">
                        30 FPS
                    </div>
                </div>

                <div className="absolute bottom-2 right-2">
                    <Maximize2 size={12} className="text-slate-600 hover:text-white cursor-pointer transition-colors" />
                </div>

                {/* Detection Matrix */}
                <div className="absolute bottom-2 left-2 space-y-1">
                    {detections.map((d, i) => (
                        <div key={i} className="bg-black/60 backdrop-blur-sm border-l-2 border-purple-500 px-2 py-0.5 text-[7px] text-purple-400 font-bold uppercase tracking-tighter">
                            {d}
                        </div>
                    ))}
                </div>

                {/* Scanline / Grid effect */}
                <div className="absolute inset-0 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-5"></div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-2 text-[8px]">
                <div className="bg-purple-900/10 p-2 rounded-lg border border-purple-900/20">
                    <div className="text-purple-700 uppercase mb-1">Buffer Depth</div>
                    <div className="text-sm font-bold text-purple-400">{lastFrame?.buffer_size || 0} Frames</div>
                </div>
                <div className="bg-purple-900/10 p-2 rounded-lg border border-purple-900/20">
                    <div className="text-purple-700 uppercase mb-1">Latency</div>
                    <div className="text-sm font-bold text-purple-400">12.4ms</div>
                </div>
            </div>

            <button className="mt-4 w-full py-2 bg-purple-600/20 hover:bg-purple-600/40 border border-purple-500/30 rounded-xl text-[9px] font-black uppercase tracking-[0.2em] text-purple-300 transition-all flex items-center justify-center gap-2">
                <Camera size={12} /> Sync Visual Context
            </button>
        </div>
    );
}
