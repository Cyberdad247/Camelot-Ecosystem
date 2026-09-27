// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { useEffect, useState } from 'react';

export const useCamelotNetwork = () => {
  const [status, setStatus] = useState<'EARTH' | 'SKY' | 'OFFLINE'>('OFFLINE');

  const checkPulse = async () => {
    try {
      // Ping Morgana (Local Tunnel / Localhost)
      const res = await fetch('http://localhost:8001/ping');
      if (res.ok) {
        setStatus('EARTH');
      } else {
        throw new Error('Morgana Unreachable');
      }
    } catch {
      // Fallback: Check if we have internet at least
      setStatus(navigator.onLine ? 'SKY' : 'OFFLINE');
    }
  };

  useEffect(() => {
    checkPulse();
    const interval = setInterval(checkPulse, 5000); // Check every 5s
    return () => clearInterval(interval);
  }, []);

  return status;
};
