import { useEffect, useState } from 'react';

export type DisplayClass = 'handheld' | 'tablet' | 'console' | 'wall';

export interface DisplayProfile {
  width: number;
  height: number;
  dpr: number;
  touch: boolean;
  reducedMotion: boolean;
  lowHeight: boolean;
  displayClass: DisplayClass;
  compact: boolean;
}

function readDisplayProfile(): DisplayProfile {
  if (typeof window === 'undefined') {
    return {
      width: 1440,
      height: 900,
      dpr: 1,
      touch: false,
      reducedMotion: false,
      lowHeight: false,
      displayClass: 'console',
      compact: false,
    };
  }

  const safeMatchMedia = (query: string) => {
    if (typeof window.matchMedia !== 'function') {
      return { matches: false } as MediaQueryList;
    }
    return window.matchMedia(query);
  };

  const width = window.innerWidth;
  const height = window.innerHeight;
  const dpr = window.devicePixelRatio || 1;
  const touch = safeMatchMedia('(pointer: coarse)').matches;
  const reducedMotion = safeMatchMedia('(prefers-reduced-motion: reduce)').matches;
  const lowHeight = height < 760;
  const displayClass: DisplayClass =
    width < 720 ? 'handheld' : width < 1120 ? 'tablet' : width >= 1920 && height >= 980 ? 'wall' : 'console';

  return {
    width,
    height,
    dpr,
    touch,
    reducedMotion,
    lowHeight,
    displayClass,
    compact: displayClass === 'handheld' || lowHeight,
  };
}

export function useDisplayProfile() {
  const [profile, setProfile] = useState<DisplayProfile>(() => readDisplayProfile());

  useEffect(() => {
    const update = () => setProfile(readDisplayProfile());
    update();
    window.addEventListener('resize', update);
    window.addEventListener('orientationchange', update);
    return () => {
      window.removeEventListener('resize', update);
      window.removeEventListener('orientationchange', update);
    };
  }, []);

  return profile;
}
