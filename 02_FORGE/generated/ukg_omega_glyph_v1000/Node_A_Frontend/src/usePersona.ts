import { useEffect, useState } from 'react';

export interface PersonaFrame {
  jawOpen: number;
  smile: number;
  blink: number;
  headYaw: number;
  headPitch: number;
}

export const DEFAULT_PERSONA_FRAME: PersonaFrame = {
  jawOpen: 0.12,
  smile: 0.18,
  blink: 0,
  headYaw: 0,
  headPitch: 0,
};

export function lerpPersonaFrame(
  previous: PersonaFrame,
  next: PersonaFrame,
  alpha: number,
): PersonaFrame {
  const mix = (a: number, b: number) => a + (b - a) * alpha;
  return {
    jawOpen: mix(previous.jawOpen, next.jawOpen),
    smile: mix(previous.smile, next.smile),
    blink: mix(previous.blink, next.blink),
    headYaw: mix(previous.headYaw, next.headYaw),
    headPitch: mix(previous.headPitch, next.headPitch),
  };
}

export function usePersona(targetFrame = DEFAULT_PERSONA_FRAME) {
  const [frame, setFrame] = useState<PersonaFrame>(targetFrame);

  useEffect(() => {
    let animationFrame = 0;

    const tick = () => {
      setFrame((current) => lerpPersonaFrame(current, targetFrame, 0.22));
      animationFrame = window.requestAnimationFrame(tick);
    };

    animationFrame = window.requestAnimationFrame(tick);
    return () => window.cancelAnimationFrame(animationFrame);
  }, [targetFrame]);

  return frame;
}
