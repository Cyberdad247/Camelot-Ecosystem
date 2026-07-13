import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

type PerceptionSignal = {
  present: boolean;
  gazeX: number;
  gazeY: number;
  blink: number;
  mouthOpen: number;
};

type WorkerRequest =
  | { type: "init"; wasmRoot: string; modelPath: string }
  | { type: "frame"; frame: ImageBitmap; timestamp: number }
  | { type: "close" };

const scope = self as unknown as {
  postMessage(message: unknown): void;
  onmessage: ((event: MessageEvent<WorkerRequest>) => void) | null;
};

let landmarker: FaceLandmarker | null = null;

function clamp(value: number, minimum = -1, maximum = 1) {
  return Math.max(minimum, Math.min(maximum, value));
}

scope.onmessage = async (event) => {
  if (event.data.type === "init") {
    const originalConsoleError = console.error;
    console.error = (...args: unknown[]) => {
      if (typeof args[0] === "string" && args[0].startsWith("INFO: Created TensorFlow Lite")) console.info(...args);
      else originalConsoleError(...args);
    };
    try {
      const files = await FilesetResolver.forVisionTasks(event.data.wasmRoot);
      landmarker = await FaceLandmarker.createFromOptions(files, {
        baseOptions: { modelAssetPath: event.data.modelPath },
        runningMode: "VIDEO",
        numFaces: 1,
        outputFaceBlendshapes: true,
        outputFacialTransformationMatrixes: false,
        minFaceDetectionConfidence: 0.55,
        minFacePresenceConfidence: 0.55,
        minTrackingConfidence: 0.55,
      });
      scope.postMessage({ type: "ready" });
    } catch (error) {
      scope.postMessage({ type: "error", message: error instanceof Error ? error.message : "Perception initialization failed." });
    } finally {
      console.error = originalConsoleError;
    }
    return;
  }

  if (event.data.type === "close") {
    landmarker?.close();
    landmarker = null;
    return;
  }

  const { frame, timestamp } = event.data;
  try {
    if (!landmarker) return;
    const result = landmarker.detectForVideo(frame, timestamp);
    const landmarks = result.faceLandmarks[0];
    const categories = result.faceBlendshapes[0]?.categories ?? [];
    const values = new Map(categories.map((category) => [category.categoryName, category.score]));
    const center = landmarks?.[1];
    const signal: PerceptionSignal = {
      present: Boolean(center),
      gazeX: center ? clamp((center.x - 0.5) * 3.2) : 0,
      gazeY: center ? clamp((center.y - 0.45) * 3.2) : 0,
      blink: clamp(Math.max(values.get("eyeBlinkLeft") ?? 0, values.get("eyeBlinkRight") ?? 0), 0, 1),
      mouthOpen: clamp(values.get("jawOpen") ?? 0, 0, 1),
    };
    scope.postMessage({ type: "signal", signal });
  } catch (error) {
    scope.postMessage({ type: "error", message: error instanceof Error ? error.message : "Perception frame failed." });
  } finally {
    frame.close();
  }
};

export {};
