import React, { useEffect, useState } from 'react';
import { Mic, MicOff, Globe, Loader2, Sparkles, Zap } from 'lucide-react';
import { speakNeural, initVoice } from './VoiceEngine';
import { runtimeConfig } from '@/config/runtime';
import { bifrostFetch } from '@/lib/bifrostClient';

interface AnyasLinkProps {
  externalUrl: string;
}

// 🛡️ CONFIGURATION: Your Modal Endpoint
const CLOUD_BRAIN_URL = runtimeConfig.cloudBrainUrl;

export default function AnyasLink({ externalUrl }: AnyasLinkProps) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [engineState, setEngineState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [useCloudVoice, setUseCloudVoice] = useState(true); // Default to High Quality

  // Initialize Local Neural Voice (Fallback)
  useEffect(() => {
    initVoice()
      .then(() => setEngineState('ready'))
      .catch(() => setEngineState('error'));
  }, []);

  const speakLocal = async (text: string) => {
    setIsSpeaking(true);
    try {
      if (engineState === 'ready') {
        await speakNeural(text);
      } else {
        throw new Error("Neural Engine not ready");
      }
    } catch (e) {
      const utterance = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.speak(utterance);
    } finally {
      setTimeout(() => setIsSpeaking(false), text.length * 100); 
    }
  };

  const speakCloud = async (topic: string) => {
    setIsProcessing(true);
    try {
        // Call Modal Function
        const res = await bifrostFetch(CLOUD_BRAIN_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ topic })
        });
        
        const data = await res.json();
        
        if (data.audio_briefing) {
            // Play the Replicate Audio URL
            const audio = new Audio(data.audio_briefing);
            audio.onplay = () => { setIsProcessing(false); setIsSpeaking(true); };
            audio.onended = () => setIsSpeaking(false);
            audio.play();
        } else {
            throw new Error("No audio returned");
        }
    } catch (e) {
        console.error("Cloud Voice Failed:", e);
        speakLocal(`I cannot reach the cloud. ${topic}`);
        setIsProcessing(false);
    }
  };

  const handleMicClick = () => {
    if (isSpeaking || isProcessing) return;

    if (useCloudVoice) {
        // Trigger a Cinematic Briefing (Humanistic)
        speakCloud("The Current State of Camelot OS");
    } else {
        // Trigger Local Response (Fast)
        speakLocal("Camelot OS Light Online. How may I serve you, Sovereign?");
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-black text-white overflow-hidden">
      {/* Mobile Header */}
      <div className="flex items-center justify-between p-4 bg-slate-900 border-b border-slate-800">
        <div className="flex flex-col">
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
            Anya's Link
            </h1>
            <span className="text-[10px] text-slate-500">
                {useCloudVoice ? "✨ KOKORO CLOUD (Humanistic)" : "⚡ LOCAL NEURAL (Fast)"}
            </span>
        </div>
        
        <div className="flex gap-2 items-center">
          <button
            onClick={() => setUseCloudVoice(!useCloudVoice)}
            className={`p-2 rounded-full transition-all ${useCloudVoice ? 'text-purple-400 bg-purple-900/20' : 'text-slate-500 bg-slate-800'}`}
          >
            {useCloudVoice ? <Sparkles size={16} /> : <Zap size={16} />}
          </button>

          {isProcessing && <Loader2 className="w-6 h-6 animate-spin text-purple-500" />}
          
          <button 
            onClick={handleMicClick}
            disabled={isProcessing}
            className={`p-3 rounded-full transition-all shadow-lg ${
                isSpeaking ? 'bg-green-500 hover:bg-green-600 shadow-green-500/50 animate-pulse' : 
                isProcessing ? 'bg-slate-700' :
                'bg-blue-600 hover:bg-blue-700 shadow-blue-500/50'
            }`}
          >
            {isSpeaking ? <MicOff size={24} /> : <Mic size={24} />}
          </button>
        </div>
      </div>

      {/* Main Content: Wikipedia Random (Research Simulation) */}
      <div className="flex-1 relative w-full h-full">
        <iframe 
          src={externalUrl} 
          className="w-full h-full border-none opacity-80 hover:opacity-100 transition-opacity"
          title="Anya's Visual Context"
        />
      </div>
    </div>
  );
}
