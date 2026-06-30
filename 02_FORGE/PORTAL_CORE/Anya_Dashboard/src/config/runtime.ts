const env = import.meta.env;

function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, '');
}

function withDefault(value: string | undefined, fallback: string) {
  const clean = value?.trim();
  return clean ? clean : fallback;
}

function websocketFromHttp(origin: string) {
  if (origin.startsWith('https://')) return `wss://${origin.slice('https://'.length)}/ws`;
  if (origin.startsWith('http://')) return `ws://${origin.slice('http://'.length)}/ws`;
  return `${origin}/ws`;
}

const bridgeOrigin = trimTrailingSlash(withDefault(env.VITE_BIFROST_HTTP_URL, 'http://127.0.0.1:8001'));
const goRouterOrigin = trimTrailingSlash(withDefault(env.VITE_GO_ROUTER_URL, 'http://127.0.0.1:8077'));

export const runtimeConfig = {
  appHomeRoute: withDefault(env.VITE_APP_HOME_ROUTE, '/openviking'),
  visualContextUrl: withDefault(env.VITE_ANYA_VISUAL_CONTEXT_URL, 'https://en.m.wikipedia.org/wiki/Special:Random'),
  cloudBrainUrl: withDefault(
    env.VITE_CLOUD_BRAIN_URL,
    `${bridgeOrigin}/modal/cloud-brain`,
  ),
  bifrost: {
    origin: bridgeOrigin,
    statusUrl: `${bridgeOrigin}/bifrost/status`,
    dispatchUrl: `${bridgeOrigin}/agent/dispatch`,
    openVikingMapUrl: `${bridgeOrigin}/openviking/map`,
    websocketUrl: withDefault(env.VITE_BIFROST_WS_URL, websocketFromHttp(bridgeOrigin)),
    token: withDefault(env.VITE_BIFROST_TOKEN, ''),
  },
  goRouter: {
    origin: goRouterOrigin,
    eventsUrl: `${goRouterOrigin}/events`,
    runeUrl: `${goRouterOrigin}/rune`,
    healthUrl: `${goRouterOrigin}/healthz`,
  },
  // Cognitive Service (Graphify/MemCastle/sync), reached through go_router's
  // /cognitive/* reverse proxy so the dashboard only ever talks to one origin.
  cognitive: {
    fleetUrl: withDefault(env.VITE_COGNITIVE_FLEET_URL, `${goRouterOrigin}/cognitive/fleet`),
    healthUrl: withDefault(env.VITE_COGNITIVE_HEALTH_URL, `${goRouterOrigin}/cognitive/healthz`),
  },
  gradioUrl: withDefault(env.VITE_GRADIO_URL, 'http://localhost:7860/'),
  saltare: {
    routeUrl: withDefault(env.VITE_SALTARE_ROUTE_URL, 'http://localhost:8080/api/v1/route'),
    token: withDefault(env.VITE_KINETIC_TOKEN, 'camelot-kinetic-v300-auth-token'),
  },
  rotel: {
    streamUrl: withDefault(env.VITE_ROTEL_STREAM_URL, 'http://127.0.0.1:4317/v1/stream'),
    token: withDefault(env.VITE_KINETIC_TOKEN, 'camelot-kinetic-v300-auth-token'),
  },
};

export function tokenizedUrl(url: string, token: string) {
  if (!token) return url;
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}token=${encodeURIComponent(token)}`;
}
