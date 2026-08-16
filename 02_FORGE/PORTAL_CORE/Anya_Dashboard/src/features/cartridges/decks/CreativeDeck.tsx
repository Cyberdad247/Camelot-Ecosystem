import React, { useState } from 'react';
import { Send, Loader2, Palette, Music, Mic } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DeckProps } from '../CartridgeDeck';

type OutputType = 'text' | 'voice' | 'script' | 'storyboard';
type VoicePersona = 'Anya_Omega' | 'Merlin_Omega' | 'Lukas_Omega';
type Tone = 'professional' | 'casual' | 'nyc_street' | 'epic';

const VOICE_DESC: Record<VoicePersona, string> = {
  Anya_Omega: 'Interface Sovereign — clear, authoritative, NYC street-smart',
  Merlin_Omega: 'Neural Conductor — mystical, deep, measured',
  Lukas_Omega: 'Kinetic Baron — direct, technical, high-velocity',
};

export default function CreativeDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [outputType, setOutputType] = useState<OutputType>('text');
  const [voice, setVoice] = useState<VoicePersona>('Anya_Omega');
  const [tone, setTone] = useState<Tone>('casual');
  const [ttsSpeed, setTtsSpeed] = useState(0.96);

  const submit = () =>
    onDispatch(intent, {
      output_type: outputType,
      voice_persona: voice,
      tone,
      tts_speed: ttsSpeed,
    });

  return (
    <div className="space-y-5">
      <p className="text-xs text-slate-500">
        SIR_SONUS — Voice AI, media production, narrative generation.
      </p>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-pink-400">
          Creative Brief
        </label>
        <textarea
          rows={4}
          placeholder="Describe the creative output: a voice intro, a brand story, a video script, a social caption…"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-pink-500 resize-none"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block">
          Output Type
        </label>
        <div className="grid grid-cols-4 gap-1.5">
          {(['text', 'voice', 'script', 'storyboard'] as OutputType[]).map((t) => (
            <button
              key={t}
              onClick={() => setOutputType(t)}
              className={cn(
                'rounded-lg border py-2 text-xs font-bold capitalize transition-colors',
                outputType === t
                  ? 'bg-pink-900/50 border-pink-500/50 text-pink-200'
                  : 'border-slate-700 text-slate-500 hover:border-slate-600',
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {(outputType === 'voice' || outputType === 'script') && (
        <div>
          <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
            <Mic className="h-3.5 w-3.5" /> Voice Persona
          </label>
          {(['Anya_Omega', 'Merlin_Omega', 'Lukas_Omega'] as VoicePersona[]).map((v) => (
            <button
              key={v}
              onClick={() => setVoice(v)}
              className={cn(
                'w-full text-left rounded-lg border px-3 py-2 mb-1.5 transition-colors',
                voice === v
                  ? 'bg-pink-950/50 border-pink-500/40 text-pink-200'
                  : 'border-slate-700 text-slate-400 hover:border-slate-600',
              )}
            >
              <p className="text-xs font-bold">{v}</p>
              <p className="text-[10px] text-slate-600">{VOICE_DESC[v]}</p>
            </button>
          ))}
          <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1.5 block mt-3">
            TTS Speed: <span className="text-pink-400">{ttsSpeed.toFixed(2)}×</span>
          </label>
          <input
            type="range"
            min={0.5}
            max={1.5}
            step={0.01}
            value={ttsSpeed}
            onChange={(e) => setTtsSpeed(Number(e.target.value))}
            className="w-full accent-pink-500"
          />
        </div>
      )}

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block">
          Tone
        </label>
        <div className="grid grid-cols-4 gap-1.5">
          {(['professional', 'casual', 'nyc_street', 'epic'] as Tone[]).map((t) => (
            <button
              key={t}
              onClick={() => setTone(t)}
              className={cn(
                'rounded-lg border py-2 text-xs font-bold capitalize transition-colors',
                tone === t
                  ? 'bg-pink-900/50 border-pink-500/50 text-pink-200'
                  : 'border-slate-700 text-slate-500 hover:border-slate-600',
              )}
            >
              {t.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-pink-700 hover:bg-pink-600 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Palette className="h-4 w-4" />
        )}
        {dispatching ? 'Creating…' : 'Dispatch to SIR_SONUS'}
      </button>
    </div>
  );
}
