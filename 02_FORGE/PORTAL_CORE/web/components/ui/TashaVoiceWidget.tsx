// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"use client";

import { useState, useCallback } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  BarVisualizer,
  DisconnectButton,
} from "@livekit/components-react";
import "@livekit/components-styles";

function TashaSession({ onDisconnect }: { onDisconnect: () => void }) {
  const { state, audioTrack } = useVoiceAssistant();

  const statusText: Record<string, string> = {
    disconnected: "Connecting...",
    connecting: "Connecting...",
    initializing: "Starting...",
    listening: "Tasha is listening",
    thinking: "Tasha is thinking...",
    speaking: "Tasha is speaking",
  };

  return (
    <div className="flex flex-col items-center gap-4 p-6">
      <div className="w-48 h-24">
        <BarVisualizer
          state={state}
          barCount={7}
          trackRef={audioTrack}
          className="w-full h-full"
          options={{ minHeight: 8 }}
        />
      </div>

      <p className="text-sm text-white/70 font-medium">
        {statusText[state] || "Connected"}
      </p>

      <DisconnectButton
        className="px-4 py-2 rounded-full bg-red-500/80 hover:bg-red-500 text-white text-sm font-medium transition-colors"
        onClick={onDisconnect}
      >
        End Call
      </DisconnectButton>

      <RoomAudioRenderer />
    </div>
  );
}

export function TashaVoiceWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [livekitUrl, setLivekitUrl] = useState<string | null>(null);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startCall = useCallback(async () => {
    setConnecting(true);
    setError(null);
    try {
      const res = await fetch("/api/livekit-token", { method: "POST" });
      if (!res.ok) throw new Error("Failed to get connection token");
      const data = await res.json();
      setToken(data.token);
      setLivekitUrl(data.url);
      setIsOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection failed");
    } finally {
      setConnecting(false);
    }
  }, []);

  const endCall = useCallback(() => {
    setIsOpen(false);
    setToken(null);
    setLivekitUrl(null);
  }, []);

  // Floating call button
  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50 pointer-events-auto">
        <button
          onClick={startCall}
          disabled={connecting}
          className="group flex items-center gap-3 px-5 py-3 rounded-full
                     bg-gradient-to-r from-amber-500 to-yellow-500
                     hover:from-amber-400 hover:to-yellow-400
                     text-black font-semibold shadow-lg shadow-amber-500/25
                     transition-all duration-200 hover:scale-105
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
          {connecting ? "Connecting..." : "Talk to Tasha"}
        </button>

        {error && (
          <p className="mt-2 text-xs text-red-400 text-center">{error}</p>
        )}
      </div>
    );
  }

  // Active call panel
  return (
    <div className="fixed bottom-6 right-6 z-50 pointer-events-auto">
      <div
        className="w-72 rounded-2xl border border-white/10
                    bg-black/80 backdrop-blur-xl shadow-2xl shadow-amber-500/10
                    overflow-hidden"
      >
        <div className="px-4 py-3 border-b border-white/10 bg-gradient-to-r from-amber-500/10 to-transparent">
          <h3 className="text-sm font-semibold text-amber-400">
            Tasha — Voice Receptionist
          </h3>
        </div>

        {token && livekitUrl && (
          <LiveKitRoom
            token={token}
            serverUrl={livekitUrl}
            connectOptions={{ autoSubscribe: true }}
            audio={true}
            video={false}
            onDisconnected={endCall}
          >
            <TashaSession onDisconnect={endCall} />
          </LiveKitRoom>
        )}
      </div>
    </div>
  );
}
