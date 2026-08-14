// SPDX-License-Identifier: MIT

/**
 * VoiceSquire: Anya's Voice Interface
 * Provides speech recognition (input) and text-to-speech (output) for hands-free operation.
 */
export class VoiceSquire {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.wakeWords = ['nano', 'anya', 'merlin'];
        
        this.anyaVoice = null;
        this.defaultRate = 1.0;
        this.defaultPitch = 1.0;
        
        this.initialize();
    }

    initialize() {
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            // Handle auto-stop or silence
            this.recognition.onend = () => {
                console.log('[VoiceSquire] Internal Recognition End');
                this.isListening = false;
                if (this.onStateChange) this.onStateChange(false);
            };
        }

        if ('speechSynthesis' in window) {
            const loadVoices = () => {
                this.anyaVoice = this.selectAnyaVoice();
            };
            window.speechSynthesis.onvoiceschanged = loadVoices;
            loadVoices(); // Try immediate load
        }
    }

    startListening(onCommand, onError) {
        if (!this.recognition) {
            const err = 'Speech recognition not supported';
            if (onError) onError(err);
            return false;
        }

        if (this.isListening) return true;

        this.recognition.onresult = (event) => {
            const transcript = event.results[event.resultIndex][0].transcript.trim();
            console.log(`[VoiceSquire] Heard: "${transcript}"`);
            
            const command = this.extractCommand(transcript);
            if (command) {
                onCommand(command);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('[VoiceSquire] Recognition error:', event.error);
            this.isListening = false;
            if (onError) onError(event.error);
        };

        try {
            this.recognition.start();
            this.isListening = true;
            console.log('[VoiceSquire] Listening started...');
            return true;
        } catch (e) {
            console.error('[VoiceSquire] Start Failed:', e);
            this.isListening = false;
            return false;
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
            console.log('[VoiceSquire] Listening stopped.');
        }
    }

    extractCommand(transcript) {
        const lower = transcript.toLowerCase();
        // Use a more precise word-based check to avoid partial matches (e.g., "banano")
        const words = lower.split(/[\s,]+/);
        
        for (const wakeWord of this.wakeWords) {
            const wakeIndex = words.indexOf(wakeWord);
            if (wakeIndex !== -1) {
                // Determine the character index for substring slicing
                // This preserves original casing for the command
                const rawLower = transcript.toLowerCase();
                const charIndex = rawLower.indexOf(wakeWord);
                const commandText = transcript.substring(charIndex + wakeWord.length)
                                              .replace(/^[\s,!:;]+/, '').trim();
                
                if (commandText.length > 0) {
                    return {
                        raw: transcript,
                        wakeWord: wakeWord,
                        command: commandText
                    };
                }
            }
        }
        return null;
    }

    speak(text, options = {}) {
        if (!('speechSynthesis' in window)) return;

        speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.anyaVoice || this.selectAnyaVoice();
        utterance.rate = options.rate || this.defaultRate;
        utterance.pitch = options.pitch || this.defaultPitch;
        utterance.volume = options.volume || 1.0;

        speechSynthesis.speak(utterance);
    }

    selectAnyaVoice() {
        const voices = speechSynthesis.getVoices();
        const targets = [
            v => v.name.includes('Google') && v.name.includes('Female'),
            v => v.name.includes('Samantha') || v.name.includes('Victoria'),
            v => v.lang.startsWith('en-US') && (v.name.includes('Female') || v.name.includes('Soft'))
        ];

        for (const target of targets) {
            const match = voices.find(target);
            if (match) return match;
        }
        return voices.find(v => v.lang.startsWith('en')) || voices[0];
    }
}

