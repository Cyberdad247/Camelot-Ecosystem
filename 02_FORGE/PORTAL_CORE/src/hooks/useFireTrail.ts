// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { useScroll, useSpring, useTransform } from 'framer-motion';
import { useRef } from 'react';

export const useFireTrail = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });

  // Physics: Smooth out the scroll jitter for "liquid" feel
  const smoothScroll = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  // Color Interpolation: Earth (Magma) -> Atmosphere (Purple) -> Space (Neon)
  const fireColor = useTransform(
    smoothScroll,
    [0, 0.4, 0.8, 1],
    ['#FF4500', '#8B0000', '#4B0082', '#00FF99'],
  );

  // Width Physics: Ragged Flame (Wide) -> Laser Beam (Thin)
  const fireWidth = useTransform(smoothScroll, [0, 0.3, 1], ['4px', '8px', '2px']);

  // Glow Intensity: Pulse increases as we ascend
  const fireGlow = useTransform(
    smoothScroll,
    [0, 1],
    ['0px 0px 15px rgba(255, 69, 0, 0.6)', '0px 0px 30px rgba(0, 255, 153, 0.9)'],
  );

  return { containerRef, fireColor, fireWidth, fireGlow };
};
