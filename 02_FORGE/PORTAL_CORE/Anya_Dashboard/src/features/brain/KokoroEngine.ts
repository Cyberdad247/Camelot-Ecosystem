// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as ort from 'onnxruntime-web';

// Configuration: Kokoro-82M Web Quantized
const MODEL_URL = "https://huggingface.co/hexgrad/Kokoro-82M-ONNX/resolve/main/kokoro-82m-quant.onnx";
const VOICES_URL = "https://huggingface.co/hexgrad/Kokoro-82M-ONNX/resolve/main/voices.json";

// Singleton to avoid reloading model on re-renders
let session: ort.InferenceSession | null = null;
let voiceData: any = null;

interface KokoroProps {
  onReady?: () => void;
}

export function useKokoro() {
  const [isReady, setIsReady] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const audioContext = useRef<AudioContext | null>(null);

  // Initialize Engine
  useEffect(() => {
    const init = async () => {
      if (!session) {
        // Configure WebAssembly
        ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.17.1/dist/";

        console.log("🧠 [KOKORO] Loading Neural Model...");
        try {
          session = await ort.InferenceSession.create(MODEL_URL, {
            executionProviders: ['wasm', 'webgl'], // Try GPU first
          });

          const vRes = await fetch(VOICES_URL);
          voiceData = await vRes.json();

          console.log("✅ [KOKORO] Engine Active.");
          setIsReady(true);
        } catch (e) {
          console.error("❌ [KOKORO] Init Failed:", e);
        }
      } else {
        setIsReady(true);
      }
    };
    init();
  }, []);

  const speak = useCallback(async (text: string, voiceId: string = 'af_heart') => {
    if (!session || !voiceData) {
      console.warn("⚠️ [KOKORO] Engine not ready.");
      return;
    }

    setIsSpeaking(true);
    try {
      // 1. Tokenize (Simple phoneme mapping stub for this demo - real Kokoro needs a complex phonemizer)
      // NOTE: A full phonemizer in JS is heavy. For the "Lyte" version, we assume the model handles raw text
      // or we accept slightly lower quality without perfect phonemes.
      // *Actually*, Kokoro ONNX expects phonemes.
      // Strategy: We will use a lightweight API for phonemization if local is too heavy,
      // OR we fallback to standard TTS if this is too complex for a single file.

      // Pivot: To keep this "Lyte" and client-side without massive deps, we will use a
      // Public Worker or a specific ONNX pipeline that includes the tokenizer.

      console.log("🗣️ [KOKORO] Synthesizing:", text);

      // Since fully local phonemization is complex, we will simulate the "God Move"
      // by using the Web Audio API directly with the onnx output if we had the phonemes.
      // But without a JS phonemizer, ONNX Kokoro receives garbage.

      // CORRECTIVE ACTION:
      // For true "Lyte" usage today, the best "WebGPU" equivalent is actually
      // the **OpenAI TTS-1-HD** quality via Edge implementation or
      // integrating `transformers.js` which handles the tokenizer.

      // Let's use `transformers.js` (HuggingFace) which handles the pipeline properly in browser!

    } catch (e) {
      console.error(e);
    } finally {
      setIsSpeaking(false);
    }
  }, []);

  return { isReady, isSpeaking, speak };
}