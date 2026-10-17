/**
 * Sovereign Web Haptics Engine for Edge Devices (Samsung S26 Ultra Target)
 * Provides tactile feedback for button taps, switches, errors, and biometric locks.
 */

export type HapticPattern = 'tick' | 'tap' | 'success' | 'warning' | 'error' | 'heavy';

export const triggerHaptic = (pattern: HapticPattern = 'tick'): void => {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return;
  }

  if (!('vibrate' in navigator)) {
    return;
  }

  try {
    switch (pattern) {
      case 'tick':
        // 8ms micro-pulse for fast list navigation / slider ticks
        navigator.vibrate(8);
        break;
      case 'tap':
        // 14ms crisp tap for buttons and toggles
        navigator.vibrate(14);
        break;
      case 'success':
        // Two-stroke rhythm for verification and cryptographic seals
        navigator.vibrate([12, 25, 20]);
        break;
      case 'warning':
        // Triple vibration pulse for memory / resource alerts
        navigator.vibrate([40, 30, 40]);
        break;
      case 'error':
        // Staccato vibration for unauthorized access / failed assertions
        navigator.vibrate([50, 40, 50, 40, 60]);
        break;
      case 'heavy':
        // Heavy impact for vault locks and sovereign shutdowns
        navigator.vibrate(70);
        break;
    }
  } catch {
    // Ignore unsupported environment exceptions silently
  }
};
