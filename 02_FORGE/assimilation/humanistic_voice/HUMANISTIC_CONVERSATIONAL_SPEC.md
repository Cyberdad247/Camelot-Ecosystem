# HUMANISTIC CONVERSATIONAL SPECIFICATION
## v10001.00-CYBERTRONIA — Live Speech Communication & Vocal Prosody Assimilation
@ctx|camelot-os.dev/ukg/v10001/humanistic_voice @typ|Sovereign_Assimilation_Spec id|Ω_HUMANISTIC_VOICE_NEXUS

---

## 1. Executive Summary & Prime Directive

The **Humanistic Voice Nexus** assimilates six open-source repositories to transform standard turn-based LLM voice interactions into a **seamless, empathic, full-duplex Human-to-Humanistic conversation**.

Traditional voice assistants suffer from:
1. **Turn-taking rigidity**: Cutting humans off during mid-sentence thinking pauses, or awkwardly waiting 1.5 seconds after a short answer.
2. **Robotic cadence**: Speaking at a constant mechanical pace and volume regardless of user urgency, sadness, or excitement.
3. **False interruptions**: Abruptly stopping when the human says "mhm" or "yeah" (backchannel cues).
4. **Disembodied speech**: Vocal audio disjointed from facial expressions and mouth movements.

This specification assimilates the media streaming, continuous audio recognition, real-time avatar synthesis, and WebSocket/WebRTC protocols from six foundational projects into Camelot-OS's **Multivoice Router** and **Reya Fabric Layer**.

---

## 2. The 6-Repository Assimilation Topology

| Repository | Source Origin | Assimilated Subsystem | Architectural Role |
| :--- | :--- | :--- | :--- |
| **`nhunzaker/speakeasy`** | Browser Web Speech API | `SpeakeasySpeechAdapter` | Client-side audio synthesis, queueing, and dynamic pitch/rate calibration sliders |
| **`livnoni/continuousSpeechRecognition`** | Web Speech / Mic Stream | `ContinuousSpeechRecognizer` | Continuous audio capture loop, stream auto-recovery, and silence/pause thresholding |
| **`danships/genie-ai`** | Streaming Conversational AI | `GenieConversationalEngine` | Token-by-token sentence boundary detection, streaming punctuation chunking, dynamic interrupt |
| **`viniciuspereiras/OpenAIChat`** | Realtime WebSocket Protocol | `OpenAIDuplexBridge` | Bidirectional audio/text frame transport, ephemeral session lifecycle, client audio framing |
| **`Cyberdad247/LiveTalking`** | Realtime Digital Human | `LiveTalkingVisemeSync` | Audio-to-viseme lip synchronization (25 FPS), phoneme timing alignment, WebRTC video track |
| **`Cyberdad247/livekit`** | WebRTC Media Server & SDK | `LiveKitMediaTransport` | Sub-100ms bidirectional WebRTC SFU, audio/video track subscription, voice agent room coordinator |

---

## 3. Acoustic Prosody & Vocal Pattern Analysis Engine

The core cognitive leap is the **`VocalPatternAnalyzer`**, which inspects incoming human audio in sliding 20ms–50ms analysis windows:

### A. Fundamental Frequency ($F_0$) & Intonation Tracking
- Tracks the human speaker's pitch contour $F_0(t)$ across voiced frames.
- Calculates pitch inflection slope $\Delta F_0 = F_0(\text{terminal}) - F_0(\text{onset})$:
  - **Rising Intonation ($\Delta F_0 > +15\text{ Hz}$)**: Indicates an unfinished thought, continuation cue, or open question.
    - *Action*: Dynamically expand silence threshold to **650ms** (prevent cutting the human off).
  - **Falling Intonation ($\Delta F_0 < -15\text{ Hz}$)**: Indicates a definitive terminal statement or closed command.
    - *Action*: Dynamically contract silence threshold to **200ms** for crisp, immediate turn-taking.
  - **Flat / Neutral Intonation**: Standard declarative utterance.

### B. Speech Cadence & Dynamic Pacing Alignment
- Measures words-per-minute (WPM) and syllable duration.
- **Humanistic Cadence Mirroring**:
  - If user is rushed/urgent ($>165\text{ WPM}$): AI increases speech rate by $+15\%$ to $+20\%$ and compresses response latency.
  - If user is relaxed/hesitant ($<115\text{ WPM}$): AI reduces speech rate by $-10\%$ and adds gentle breath pauses.

### C. RMS Energy & Vocal Dynamic Valence
- Computes Root Mean Square (RMS) loudness in dBFS.
- **Energy Mirroring**:
  - Whispered / Low Energy ($< -32\text{ dBFS}$): AI shifts to warm, intimate near-field timbre (e.g., Reya companion mode).
  - Assertive / High Energy ($> -16\text{ dBFS}$): AI responds with crisp, high-presence architectural resonance (e.g., Sir Boris / Arthur).

### D. Intelligent Backchannel Filter (Non-Interruptive Barge-In)
- Humans constantly utter conversational grounding signals: *"mhm"*, *"yeah"*, *"uh-huh"*, *"right"*, *"sure"*.
- In naive voice bots, any mic signal flushes the output buffer and stops the AI mid-sentence.
- The **Backchannel Detector** evaluates duration ($<420\text{ ms}$), low RMS energy, and acoustic syllable count:
  - If identified as a **Backchannel**: The AI **continues speaking uninterrupted**, logging user affirmation into short-term context.
  - If identified as **True Interruption** ($>500\text{ ms}$ or high semantic content): Outbound audio immediately halts in $<30\text{ ms}$.

### E. LiveTalking Audio-to-Viseme Synchronization
- As streaming audio chunks emerge from the TTS diffusion head or Gemini Live outbound stream, the audio is analyzed for phoneme energy.
- Emits 16 standard visemes (Sil, AA, AE, AH, AO, B/M/P, CH/J/SH, D/T, EH, ER, F/V, K/G, L, N, R, W/UW) at 25 FPS.
- Enables synchronous lip movement on 2D/3D WebGPU avatar interfaces (`LakishaHUD` / `LiveTalking`).

---

## 4. Architectural State Machine

```
              ┌────────────────────────────────────────────────────────┐
              │             Human Audio Stream (LiveKit WebRTC)        │
              └──────────────────────────┬─────────────────────────────┘
                                         │
                                         ▼
              ┌────────────────────────────────────────────────────────┐
              │              VocalPatternAnalyzer                      │
              │  - F0 Pitch Contour: Rising (+Δ) vs Falling (-Δ)       │
              │  - Cadence: WPM calculation (Urgent vs Relaxed)        │
              │  - Backchannel Classifier ("mhm", "yeah" -> Ignore)    │
              │  - Adaptive Turn-Taking Timer (200ms - 650ms)          │
              └──────────────────────────┬─────────────────────────────┘
                                         │
                         [Turn Complete Verified]
                                         │
                                         ▼
              ┌────────────────────────────────────────────────────────┐
              │             Humanistic Conversational Loop             │
              │  - Dynamic Prosody Prompt Conditioning                 │
              │  - Token-by-token Streaming (Genie / OpenAIChat)       │
              │  - Channeled Knight Selection (Reya / Boris / Merlin)  │
              └──────────────────────────┬─────────────────────────────┘
                                         │
                                         ▼
              ┌────────────────────────────────────────────────────────┐
              │                  Streaming Multivoice TTS              │
              │  - Pacing & Pitch Offset Mirroring Applied             │
              │  - LiveTalking Visemes Streamed via WebRTC DataChannel │
              └────────────────────────────────────────────────────────┘
```
