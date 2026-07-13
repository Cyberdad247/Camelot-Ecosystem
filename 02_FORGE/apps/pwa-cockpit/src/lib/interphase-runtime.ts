export type InterphaseRuntimeProfile = {
  deviceClass: "mobile" | "tablet" | "desktop";
  motionMode: "full-motion" | "reduced-motion" | "poster-only";
  objectPosition: string;
  reasons: string[];
};

export type InterphaseRuntimeInput = {
  width: number;
  height: number;
  devicePixelRatio?: number;
  hardwareConcurrency?: number;
  saveData?: boolean;
  prefersReducedMotion?: boolean;
};

export function resolveInterphaseRuntime(input: InterphaseRuntimeInput): InterphaseRuntimeProfile {
  const deviceClass = input.width < 640 ? "mobile" : input.width < 1024 ? "tablet" : "desktop";
  const reasons: string[] = [];
  if (input.prefersReducedMotion) reasons.push("reduced-motion");
  if (input.saveData) reasons.push("save-data");
  if ((input.hardwareConcurrency ?? 4) <= 4) reasons.push("limited-cpu");
  if ((input.devicePixelRatio ?? 1) > 2.25 && input.width < 480) reasons.push("dense-mobile-display");

  const motionMode = input.prefersReducedMotion
    ? "poster-only"
    : reasons.length > 0
      ? "reduced-motion"
      : "full-motion";

  return {
    deviceClass,
    motionMode,
    objectPosition: input.height < 760 || deviceClass === "mobile" ? "50% 18%" : "50% 22%",
    reasons,
  };
}

export function browserInterphaseRuntime(): InterphaseRuntimeProfile {
  const connection = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection;
  return resolveInterphaseRuntime({
    width: window.innerWidth,
    height: window.innerHeight,
    devicePixelRatio: window.devicePixelRatio,
    hardwareConcurrency: navigator.hardwareConcurrency,
    saveData: connection?.saveData,
    prefersReducedMotion: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  });
}
