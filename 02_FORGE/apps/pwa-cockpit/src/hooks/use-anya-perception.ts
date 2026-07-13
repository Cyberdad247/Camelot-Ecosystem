"use client";

import { useEffect, useState } from "react";

export type AnyaPerceptionSignal = {
  present: boolean;
  gazeX: number;
  gazeY: number;
  blink: number;
  mouthOpen: number;
};

type PerceptionState = "disabled" | "starting" | "tracking" | "no-face" | "unavailable" | "error";

const neutralSignal: AnyaPerceptionSignal = { present: false, gazeX: 0, gazeY: 0, blink: 0, mouthOpen: 0 };

export function useAnyaPerception(enabled: boolean) {
  const [state, setState] = useState<PerceptionState>("disabled");
  const [signal, setSignal] = useState<AnyaPerceptionSignal>(neutralSignal);

  useEffect(() => {
    if (!enabled) {
      setState("disabled");
      setSignal(neutralSignal);
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia || typeof Worker === "undefined" || typeof createImageBitmap === "undefined") {
      setState("unavailable");
      return;
    }

    let disposed = false;
    let ready = false;
    let cameraUnavailable = false;
    let framePending = false;
    let animationFrame = 0;
    let lastFrameAt = 0;
    let stream: MediaStream | null = null;
    const video = document.createElement("video");
    video.muted = true;
    video.playsInline = true;
    const worker = new Worker(new URL("../workers/anya-perception.worker.ts", import.meta.url), { type: "module" });

    const stop = () => {
      disposed = true;
      cancelAnimationFrame(animationFrame);
      stream?.getTracks().forEach((track) => track.stop());
      worker.postMessage({ type: "close" });
      worker.terminate();
      video.srcObject = null;
    };

    const sample = async (timestamp: number) => {
      if (disposed) return;
      if (ready && !framePending && video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA && timestamp - lastFrameAt >= 100) {
        framePending = true;
        lastFrameAt = timestamp;
        try {
          const frame = await createImageBitmap(video);
          if (disposed) frame.close();
          else worker.postMessage({ type: "frame", frame, timestamp }, [frame]);
        } catch {
          framePending = false;
        }
      }
      animationFrame = requestAnimationFrame(sample);
    };

    worker.onmessage = (event: MessageEvent<{ type: string; signal?: AnyaPerceptionSignal }>) => {
      if (event.data.type === "ready") {
        ready = true;
        if (!cameraUnavailable) setState("no-face");
      } else if (event.data.type === "signal" && event.data.signal) {
        framePending = false;
        setSignal(event.data.signal);
        setState(event.data.signal.present ? "tracking" : "no-face");
      } else if (event.data.type === "error") {
        framePending = false;
        setState("error");
      }
    };

    setState("starting");
    worker.postMessage({ type: "init", wasmRoot: "/mediapipe/wasm", modelPath: "/mediapipe/face_landmarker.task" });
    void navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 12, max: 15 } },
    }).then(async (mediaStream) => {
      if (disposed) {
        mediaStream.getTracks().forEach((track) => track.stop());
        return;
      }
      stream = mediaStream;
      video.srcObject = mediaStream;
      await video.play();
      animationFrame = requestAnimationFrame(sample);
    }).catch(() => {
      cameraUnavailable = true;
      ready = false;
      worker.postMessage({ type: "close" });
      setState("unavailable");
    });

    return stop;
  }, [enabled]);

  return { state, signal };
}
