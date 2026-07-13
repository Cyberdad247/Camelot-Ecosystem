"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  Boxes,
  BrainCircuit,
  Check,
  ChevronRight,
  CircleAlert,
  Command,
  Download,
  Factory,
  Fingerprint,
  Gauge,
  Hammer,
  LoaderCircle,
  LogOut,
  Menu,
  MessageSquareText,
  Radio,
  ScanEye,
  Smartphone,
  Send,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";
import { startAuthentication, startRegistration } from "@simplewebauthn/browser";
import { AnyaPresence } from "@/components/anya-presence";
import { CartridgeMount, cartridgeManifests, manifestFor } from "@/cartridges/registry";
import type { CartridgeId } from "@/cartridges/types";
import type { Approval, CockpitEvent, CockpitStatus, CommandResponse } from "@/lib/cockpit-types";
import { cancelAnyaSpeech, primeAnyaVoices, speakAnya } from "@/lib/anya-voice";
import { synthesizeSpeech, currentTtsProvider, type TtsProvider } from "@/lib/tts-router";
import { readOfflineSnapshot, saveOfflineSnapshot } from "@/lib/offline-store";

type BeforeInstallPromptEvent = Event & {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

type OperatorSession = {
  required: boolean;
  configured: boolean;
  authenticated: boolean;
  local: boolean;
};

type PasskeyStatus = { configured: boolean; count: number };

const navIcons = {
  command: Command,
  factory: Factory,
  "forge-law": Hammer,
  intelligence: BrainCircuit,
  interphase: ScanEye,
  "device-hall": Smartphone,
  mesh: Boxes,
} as const;

const quickCommands = ["//STATUS", "//PLAN", "//ENGAGE_BIFROST", "//IGNITE_KNIGHTS"];

async function readJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.json() as Promise<T>;
}

function modeLabel(status: CockpitStatus | null, offlineCache: boolean) {
  if (offlineCache) return "cached edge state";
  if (!status) return "connecting";
  return status.mode;
}

function timeLabel(value?: string | null) {
  if (!value) return "--:--";
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? "--:--" : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function CockpitShell() {
  const composerRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<CockpitStatus | null>(null);
  const [events, setEvents] = useState<CockpitEvent[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [activeId, setActiveId] = useState<CartridgeId>("command");
  const [composer, setComposer] = useState("");
  const [busy, setBusy] = useState(false);
  const [offlineCache, setOfflineCache] = useState(false);
  const [voiceReplies, setVoiceReplies] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [session, setSession] = useState<OperatorSession | null>(null);
  const [pairingToken, setPairingToken] = useState("");
  const [pairingError, setPairingError] = useState("");
  const [passkeys, setPasskeys] = useState<PasskeyStatus>({ configured: false, count: 0 });
  const [passkeySupported, setPasskeySupported] = useState(false);
  const [transport, setTransport] = useState<{
    state: "offline" | "connecting" | "live" | "reconnecting";
    attempt: number;
    nextRetryMs: number | null;
  }>({ state: "offline", attempt: 0, nextRetryMs: null });
  const [conversation, setConversation] = useState<Array<{ role: "anya" | "operator"; text: string; ts: string; provider?: TtsProvider; providerLabel?: string }>>([
    { role: "anya", text: "Sovereign interphase online. Runtime claims are bound to local evidence.", ts: new Date().toISOString() },
  ]);
  const [ttsLabel, setTtsLabel] = useState<string>(() => {
    const provider = currentTtsProvider();
    if (provider === "multivoice") return "TTS: Multivoice";
    if (provider === "vendor-cloud") return "TTS: vendor cloud";
    return "TTS: browser synth";
  });
  const [ttsAudioCtx, setTtsAudioCtx] = useState<AudioContext | null>(null);
  const [ttsAudioSource, setTtsAudioSource] = useState<AudioBufferSourceNode | null>(null);
  const [bargeInSignal, setBargeInSignal] = useState(0);

  const activeManifest = useMemo(() => manifestFor(activeId), [activeId]);
  const pendingApprovals = approvals.filter((approval) => approval.status === "pending");
  const lowPower = (status?.telemetry.memoryPercent ?? 0) >= 85;

  async function refresh() {
    try {
      const [nextStatus, nextEvents, nextApprovals] = await Promise.all([
        readJson<CockpitStatus>("/api/status"),
        readJson<CockpitEvent[]>("/api/events"),
        readJson<Approval[]>("/api/approvals"),
      ]);
      setStatus(nextStatus);
      setEvents(nextEvents);
      setApprovals(nextApprovals);
      setOfflineCache(false);
      void saveOfflineSnapshot({ status: nextStatus, cachedAt: new Date().toISOString() });
    } catch {
      const cached = await readOfflineSnapshot().catch(() => null);
      if (cached) {
        setStatus({ ...cached.status, mode: "offline", stale: true, source: "indexeddb-edge-cache" });
        setEvents([{
          id: "offline-snapshot",
          ts: cached.cachedAt,
          level: "warn",
          source: "offline-cache",
          message: "Sanitized edge status loaded. Commands, events, and approvals are never retained offline.",
        }]);
        setApprovals([]);
        setOfflineCache(true);
      } else {
        setStatus(null);
        setOfflineCache(true);
      }
    }
  }

  async function loadSession() {
    try {
      const [nextSession, nextPasskeys] = await Promise.all([
        readJson<OperatorSession>("/api/session"),
        readJson<PasskeyStatus>("/api/passkeys"),
      ]);
      setSession(nextSession);
      setPasskeys(nextPasskeys);
    } catch {
      if (!navigator.onLine) {
        setSession({ required: false, configured: false, authenticated: true, local: true });
      } else {
        setSession({ required: true, configured: false, authenticated: false, local: false });
      }
    }
  }

  useEffect(() => {
    setPasskeySupported(typeof window.PublicKeyCredential !== "undefined");
    const query = new URLSearchParams(window.location.search).get("cartridge") as CartridgeId | null;
    if (query && cartridgeManifests.some((manifest) => manifest.id === query)) setActiveId(query);
    void loadSession();
  }, []);

  useEffect(() => () => cancelAnyaSpeech(), []);

  useEffect(() => {
    if (!session?.authenticated) return;
    void refresh();
    const timer = window.setInterval(() => void refresh(), 10000);
    return () => window.clearInterval(timer);
  }, [session?.authenticated]);

  useEffect(() => {
    if (!session?.authenticated || !navigator.onLine) {
      setTransport({ state: "offline", attempt: 0, nextRetryMs: null });
      return;
    }

    let closed = false;
    let stream: EventSource | null = null;
    let reconnectTimer: number | null = null;
    let attempt = 0;
    const retrySchedule = [3_000, 6_000, 12_000, 60_000];

    const connect = () => {
      if (closed) return;
      setTransport({ state: attempt === 0 ? "connecting" : "reconnecting", attempt, nextRetryMs: null });
      stream = new EventSource("/api/stream");
      stream.addEventListener("ready", () => {
        attempt = 0;
        setTransport({ state: "live", attempt: 0, nextRetryMs: null });
      });
      stream.addEventListener("cockpit-event", (message) => {
        const event = JSON.parse((message as MessageEvent<string>).data) as CockpitEvent;
        setEvents((current) => [event, ...current.filter((item) => item.id !== event.id)].slice(0, 100));
      });
      stream.onerror = () => {
        stream?.close();
        if (closed) return;
        attempt += 1;
        const delay = retrySchedule[Math.min(attempt - 1, retrySchedule.length - 1)];
        setTransport({ state: "reconnecting", attempt, nextRetryMs: delay });
        reconnectTimer = window.setTimeout(connect, delay);
      };
    };

    connect();
    return () => {
      closed = true;
      stream?.close();
      if (reconnectTimer !== null) window.clearTimeout(reconnectTimer);
      setTransport({ state: "offline", attempt: 0, nextRetryMs: null });
    };
  }, [session?.authenticated]);

  useEffect(() => {
    const captureInstall = (event: Event) => {
      event.preventDefault();
      setInstallPrompt(event as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", captureInstall);
    return () => window.removeEventListener("beforeinstallprompt", captureInstall);
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        composerRef.current?.focus();
      }
      if (event.key === "Escape") setMobileMenu(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  function selectCartridge(id: CartridgeId) {
    setActiveId(id);
    setMobileMenu(false);
    const url = new URL(window.location.href);
    url.searchParams.set("cartridge", id);
    window.history.replaceState({}, "", url);
  }

  async function speak(text: string) {
    if (!voiceReplies) return;
    setSpeaking(true);
    const result = await synthesizeSpeech(text);
    if (!result.ok) {
      setSpeaking(false);
      return;
    }
    setTtsLabel(result.label);
    // Tag the Anya message (the one that was just spoken) with the TTS
    // provider label. The for-loop scans backward from the most recent entry
    // to find the newest Anya message whose text matches the synthesized
    // text. Correlation IDs are a Phase 6 follow-up; the single-step reverse
    // scan is sufficient for the steady-state "one command, one response"
    // flow that the cockpit enforces via `setBusy` gates.
    setConversation((current) => {
      const next = [...current];
      for (let i = next.length - 1; i >= 0; i -= 1) {
        if (next[i].role === "anya" && next[i].text === text) {
          next[i] = { ...next[i], provider: result.provider, providerLabel: result.label };
          break;
        }
      }
      return next.slice(-10);
    });

    if (result.provider === "multivoice" && result.audio) {
      const ContextCtor = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!ContextCtor) {
        const label = `TTS: browser synth (fallback: AudioContext unavailable)`;
        setTtsLabel(label);
        fallbackToBrowserSynth(`${label}. ${result.spokenText}`);
        return;
      }
      try {
        const ctx = new ContextCtor();
        const buffer = await ctx.decodeAudioData(result.audio.slice(0));
        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.onended = () => {
          setSpeaking(false);
          setTtsAudioSource(null);
          void ctx.close();
          setTtsAudioCtx(null);
        };
        source.start();
        setTtsAudioCtx(ctx);
        setTtsAudioSource(source);
        return;
      } catch (error) {
        const reason = error instanceof Error ? error.message : "decode failed";
        const label = `TTS: browser synth (fallback: multivoice audio decode failed — ${reason})`;
        setTtsLabel(label);
        fallbackToBrowserSynth(`${label}. ${result.spokenText}`);
        return;
      }
    }

    // Consistent label prepending: every fallback path speaks the label
    // prefix so the operator hears the same TTS provider tag they see in
    // the Anya channel heading. The default browser-synth path (no
    // fallbackReason) speaks only the answer to avoid verbose prefixes on
    // the happy path.
    const prefix = result.fallbackReason
      ? `${result.label}. `
      : result.provider === "vendor-cloud"
        ? `${result.label}. `
        : "";
    fallbackToBrowserSynth(`${prefix}${result.spokenText}`);
  }

  function fallbackToBrowserSynth(text: string) {
    const started = speakAnya(text, {
      onStart: () => setSpeaking(true),
      onEnd: () => setSpeaking(false),
      onError: () => setSpeaking(false),
    });
    if (!started) setSpeaking(false);
  }

  function setSpokenReplies(enabled: boolean) {
    if (enabled) primeAnyaVoices();
    else cancelAnyaSpeech();
    setSpeaking(false);
    setVoiceReplies(enabled);
  }

  function bargeIn() {
    cancelAnyaSpeech();
    const ctx = ttsAudioCtx;
    const source = ttsAudioSource;
    setTtsAudioCtx(null);
    setTtsAudioSource(null);
    if (source) {
      try { source.stop(); } catch { /* already stopped */ }
    }
    if (ctx) {
      void ctx.close();
    }
    setSpeaking(false);
    // Phase 5: signal the presence component to flash the avatar state ring
    // through the "interrupted" state for 350ms before returning to "idle".
    // Natural end of speech (speakAnya onEnd) does NOT increment the signal.
    setBargeInSignal((current) => current + 1);
  }

  async function sendCommand(command: string) {
    const clean = command.trim();
    if (!clean || busy) return;
    setBusy(true);
    setConversation((current) => [...current.slice(-10), { role: "operator", text: clean, ts: new Date().toISOString() }]);
    try {
      const response = await fetch("/api/commands", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: clean, cartridge: activeId }),
      });
      const data = (await response.json()) as CommandResponse;
      if (!response.ok) throw new Error(data.message);
      setConversation((current) => [...current.slice(-10), { role: "anya", text: data.message, ts: new Date().toISOString() }]);
      speak(data.message);
      setComposer("");
      await refresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Command handoff failed.";
      setConversation((current) => [...current.slice(-10), { role: "anya", text: message, ts: new Date().toISOString() }]);
    } finally {
      setBusy(false);
    }
  }

  // The TTS provider is captured once at mount so the Anya channel heading
  // shows the operator which backend is currently serving voice replies.
  const ttsProvider = currentTtsProvider();

  async function resolveApproval(approval: Approval, decision: "approved" | "rejected") {
    if (busy) return;
    setBusy(true);
    try {
      const response = await fetch(`/api/approvals/${approval.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision }),
      });
      const data = (await response.json()) as CommandResponse;
      if (!response.ok) throw new Error(data.message);
      setConversation((current) => [...current.slice(-10), { role: "anya", text: data.message, ts: new Date().toISOString() }]);
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function installApp() {
    if (!installPrompt) return;
    await installPrompt.prompt();
    await installPrompt.userChoice;
    setInstallPrompt(null);
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void sendCommand(composer);
  }

  async function pairOperator(event: FormEvent) {
    event.preventDefault();
    if (!pairingToken.trim() || busy) return;
    setBusy(true);
    setPairingError("");
    try {
      const response = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: pairingToken }),
      });
      const data = (await response.json()) as { authenticated?: boolean; message?: string };
      if (!response.ok || !data.authenticated) throw new Error(data.message ?? "Pairing failed.");
      setPairingToken("");
      await loadSession();
    } catch (error) {
      setPairingError(error instanceof Error ? error.message : "Pairing failed.");
    } finally {
      setBusy(false);
    }
  }

  async function authenticateWithPasskey() {
    if (busy) return;
    setBusy(true);
    setPairingError("");
    try {
      const optionsResponse = await fetch("/api/passkeys/authenticate/options", { method: "POST" });
      const options = await optionsResponse.json();
      if (!optionsResponse.ok) throw new Error(options.message ?? "Passkey authentication could not start.");
      const credential = await startAuthentication({ optionsJSON: options });
      const verification = await fetch("/api/passkeys/authenticate/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credential),
      });
      const result = await verification.json() as { verified?: boolean; message?: string };
      if (!verification.ok || !result.verified) throw new Error(result.message ?? "Passkey authentication failed.");
      await loadSession();
    } catch (error) {
      setPairingError(error instanceof Error ? error.message : "Passkey authentication failed.");
    } finally {
      setBusy(false);
    }
  }

  async function enrollPasskey() {
    if (busy) return;
    setBusy(true);
    setPairingError("");
    try {
      const optionsResponse = await fetch("/api/passkeys/register/options", { method: "POST" });
      const options = await optionsResponse.json();
      if (!optionsResponse.ok) throw new Error(options.message ?? "Passkey enrollment could not start.");
      const credential = await startRegistration({ optionsJSON: options });
      const verification = await fetch("/api/passkeys/register/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credential),
      });
      const result = await verification.json() as { verified?: boolean; message?: string };
      if (!verification.ok || !result.verified) throw new Error(result.message ?? "Passkey enrollment failed.");
      setPasskeys((current) => ({ configured: true, count: current.count + 1 }));
    } catch (error) {
      setPairingError(error instanceof Error ? error.message : "Passkey enrollment failed.");
    } finally {
      setBusy(false);
    }
  }

  async function signOut() {
    await fetch("/api/session", { method: "DELETE" }).catch(() => null);
    setStatus(null);
    setEvents([]);
    setApprovals([]);
    setSession((current) => ({ required: true, configured: current?.configured ?? true, authenticated: false, local: current?.local ?? false }));
  }

  if (!session) {
    return (
      <main className="session-gate" aria-live="polite">
        <span className="brand-mark">A</span>
        <p className="eyebrow">Camelot OS</p>
        <h1>Establishing operator boundary</h1>
        <LoaderCircle className="spin" aria-hidden="true" />
      </main>
    );
  }

  if (!session.authenticated) {
    return (
      <main className="session-gate">
        <span className="brand-mark">A</span>
        <p className="eyebrow">Zero-trust edge</p>
        <h1>Authenticate operator</h1>
        <p className="session-copy">
          {passkeys.configured
            ? "Use this device's passkey to enter the sovereign cockpit."
            : "Bootstrap this cockpit once with its local recovery token, then enroll a passkey."}
        </p>
        {passkeys.configured && passkeySupported ? (
          <button className="passkey-primary" type="button" onClick={() => void authenticateWithPasskey()} disabled={busy}>
            {busy ? <LoaderCircle className="spin" /> : <Fingerprint />}<span>Continue with passkey</span>
          </button>
        ) : null}
        {session.configured ? (
          <details className="recovery-access" open={!passkeys.configured || !passkeySupported}>
            <summary>{passkeys.configured ? "Use recovery token" : "Bootstrap with recovery token"}</summary>
            <form className="pairing-form" onSubmit={pairOperator}>
              <label htmlFor="operator-token">Recovery token</label>
              <div>
                <input id="operator-token" type="password" value={pairingToken} onChange={(event) => setPairingToken(event.target.value)} autoComplete="current-password" minLength={16} />
                <button type="submit" aria-label="Authenticate with recovery token" disabled={busy || pairingToken.length < 16}>{busy ? <LoaderCircle className="spin" /> : <ShieldCheck />}</button>
              </div>
            </form>
          </details>
        ) : <p className="pairing-error" role="alert">Recovery authentication is not configured on this host.</p>}
        {pairingError ? <p className="pairing-error" role="alert">{pairingError}</p> : null}
      </main>
    );
  }

  return (
    <div className={lowPower ? "cockpit-shell resource-constrained" : "cockpit-shell"}>
      <header className="topbar">
        <button className="mobile-menu-button icon-button" type="button" onClick={() => setMobileMenu(true)} aria-label="Open cartridge navigation"><Menu /></button>
        <div className="brand-lockup">
          <span className="brand-mark">A</span>
          <div><strong>ANYA</strong><small>Camelot OS · Edge Interphase</small></div>
        </div>
        <div className="phase-rail" aria-label="Execution phase">
          <span className="phase-complete"><Check /> Assimilate</span>
          <ChevronRight />
          <span className="phase-active"><LoaderCircle /> Forge</span>
          <ChevronRight />
          <span>Validate</span>
        </div>
        <div className="topbar-actions">
          {installPrompt && <button className="install-button" type="button" onClick={() => void installApp()}><Download /> Install</button>}
          <div className={`connection-chip mode-${status?.mode ?? "offline"}`}><span />{modeLabel(status, offlineCache)}</div>
          <button className="session-action icon-button" type="button" onClick={() => void signOut()} aria-label="Sign out" title="Sign out"><LogOut /></button>
        </div>
      </header>

      <nav className={mobileMenu ? "rail-nav rail-nav-open" : "rail-nav"} aria-label="Cartridge navigation">
        <div className="mobile-nav-heading"><strong>Cartridges</strong><button className="icon-button" type="button" onClick={() => setMobileMenu(false)} aria-label="Close navigation"><X /></button></div>
        {cartridgeManifests.map((manifest) => {
          const Icon = navIcons[manifest.id];
          return (
            <button key={manifest.id} type="button" className={activeId === manifest.id ? "rail-button active" : "rail-button"} onClick={() => selectCartridge(manifest.id)} aria-current={activeId === manifest.id ? "page" : undefined} title={manifest.label}>
              <Icon aria-hidden="true" /><span>{manifest.shortLabel}</span>
              {manifest.id === "command" && pendingApprovals.length > 0 && <b>{pendingApprovals.length}</b>}
            </button>
          );
        })}
        <div className="rail-spacer" />
        <div className="rail-health" title="Live services"><Gauge /><span>{status?.services.filter((service) => service.status === "online").length ?? 0}</span></div>
        <button className="rail-signout" type="button" onClick={() => void signOut()}><LogOut aria-hidden="true" /><span>Sign out</span></button>
      </nav>
      {mobileMenu && <button className="nav-scrim" type="button" onClick={() => setMobileMenu(false)} aria-label="Close navigation" />}

      <main className="workspace" id="workspace">
        <section className="workspace-heading">
          <div>
            <p className="eyebrow">{activeManifest.phaseGlyph} · {activeManifest.lead}</p>
            <h1>{activeManifest.label}</h1>
            <p>{activeManifest.description}</p>
          </div>
          <div className="workspace-meta"><span>Source</span><strong>{status?.source ?? "connecting"}</strong><small>{status?.stale ? `stale · ${status.ageSeconds ?? "?"}s` : `updated ${timeLabel(status?.updatedAt)}`}</small></div>
        </section>

        {status?.warnings.length ? (
          <div className="warning-rail" role="status"><CircleAlert /> <span>{status.warnings.join(" ")}</span></div>
        ) : null}

        {!passkeys.configured && passkeySupported ? (
          <section className="passkey-enrollment" aria-labelledby="passkey-enrollment-title">
            <Fingerprint aria-hidden="true" />
            <div><p className="eyebrow">Operator security</p><h2 id="passkey-enrollment-title">Create a passkey</h2></div>
            <button type="button" onClick={() => void enrollPasskey()} disabled={busy}>{busy ? <LoaderCircle className="spin" /> : <Fingerprint />} Enroll device</button>
          </section>
        ) : null}

        <AnyaPresence mode={status?.mode ?? "offline"} busy={busy} speaking={speaking} voiceReplies={voiceReplies} lowPower={lowPower} bargeInSignal={bargeInSignal} onVoiceReplies={setSpokenReplies} onBargeIn={bargeIn} onTranscript={setComposer} />

        <CartridgeMount id={activeId} status={status} events={events} onCommand={sendCommand} onInterrupt={bargeIn} busy={busy} transport={transport} />

        <section className="conversation-strip" aria-labelledby="conversation-title">
          <div className="conversation-heading"><MessageSquareText /><div><p className="eyebrow">Shared state</p><h2 id="conversation-title">Anya channel</h2><small className="tts-provider" data-provider={ttsProvider} title={ttsLabel}>{ttsLabel}</small></div></div>
          <div className="conversation-feed" aria-live="polite">
            {conversation.slice(-4).map((message, index) => (
              <div className={`message message-${message.role}`} key={`${message.ts}-${index}`}>
                <span>{message.role === "anya" ? "A" : "You"}</span><p>{message.text}</p><time>{timeLabel(message.ts)}</time>
                {message.providerLabel ? <small className="tts-tag" data-provider={message.provider}>{message.providerLabel}</small> : null}
              </div>
            ))}
          </div>
        </section>

        <form className="command-composer" onSubmit={submit}>
          <Sparkles aria-hidden="true" />
          <label className="sr-only" htmlFor="anya-command">Message or command for Anya</label>
          <input id="anya-command" ref={composerRef} value={composer} onChange={(event) => setComposer(event.target.value)} placeholder="Ask Anya or enter a runic directive" autoComplete="off" maxLength={1200} />
          <div className="quick-command-row">
            {quickCommands.map((command) => <button type="button" key={command} onClick={() => setComposer(command)}>{command.replace("//", "")}</button>)}
          </div>
          <button className="send-button" type="submit" disabled={busy || !composer.trim()} aria-label="Send to Anya">{busy ? <LoaderCircle className="spin" /> : <Send />}</button>
        </form>
      </main>

      <aside className="context-rail" aria-label="Operational context">
        <section className="context-section trace-section">
          <div className="context-heading"><div><p className="eyebrow">Transparency</p><h2>Thought trace</h2></div><Activity /></div>
          <div className="trace-list">
            {events.slice(0, 6).map((event, index) => (
              <div key={event.id}><span className={`event-mark event-${event.level}`} /> <time>{timeLabel(event.ts)}</time><div><strong>{index === 0 ? "[EXECUTE]" : "[VALIDATE]"} {event.source}</strong><p>{event.message}</p></div></div>
            ))}
            {events.length === 0 && <p className="empty-state">Waiting for local event evidence.</p>}
          </div>
        </section>

        <section className="context-section approval-section">
          <div className="context-heading"><div><p className="eyebrow">Iron Gate</p><h2>Approvals</h2></div><ShieldCheck /></div>
          {pendingApprovals.length === 0 ? (
            <div className="approval-clear"><Check /><div><strong>Queue clear</strong><small>No mutation awaiting consent</small></div></div>
          ) : pendingApprovals.slice(0, 2).map((approval) => (
            <div className="approval-item" key={approval.id}>
              <strong>{approval.command}</strong><p>{approval.reason}</p>
              <div><button type="button" onClick={() => void resolveApproval(approval, "rejected")} disabled={busy}>Reject</button><button type="button" onClick={() => void resolveApproval(approval, "approved")} disabled={busy}>Approve</button></div>
            </div>
          ))}
        </section>

        <section className="context-section system-section">
          <div className="context-heading"><div><p className="eyebrow">Edge substrate</p><h2>Resource guard</h2></div><Radio /></div>
          <div className="resource-row"><span>Memory</span><div><i style={{ width: `${Math.min(100, status?.telemetry.memoryPercent ?? 0)}%` }} /></div><strong>{status?.telemetry.memoryPercent ?? "--"}%</strong></div>
          <div className="resource-row"><span>CPU</span><div><i style={{ width: `${Math.min(100, status?.telemetry.cpuPercent ?? 0)}%` }} /></div><strong>{status?.telemetry.cpuPercent ?? "--"}%</strong></div>
          <div className="context-facts"><span>Bio cells <strong>{status?.telemetry.swarmCells ?? 0}</strong></span><span>Cloud Brain <strong>{status?.capabilities.cloudbrain ?? "offline"}</strong></span><span>Command adapter <strong>{status?.capabilities.commandExecution ?? "record-only"}</strong></span></div>
        </section>
      </aside>

      <nav className="mobile-bottom-nav" aria-label="Mobile cartridge navigation">
        {cartridgeManifests.map((manifest) => {
          const Icon = navIcons[manifest.id];
          return <button key={manifest.id} type="button" className={activeId === manifest.id ? "active" : ""} onClick={() => selectCartridge(manifest.id)}><Icon /><span>{manifest.shortLabel}</span></button>;
        })}
      </nav>
    </div>
  );
}
