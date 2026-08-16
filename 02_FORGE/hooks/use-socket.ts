// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
'use client';

import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export interface KnightState {
  name: string;
  hp: number;
  xp: number;
  current_task: string | null;
  status: string;
  last_thought: string;
}

export const useSocket = () => {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [knightState, setKnightState] = useState<KnightState | null>(null);

  useEffect(() => {
    // Connect to the Bridge (Port 8001)
    socketRef.current = io('http://localhost:8001', {
      transports: ['websocket'],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    const socket = socketRef.current;

    socket.on('connect', () => {
      console.log('✅ UseSocket: Connected to Bridge');
      setIsConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('❌ UseSocket: Disconnected');
      setIsConnected(false);
    });

    socket.on('thought_stream', (data: { message: string; stream?: boolean; error?: boolean }) => {
      setLogs((prev) => {
        // Optional: If streaming, we could append to the last message if it was also a stream
        // For now, we just list them to show the real-time effect
        return [...prev, `[THOUGHT] ${data.message}`];
      });
    });

    socket.on('state_update', (data: KnightState) => {
      setKnightState(data);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const sendCommand = (command: string) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('user_command', { command });
      setLogs((prev) => [...prev, `[USER] ${command}`]);
    } else {
      console.warn('Socket not connected');
    }
  };

  // Speech Synthesis
  const speak = (text: string) => {
    if (!window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 0.8; // Lower pitch for "Knight" effect
    // Try to find a good voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find((v) => v.name.includes('Google US English')) || voices[0];
    if (preferredVoice) utterance.voice = preferredVoice;
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    // Trigger voice on the last log if it's not a user command and not a stream update
    // Note: For real streaming TTS, we'd need a more complex buffer, but this works for "Thought Completed"
    const lastLog = logs[logs.length - 1];
    if (lastLog && !lastLog.startsWith('[USER]') && !lastLog.startsWith('[Thinking]')) {
      // Simple debounced speak or speak check could go here
      // For now, we only speak if the log seems complete or important
      // speak(lastLog.replace('[THOUGHT]', ''));
    }
  }, [logs]);

  return { isConnected, logs, sendCommand, knightState, speak };
};
