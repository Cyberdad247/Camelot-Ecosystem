// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS - CONFIDENTIAL AND PROPRIETARY

let voiceReady = false;

function hasSpeechSynthesis(): boolean {
  return (
    typeof window !== 'undefined' &&
    'speechSynthesis' in window &&
    'SpeechSynthesisUtterance' in window
  );
}

export const initVoice = async () => {
  if (!hasSpeechSynthesis()) {
    throw new Error('Browser speech synthesis is not available in this environment.');
  }

  voiceReady = true;
  return window.speechSynthesis;
};

export const speakNeural = async (text: string) => {
  if (!voiceReady) {
    await initVoice();
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.96;
  utterance.pitch = 1.02;
  utterance.volume = 0.95;

  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
};
