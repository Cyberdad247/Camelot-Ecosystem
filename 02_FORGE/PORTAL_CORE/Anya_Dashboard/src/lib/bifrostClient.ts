import { runtimeConfig } from '@/config/runtime';

export function bifrostHeaders(init?: HeadersInit) {
  const headers = new Headers(init);
  if (runtimeConfig.bifrost.token) {
    headers.set('Authorization', `Bearer ${runtimeConfig.bifrost.token}`);
    headers.set('x-camelot-token', runtimeConfig.bifrost.token);
  }
  return headers;
}

export function bifrostFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  return fetch(input, {
    ...init,
    headers: bifrostHeaders(init.headers),
  });
}

export function bifrostWebSocketUrl(url = runtimeConfig.bifrost.websocketUrl) {
  if (!runtimeConfig.bifrost.token) return url;
  const next = new URL(url);
  next.searchParams.set('token', runtimeConfig.bifrost.token);
  return next.toString();
}
