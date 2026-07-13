// Phase 5: TTS router.
//
// Priority chain:
//   1. Multivoice (Camelot Anya_Ω governed compiler) — only when the configured
//      NEXT_PUBLIC_MULTIVOICE_URL is a loopback or Tailscale host. Mirrors the
//      trusted-host check from Kickbox-audio/apps/mcp-query/src/query.ts so the
//      PWA and the MCP server agree on what counts as a safe hop.
//   2. Vendor-cloud fallback (OpenAI TTS stub) — only when
//      NEXT_PUBLIC_TTS_VENDOR_FALLBACK === "on". The router returns a labeled
//      marker; the cockpit shell's speak() function speaks the label through
//      browser-synth so the operator hears "TTS: vendor cloud (openai) —
//      fallback: multivoice unreachable" when audio leaves the local trust
//      boundary. Phase 5 does not POST to the vendor; that is wired up when a
//      vendor key + endpoint env are configured.
//   3. Browser speechSynthesis — the existing speakAnya() path, last resort.
//
// The visible provider label is the security property. Every code path
// returns one of: "multivoice", "vendor-cloud", "browser-synth" and a
// human-readable label so the Anya channel UI can show the operator which
// backend produced the current audio.

import { spokenSummary } from "./anya-voice";

export type TtsProvider = "multivoice" | "vendor-cloud" | "browser-synth";

export type TtsResult =
  | {
      ok: true;
      provider: TtsProvider;
      label: string;
      fallbackReason?: string;
      audio?: ArrayBuffer | null;
      spokenText: string;
    }
  | {
      ok: false;
      reason: string;
      provider: TtsProvider;
    };

export type SynthesizeOptions = {
  voice?: string;
  urgency?: "normal" | "high";
  timeoutMs?: number;
  fetchImpl?: typeof fetch;
};

// Mirrors Kickbox-audio/apps/mcp-query/src/query.ts isTrustedHost exactly so
// the PWA and the mcp-query server agree on the same Tailscale + CGNAT ranges.
const TS_CGNAT = /^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}$/;

export function isTrustedTtsHost(host: string): boolean {
  return (
    host === "localhost" ||
    host === "127.0.0.1" ||
    host === "::1" ||
    /\.ts\.net$/i.test(host) ||
    TS_CGNAT.test(host)
  );
}

function readMultivoiceUrl(): string | null {
  const raw = process.env.NEXT_PUBLIC_MULTIVOICE_URL?.trim();
  if (!raw) return null;
  try {
    const parsed = new URL(raw);
    if (!isTrustedTtsHost(parsed.hostname)) return null;
    return parsed.toString();
  } catch {
    return null;
  }
}

function readVendorFallbackEnabled(): boolean {
  return process.env.NEXT_PUBLIC_TTS_VENDOR_FALLBACK === "on";
}

function readVendorUrl(): string | null {
  const raw = process.env.NEXT_PUBLIC_TTS_VENDOR_URL?.trim();
  if (!raw) return null;
  try {
    return new URL(raw).toString();
  } catch {
    return null;
  }
}

async function multivoiceSynthesize(
  text: string,
  endpoint: string,
  opts: SynthesizeOptions,
): Promise<TtsResult> {
  const doFetch = opts.fetchImpl ?? fetch;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), opts.timeoutMs ?? 800);
  try {
    const res = await doFetch(endpoint, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ utterance: text, query: text, voice: opts.voice }),
      signal: controller.signal,
    });
    if (!res.ok) {
      return { ok: false, provider: "multivoice", reason: `multivoice ${res.status}` };
    }
    const audio = await res.arrayBuffer().catch(() => null);
    return {
      ok: true,
      provider: "multivoice",
      label: "TTS: Multivoice",
      audio,
      spokenText: text,
    };
  } catch (error) {
    return {
      ok: false,
      provider: "multivoice",
      reason: error instanceof Error ? error.message : "multivoice unreachable",
    };
  } finally {
    clearTimeout(timer);
  }
}

export async function synthesizeSpeech(
  text: string,
  opts: SynthesizeOptions = {},
): Promise<TtsResult> {
  const spoken = spokenSummary(text);
  if (!spoken) {
    return { ok: false, provider: "browser-synth", reason: "spoken text was empty after summarization" };
  }

  const endpoint = readMultivoiceUrl();
  if (endpoint) {
    const result = await multivoiceSynthesize(spoken, endpoint, opts);
    if (result.ok) return result;
    // Multivoice failed. The visible label is the security property: we only
    // label the path "vendor-cloud" when a vendor URL is actually configured
    // so the operator is never told audio is going to a vendor when the
    // vendor wiring is missing in Phase 5.
    const vendorUrl = readVendorUrl();
    if (readVendorFallbackEnabled() && vendorUrl) {
      return {
        ok: true,
        provider: "vendor-cloud",
        label: `TTS: vendor cloud — fallback: multivoice unreachable (${result.reason})`,
        fallbackReason: result.reason,
        spokenText: spoken,
      };
    }
    return {
      ok: true,
      provider: "browser-synth",
      label: `TTS: browser synth (fallback: multivoice unreachable — ${result.reason}${readVendorFallbackEnabled() ? "; vendor-cloud not wired in Phase 5" : ""})`,
      fallbackReason: result.reason,
      spokenText: spoken,
    };
  }

  if (readVendorFallbackEnabled() && readVendorUrl()) {
    return {
      ok: true,
      provider: "vendor-cloud",
      label: "TTS: vendor cloud — fallback: multivoice not configured",
      fallbackReason: "multivoice-not-configured",
      spokenText: spoken,
    };
  }

  return {
    ok: true,
    provider: "browser-synth",
    label: "TTS: browser synth",
    spokenText: spoken,
  };
}

export function currentTtsProvider(): TtsProvider {
  if (readMultivoiceUrl()) return "multivoice";
  if (readVendorFallbackEnabled() && readVendorUrl()) return "vendor-cloud";
  return "browser-synth";
}
