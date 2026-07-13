"use client";

import { useEffect } from "react";
import { preloadTrustedCartridges } from "@/cartridges/registry";

export function PwaRuntime() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;

    const register = async () => {
      try {
        const registration = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
        await navigator.serviceWorker.ready;
        await preloadTrustedCartridges();
        const urls = performance
          .getEntriesByType("resource")
          .map((entry) => entry.name)
          .filter((url) => url.startsWith(window.location.origin) && !new URL(url).pathname.startsWith("/api/"));
        const worker = navigator.serviceWorker.controller ?? registration.active;
        if (!worker) throw new Error("No active service worker accepted the cartridge prewarm request.");
        const channel = new MessageChannel();
        await new Promise<void>((resolve, reject) => {
          const timeout = window.setTimeout(() => reject(new Error("Cartridge prewarm acknowledgement timed out.")), 10_000);
          channel.port1.onmessage = (event: MessageEvent<{ type?: string }>) => {
            if (event.data?.type !== "CACHE_RESOURCES_COMPLETE") return;
            window.clearTimeout(timeout);
            resolve();
          };
          worker.postMessage({ type: "CACHE_RESOURCES", urls: Array.from(new Set(urls)) }, [channel.port2]);
        });
        document.documentElement.dataset.pwaPrewarmed = "true";
      } catch (error) {
        console.warn("PWA service worker registration failed", error);
      }
    };

    void register();
  }, []);

  return null;
}
