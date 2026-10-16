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
            console.log('[Invisioned SW] Registered with scope:', registration.scope);
            registration.onupdatefound = () => {
              const installingWorker = registration.installing;
              if (installingWorker) {
                installingWorker.onstatechange = () => {
                  if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                    console.log('[Invisioned SW] New version ready.');
                  }
                };
              }
            };
          })
          .catch((error) => {
            console.error('[Invisioned SW] Registration error:', error);
          });
      });
    }
  }, []);

  return null;
}
