// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { pipeline } from '@xenova/transformers';

let synthesizer: any = null;
let initPromise: Promise<any> | null = null;

export const initVoice = async () => {
  if (synthesizer) return synthesizer;
  
  if (!initPromise) {
    console.log("🧠 [TRANSFORMERS] Loading Web Neural Engine...");
    initPromise = pipeline('text-to-speech', 'Xenova/speecht5_tts', { quantized: true })
      .then(s => {
        console.log("✅ [TRANSFORMERS] Engine Active.");
        synthesizer = s;
        return s;
      })
      .catch(e => {
        console.error("❌ [TRANSFORMERS] Init Failed:", e);
        initPromise = null; // Reset on failure so we can retry
        throw e;
      });
  }
  
  return initPromise;
};

export const speakNeural = async (text: string, speakerEmbeddings: string = 'https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/main/speaker_embeddings.bin') => {
  const synth = await initVoice();
  
  // Create speaker embeddings (SpeechT5 requires this)
  const response = await fetch(speakerEmbeddings);
  if (!response.ok) {
    throw new Error(`Failed to fetch speaker embeddings: ${response.statusText}`);
  }
  const speaker_embeddings = await response.arrayBuffer();

  const result = await synth(text, { speaker_embeddings });
  
  // Play Audio
  const wav = new Blob([result.audio], { type: 'audio/wav' });
  const url = URL.createObjectURL(wav);
  const audio = new Audio(url);
  audio.play();
};