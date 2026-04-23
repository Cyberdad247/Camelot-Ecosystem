# Skill: Voice AI (SIR_SONUS)
# Loaded when voice/audio interactions detected

## Mode A: No-Code (ElevenLabs Conversational AI 2.0)
- System Prompt defines brain behavior
- Upload Knowledge Base PDFs for domain expertise
- Select from 3,000+ voices or clone custom
- Native Twilio integration for real phone number
- Sub-second latency + state-of-the-art turn-taking
- Handles interruptions, filler words, mid-sentence corrections

## Mode B: Custom (LiveKit Pipeline)
- ASR: assemblyai (<100ms STT)
- Brain: openai.LLM or Cerebras Llama 3.1
- TTS: rime (synthesis)
- VAD: silero (Voice Activity Detection for natural turn-taking)
- Supports barge-in (interruptions)

## Mode C: Local Neural (Piper TTS + HuggingFace)
- Engine: piper-tts (ONNX runtime, zero API cost)
- Models: rhasspy/piper-voices on HuggingFace (auto-download)
- Tasha default: en_GB-jenny_dioco-medium (British female)
- Presets: tasha, tasha_british, tasha_scottish, merlin, narrator
- Streaming: synthesize_stream() for real-time playback
- Setup: python 01_KERNEL/forge/scripts/setup_piper.py
- Env override: CAMELOT_TTS_ENGINE=piper (voice_swarm auto-selects)
- Fallback chain: Piper → Kokoro → ElevenLabs

## Constraints
- Sub-second latency mandatory (Voice Law)
- No IVR-style rigid menu trees
- Natural conversational flow required
- Reports to SIR_KRONOS for latency management
