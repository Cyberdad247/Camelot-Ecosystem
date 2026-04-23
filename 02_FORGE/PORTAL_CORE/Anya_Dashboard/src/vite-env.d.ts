/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_HOME_ROUTE?: string;
  readonly VITE_ANYA_VISUAL_CONTEXT_URL?: string;
  readonly VITE_CLOUD_BRAIN_URL?: string;
  readonly VITE_BIFROST_HTTP_URL?: string;
  readonly VITE_BIFROST_WS_URL?: string;
  readonly VITE_BIFROST_TOKEN?: string;
  readonly VITE_GRADIO_URL?: string;
  readonly VITE_SALTARE_ROUTE_URL?: string;
  readonly VITE_ROTEL_STREAM_URL?: string;
  readonly VITE_KINETIC_TOKEN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
