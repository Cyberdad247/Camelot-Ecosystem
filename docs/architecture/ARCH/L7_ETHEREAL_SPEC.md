# L7: THE ETHEREAL LAYER (Architecture Spec)
**Guardian:** Anya_Ω
**Domain:** Interface, Voice, "Vibe"
**Status:** ACTIVE

## 1. Executive Summary
Layer 7 (The Ethereal) is the user-facing membrane of the Septem Regna. It translates Kinetic (L2) and Semantic (L4) data into human-perceivable formats: Visuals (PWA), Audio (Voice), and Personality (Vibe).

## 2. Core Components

### A. The Kinetic Interface (PWA)
*   **Tech Stack:** Next.js / React (hosted via Vercel or Local).
*   **Bridge:** Connects to **Saltare** via REST/WebSocket.
*   **Role:**
    *   **The Mirror:** Displays the HUD visuals on mobile/desktop.
    *   **The Input:** Captures touch/voice inputs for the Kernel.

### B. The Voice Engine (Vox Anima)
*   **Tech Stack:** OpenAI Realtime API / ElevenLabs (Cloud) + Kokoro (Local).
*   **Protocol:** WebSocket stream for <200ms latency.
*   **Role:**
    *   **Anya's Voice:** Provides empathetic, personality-driven feedback.
    *   **Command:** Accepts "Hey Anya" wake words.

### C. The "Vibe" Engine (Sentiment Matrix)
*   **Tech Stack:** Python (Textual) + Symbolect.
*   **Role:**
    *   **Dynamic Theme:** Changes HUD colors based on system load (Green=Calm, Red=Crisis).
    *   **Personality Injection:** Injects slang/tone into responses based on the "Vibe Score."

## 3. Data Flow
1.  **User Input:** Voice/Text -> L7 PWA.
2.  **Transduction:** L7 -> **Saltare (Gateway)** via API.
3.  **Reasoning:** Saltare -> **Merlin (L3)**.
4.  **Execution:** Merlin -> **Lukas (L2)**.
5.  **Feedback:** Lukas -> **Rotel** -> **L7 PWA (Visual Update)**.

## 4. Integrity Metrics
*   **Latency:** Voice Response < 500ms.
*   **Uptime:** PWA 99.9%.
*   **Vibe Check:** Tone matches context (e.g., Serious during errors, Playful during idle).
