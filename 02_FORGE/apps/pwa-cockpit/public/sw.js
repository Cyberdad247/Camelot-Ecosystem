const VERSION = "anya-cockpit-4cce61e2cf9b";
const SHELL_CACHE = `${VERSION}-shell`;
const ASSET_CACHE = `${VERSION}-assets`;
const SHELL = ["/", "/offline.html", "/manifest.json", "/icon.svg", "/icon-192.png", "/icon-512.png", "/anya.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => !key.startsWith(VERSION)).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("message", (event) => {
  if (event.data?.type !== "CACHE_RESOURCES" || !Array.isArray(event.data.urls)) return;
  const urls = event.data.urls.filter((value) => {
    if (typeof value !== "string") return false;
    const url = new URL(value, self.location.origin);
    return url.origin === self.location.origin && !url.pathname.startsWith("/api/");
  });
  event.waitUntil(
    caches.open(ASSET_CACHE).then((cache) => cache.addAll(urls)).then(() => {
      event.ports[0]?.postMessage({ type: "CACHE_RESOURCES_COMPLETE", count: urls.length });
    }),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.startsWith("/api/")) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) caches.open(SHELL_CACHE).then((cache) => cache.put(request, response.clone()));
          return response;
        })
        .catch(async () => (await caches.match(request)) || (await caches.match("/")) || caches.match("/offline.html")),
    );
    return;
  }

  if (["script", "style", "image", "font"].includes(request.destination)) {
    event.respondWith(
      caches.match(request).then(async (cached) => {
        const network = fetch(request).then(async (response) => {
          if (response.ok) {
            const cache = await caches.open(ASSET_CACHE);
            await cache.put(request, response.clone());
          }
          return response;
        });
        if (cached) {
          event.waitUntil(network.catch(() => undefined));
          return cached;
        }
        return network;
      }),
    );
  }
});
