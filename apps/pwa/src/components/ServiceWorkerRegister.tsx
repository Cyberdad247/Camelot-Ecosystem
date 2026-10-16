// SPDX-License-Identifier: MIT
'use client';

import { useEffect } from 'react';

export function ServiceWorkerRegister() {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      window.addEventListener('load', () => {
        navigator.serviceWorker
          .register('/sw.js')
          .then((registration) => {
            console.log('[Sovereign SW] Registered with scope:', registration.scope);

            // Listen for waiting updates
            registration.onupdatefound = () => {
              const installingWorker = registration.installing;
              if (installingWorker) {
                installingWorker.onstatechange = () => {
                  if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    console.log('[Sovereign SW] New version available; refresh to activate.');
                  }
                };
              }
            };
          })
          .catch((error) => {
            console.error('[Sovereign SW] Registration failed:', error);
          });
      });
    }
  }, []);

  return null;
}
