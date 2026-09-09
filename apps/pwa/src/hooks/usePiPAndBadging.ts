// SPDX-License-Identifier: MIT

'use client';

import { useCallback, useEffect, useState } from 'react';

/**
 * usePiPAndBadging — Picture-in-Picture (PiP) and OS App Badging API hook.
 * Assimilated from Cyberdad247/kba-v.3 & vuejs-templates/pwa.
 * Provides Document Picture-in-Picture window for persistent avatar execution
 * and App Badging to indicate active Bifrost tasks/notifications on OS app icons.
 */
export function usePiPAndBadging() {
  const [isPiPActive, setIsPiPActive] = useState(false);
  const [pipSupported, setPipSupported] = useState(false);
  const [badgeSupported, setBadgeSupported] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setPipSupported('documentPictureInPicture' in window);
      setBadgeSupported('setAppBadge' in navigator);
    }
  }, []);

  // App Badging API (sets unread count or indicator on OS app icon/dock)
  const setBadge = useCallback(async (count?: number) => {
    if (typeof navigator !== 'undefined' && 'setAppBadge' in navigator) {
      try {
        if (count !== undefined && count > 0) {
          await (navigator as unknown as { setAppBadge: (c: number) => Promise<void> }).setAppBadge(count);
        } else {
          await (navigator as unknown as { clearAppBadge: () => Promise<void> }).clearAppBadge();
        }
      } catch {
        // Restricted context or user preference guard
      }
    }
  }, []);

  const clearBadge = useCallback(async () => {
    if (typeof navigator !== 'undefined' && 'clearAppBadge' in navigator) {
      try {
        await (navigator as unknown as { clearAppBadge: () => Promise<void> }).clearAppBadge();
      } catch {
        // Guard
      }
    }
  }, []);

  // Request Document Picture-in-Picture window for Avatar Knight / Lakeisha
  const requestPiP = useCallback(async (title = 'Lakeisha Enclave Cockpit') => {
    if (typeof window !== 'undefined' && 'documentPictureInPicture' in window) {
      try {
        const pipWindow = await (
          window as unknown as {
            documentPictureInPicture: {
              requestWindow: (options: { width: number; height: number }) => Promise<Window>;
            };
          }
        ).documentPictureInPicture.requestWindow({
          width: 380,
          height: 520,
        });

        if (pipWindow) {
          pipWindow.document.title = title;
          pipWindow.document.body.innerHTML = `
            <div style="background:#050507;color:#ffffff;font-family:-apple-system,BlinkMacSystemFont,sans-serif;padding:20px;text-align:center;height:100vh;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;justify-content:center;border:1px solid #D4AF37;">
              <div style="font-size:44px;margin-bottom:12px;filter:drop-shadow(0 0 10px #D4AF37);">⚔️</div>
              <h2 style="color:#D4AF37;margin:0 0 6px 0;font-size:16px;letter-spacing:0.12em;text-transform:uppercase;">Lakeisha Video Enclave</h2>
              <p style="color:rgba(255,255,255,0.6);font-size:12px;margin:0 0 16px 0;">Sovereign Persistent Companion</p>
              <div style="padding:8px 16px;background:rgba(212,175,55,0.1);border:1px solid #D4AF37;border-radius:999px;font-size:11px;color:#D4AF37;letter-spacing:0.08em;">
                ● Bifröst Listening Active
              </div>
            </div>
          `;
          setIsPiPActive(true);
          pipWindow.addEventListener('pagehide', () => setIsPiPActive(false));
          return pipWindow;
        }
      } catch (err) {
        console.warn('[PiP] Document PiP request rejected or cancelled:', err);
      }
    }
    setIsPiPActive((prev) => !prev);
    return null;
  }, []);

  return {
    isPiPActive,
    pipSupported,
    badgeSupported,
    requestPiP,
    setBadge,
    clearBadge,
  };
}
