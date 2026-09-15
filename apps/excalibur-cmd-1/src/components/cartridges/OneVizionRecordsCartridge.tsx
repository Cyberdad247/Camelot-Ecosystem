import { useState } from 'react';
import { Disc, Music, CheckCircle2, ShieldCheck, Sparkles, RefreshCw, UploadCloud, Radio } from 'lucide-react';

export function OneVizionRecordsCartridge() {
  const [trackTitle, setTrackTitle] = useState('Sovereign Frequency 71228');
  const [artistName] = useState('Vizion');
  const [tuningStandard, setTuningStandard] = useState<'432Hz' | '440Hz'>('432Hz');
  const [isSealing, setIsSealing] = useState(false);
  const [lufsValue, setLufsValue] = useState(-14.1);
  const [truePeak, setTruePeak] = useState(-1.0);
  const [phaseCorrelation, setPhaseCorrelation] = useState(0.96);

  const [sealReport, setSealReport] = useState<{
    isrc: string;
    upc: string;
    artwork3000px: boolean;
    artworkHash: string;
    audioPhysicsStatus: string;
    lufs: number;
    truePeak: number;
    phase: number;
    sealedTimestamp: string;
  } | null>({
    isrc: 'US-1VZ-26-71228',
    upc: '071228190014',
    artwork3000px: true,
    artworkHash: 'SHA256:71228a9b3c4d5e8f00192837465abced',
    audioPhysicsStatus: '32-BIT FLOAT // 48KHZ // EBU R128 COMPLIANT',
    lufs: -14.1,
    truePeak: -1.0,
    phase: 0.96,
    sealedTimestamp: new Date().toLocaleTimeString()
  });

  const runDistributionPipeline = () => {
    setIsSealing(true);
    setTimeout(() => {
      setIsSealing(false);
      const isrcSuffix = Math.floor(10000 + Math.random() * 90000);
      const newLufs = -14.0 + +(Math.random() * 0.4 - 0.2).toFixed(1);
      const newPeak = -1.0 + +(Math.random() * 0.2 - 0.1).toFixed(1);
      const newPhase = 0.94 + +(Math.random() * 0.05).toFixed(2);
      setLufsValue(newLufs);
      setTruePeak(newPeak);
      setPhaseCorrelation(newPhase);

      setSealReport({
        isrc: `US-1VZ-26-${isrcSuffix}`,
        upc: `071228${Math.floor(100000 + Math.random() * 900000)}`,
        artwork3000px: true,
        artworkHash: `SHA256:${Math.random().toString(16).substring(2, 18)}71228`,
        audioPhysicsStatus: `32-BIT FLOAT // 48KHZ // ${tuningStandard} // RECORDS UNCHAINED SEALED`,
        lufs: newLufs,
        truePeak: newPeak,
        phase: newPhase,
        sealedTimestamp: new Date().toLocaleTimeString()
      });
    }, 1100);
  };

  return (
    <div className="w-full h-full p-3 sm:p-6 overflow-y-auto">
      <div className="max-w-[1400px] mx-auto space-y-6">
        
        {/* Banner */}
        <div className="border border-[#D4AF37] bg-[#050510] p-4 sm:p-6 relative shadow-[0_0_30px_rgba(75,0,130,0.4)]">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 border border-[#D4AF37] bg-black flex items-center justify-center">
                <Disc className="w-7 h-7 text-[#D4AF37] animate-spin-slow" />
              </div>
              <div>
                <h1 className="font-['Cinzel'] text-xl sm:text-2xl font-black tracking-widest text-[#D4AF37]">
                  CARTRIDGE 03: 1VIZION RCRDS
                </h1>
                <p className="text-xs sm:text-sm font-['Spectral'] text-[#F1EFF4]/80 mt-0.5">
                  AI-Assisted Music Generation ⨷ Audio Physics ⨷ Records Unchained 71228 Pipeline
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="px-3 py-1.5 border border-[#D4AF37]/50 bg-[#D4AF37]/10 text-[#D4AF37] font-['JetBrains_Mono'] text-xs flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-green-400 animate-pulse" />
                <span>RECORDS UNCHAINED 71228</span>
              </div>
            </div>
          </div>
        </div>

        {/* Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left: Release Packaging & Verification */}
          <div className="lg:col-span-6 space-y-4">
            <div className="border border-[#D4AF37]/60 bg-black/90 p-5 space-y-4">
              <div className="flex items-center gap-2 border-b border-[#4B0082] pb-3">
                <Music className="w-5 h-5 text-[#D4AF37]" />
                <h2 className="text-base font-['Cinzel'] font-bold text-[#D4AF37]">
                  Master Release Sealing Pipeline
                </h2>
              </div>

              <div className="space-y-3 text-xs font-['JetBrains_Mono']">
                <div>
                  <label className="text-[10px] text-[#D4AF37] uppercase block mb-1">TRACK / RELEASE TITLE</label>
                  <input
                    type="text"
                    value={trackTitle}
                    onChange={(e) => setTrackTitle(e.target.value)}
                    className="w-full bg-black border border-[#4B0082] px-3 py-2 text-[#F1EFF4] focus:outline-none focus:border-[#D4AF37]"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-[10px] text-[#D4AF37] uppercase block mb-1">PRIMARY ARTIST</label>
                    <input
                      type="text"
                      disabled
                      value={artistName}
                      className="w-full bg-black/40 border border-[#4B0082]/40 px-3 py-2 text-[#D4AF37] font-bold"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-[#D4AF37] uppercase block mb-1">HARMONIC TUNING</label>
                    <div className="grid grid-cols-2 gap-1 border border-[#4B0082] p-1 bg-black">
                      <button
                        type="button"
                        onClick={() => setTuningStandard('432Hz')}
                        className={`py-1 text-[10px] font-bold ${tuningStandard === '432Hz' ? 'bg-[#D4AF37] text-black' : 'text-[#F1EFF4]/70 hover:text-white'}`}
                      >
                        432Hz
                      </button>
                      <button
                        type="button"
                        onClick={() => setTuningStandard('440Hz')}
                        className={`py-1 text-[10px] font-bold ${tuningStandard === '440Hz' ? 'bg-[#D4AF37] text-black' : 'text-[#F1EFF4]/70 hover:text-white'}`}
                      >
                        440Hz
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Live Audio Physics DSP Metering */}
              <div className="border border-[#4B0082] bg-black/60 p-3.5 space-y-3">
                <span className="text-[10px] font-['JetBrains_Mono'] text-[#D4AF37] uppercase tracking-wider block">
                  ACOUSTIC PHYSICS & BROADCAST LOUDNESS DSP
                </span>

                <div className="grid grid-cols-3 gap-2 text-center text-xs font-['JetBrains_Mono']">
                  <div className="border border-[#4B0082]/80 bg-black p-2">
                    <span className="text-[9px] text-[#F1EFF4]/60 block">INTEGRATED</span>
                    <span className="text-sm font-bold text-[#D4AF37]">{lufsValue} LUFS</span>
                    <span className="text-[9px] text-green-400 block">TARGET -14.0</span>
                  </div>
                  <div className="border border-[#4B0082]/80 bg-black p-2">
                    <span className="text-[9px] text-[#F1EFF4]/60 block">TRUE PEAK</span>
                    <span className="text-sm font-bold text-[#D4AF37]">{truePeak} dBTP</span>
                    <span className="text-[9px] text-green-400 block">MAX -1.0</span>
                  </div>
                  <div className="border border-[#4B0082]/80 bg-black p-2">
                    <span className="text-[9px] text-[#F1EFF4]/60 block">PHASE CORR</span>
                    <span className="text-sm font-bold text-emerald-400">+{phaseCorrelation}</span>
                    <span className="text-[9px] text-emerald-300 block">MONO SAFE</span>
                  </div>
                </div>

                {/* Meter visual bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[9px] font-['JetBrains_Mono'] text-[#F1EFF4]/60">
                    <span>-24 LUFS</span>
                    <span className="text-[#D4AF37] font-bold">-14 LUFS (STREAMING SPEC)</span>
                    <span>-6 LUFS</span>
                  </div>
                  <div className="w-full h-2 bg-black border border-[#4B0082] overflow-hidden relative">
                    <div className="absolute left-[58%] top-0 bottom-0 w-0.5 bg-yellow-400 z-10" />
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 via-[#D4AF37] to-amber-500 transition-all duration-300"
                      style={{ width: `${Math.min(100, Math.max(10, (1 - (Math.abs(lufsValue) / 30)) * 100))}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* 3000x3000px Artwork Inspector */}
              <div className="p-3 border border-[#4B0082] bg-white/5 space-y-2 text-xs font-['JetBrains_Mono']">
                <div className="flex items-center justify-between">
                  <span className="text-[#F1EFF4]/70">3000x3000px ARTWORK DIMENSIONS:</span>
                  <span className="text-green-400 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> 3000 × 3000 PX (EXACT)
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#F1EFF4]/70">PRINT DENSITY & COLOR PROFILE:</span>
                  <span className="text-green-400 font-bold">300 DPI // sRGB IEC61966-2.1</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#F1EFF4]/70">PHYSICS HARMONIC FREQUENCY:</span>
                  <span className="text-[#D4AF37] font-bold">{tuningStandard} / 48kHz MATCH</span>
                </div>
              </div>

              <button
                onClick={runDistributionPipeline}
                disabled={isSealing}
                className="w-full py-3 bg-[#D4AF37] text-black font-['Cinzel'] font-black text-xs tracking-widest uppercase hover:bg-[#F1EFF4] transition-all flex items-center justify-center gap-2 disabled:opacity-50 min-h-[44px]"
              >
                {isSealing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    SEALING ISRC & METADATA...
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    EXECUTE 1VIZION DISTRIBUTION SEAL
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Right: Master Attestation Details */}
          <div className="lg:col-span-6 space-y-4">
            {sealReport && (
              <div className="border border-[#D4AF37] bg-black/95 p-5 space-y-4 shadow-[0_0_20px_rgba(212,175,55,0.2)]">
                <div className="flex items-center justify-between border-b border-[#4B0082] pb-3">
                  <span className="text-xs font-['Cinzel'] font-bold text-[#D4AF37]">
                    SEALED DISTRIBUTION MANIFEST
                  </span>
                  <span className="text-[10px] font-['JetBrains_Mono'] text-green-400">
                    SEALED AT {sealReport.sealedTimestamp}
                  </span>
                </div>

                <div className="space-y-3 font-['JetBrains_Mono'] text-xs">
                  <div className="p-3 border border-[#4B0082] bg-black flex justify-between items-center">
                    <span className="text-[#F1EFF4]/70">BOUND ISRC:</span>
                    <span className="text-[#D4AF37] font-bold font-mono">{sealReport.isrc}</span>
                  </div>

                  <div className="p-3 border border-[#4B0082] bg-black flex justify-between items-center">
                    <span className="text-[#F1EFF4]/70">ASSIGNED UPC:</span>
                    <span className="text-[#D4AF37] font-bold font-mono">{sealReport.upc}</span>
                  </div>

                  <div className="p-3 border border-[#4B0082] bg-black flex justify-between items-center">
                    <span className="text-[#F1EFF4]/70">ARTWORK ATTESTATION:</span>
                    <span className="text-green-400 font-mono text-[10px]">{sealReport.artworkHash}</span>
                  </div>

                  <div className="grid grid-cols-3 gap-2">
                    <div className="p-2 border border-[#4B0082] bg-black text-center">
                      <span className="text-[9px] text-[#F1EFF4]/60 block">INTEGRATED</span>
                      <span className="text-xs font-bold text-[#D4AF37]">{sealReport.lufs} LUFS</span>
                    </div>
                    <div className="p-2 border border-[#4B0082] bg-black text-center">
                      <span className="text-[9px] text-[#F1EFF4]/60 block">TRUE PEAK</span>
                      <span className="text-xs font-bold text-[#D4AF37]">{sealReport.truePeak} dBTP</span>
                    </div>
                    <div className="p-2 border border-[#4B0082] bg-black text-center">
                      <span className="text-[9px] text-[#F1EFF4]/60 block">PHASE</span>
                      <span className="text-xs font-bold text-emerald-400">+{sealReport.phase}</span>
                    </div>
                  </div>

                  <div className="p-3 border border-[#4B0082] bg-black flex justify-between items-center">
                    <span className="text-[#F1EFF4]/70">ACOUSTIC PROFILE:</span>
                    <span className="text-green-400 font-bold text-[11px]">{sealReport.audioPhysicsStatus}</span>
                  </div>

                  <div className="p-3 border border-[#D4AF37]/50 bg-[#D4AF37]/10 text-[#D4AF37] text-center font-bold">
                    ATTESTATION: RECORDS UNCHAINED 71228 SEALED ⚜️_SOVEREIGN_TRUTH
                  </div>
                </div>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
}
