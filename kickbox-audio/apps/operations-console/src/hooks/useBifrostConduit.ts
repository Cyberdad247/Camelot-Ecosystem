import { useEffect, useRef, useState, useCallback } from 'react';

export const useBifrostConduit = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [telemetry, setTelemetry] = useState({ memoryAlloc: '0MB', vadLatency: '0ms' });
  const wsRef = useRef<WebSocket | null>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);

  const initBifrost = useCallback(async () => {
    // 1. Establish mTLS WebSocket
    wsRef.current = new WebSocket('wss://bifrost.kba-services.internal:4433');
    
    wsRef.current.onopen = () => setIsConnected(true);
    wsRef.current.onclose = () => setIsConnected(false);

    // 2. Scaffold WebRTC Peer Connection
    peerConnectionRef.current = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });

    peerConnectionRef.current.ontrack = (event) => {
      if (videoRef.current) {
        videoRef.current.srcObject = event.streams[0];
      }
    };

    peerConnectionRef.current.onicecandidate = (event) => {
      if (event.candidate && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ice', candidate: event.candidate }));
      }
    };

    wsRef.current.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'offer') {
        await peerConnectionRef.current?.setRemoteDescription(new RTCSessionDescription(msg.offer));
        const answer = await peerConnectionRef.current?.createAnswer();
        await peerConnectionRef.current?.setLocalDescription(answer);
        wsRef.current?.send(JSON.stringify({ type: 'answer', answer }));
      } else if (msg.type === 'ice') {
        await peerConnectionRef.current?.addIceCandidate(new RTCIceCandidate(msg.candidate));
      } else if (msg.type === 'telemetry') {
        setTelemetry({ memoryAlloc: msg.memoryAlloc, vadLatency: msg.vadLatency });
      }
    };

    // 3. Mount AudioWorklet for Mic Capture
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      await audioContextRef.current.audioWorklet.addModule('/vocal_enclave_processor.js');
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      workletNodeRef.current = new AudioWorkletNode(audioContextRef.current, 'vocal_enclave_processor');
      
      workletNodeRef.current.port.onmessage = (event) => {
        if (event.data.eventType === 'audio_data' && wsRef.current?.readyState === WebSocket.OPEN) {
          // Send PCM Data over WebSocket for raw processing
          wsRef.current.send(event.data.pcmData.buffer);
        }
      };

      source.connect(workletNodeRef.current);
      workletNodeRef.current.connect(audioContextRef.current.destination);
    } catch (err) {
      console.error("[BIFROST] Mic access denied or worklet failed.", err);
    }
  }, []);

  useEffect(() => {
    initBifrost();
    return () => {
      wsRef.current?.close();
      peerConnectionRef.current?.close();
      audioContextRef.current?.close();
    };
  }, [initBifrost]);

  return { isConnected, videoRef, telemetry };
};
