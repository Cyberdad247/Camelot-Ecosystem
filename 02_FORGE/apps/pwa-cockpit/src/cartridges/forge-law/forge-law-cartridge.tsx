"use client";

import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, CircleAlert, FileCode2, Hammer, LoaderCircle, Play, RefreshCw, ShieldCheck } from "lucide-react";
import type { CartridgeProps } from "../types";
import type { ForgeCartridge } from "@/lib/forge-law";

const executableStates = new Set(["validated", "awaiting_approval", "failed", "rolled_back"]);

function shortDigest(value: string) {
  return `${value.slice(0, 12)}...${value.slice(-8)}`;
}

export default function ForgeLawCartridge({ onCommand, busy }: CartridgeProps) {
  const [cartridges, setCartridges] = useState<ForgeCartridge[]>([]);
  const [selected, setSelected] = useState<ForgeCartridge | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("Loading verified cartridge evidence.");

  const refresh = useCallback(async () => {
    try {
      const response = await fetch("/api/forge", { cache: "no-store" });
      if (!response.ok) throw new Error(`Forge API returned ${response.status}`);
      const next = await response.json() as ForgeCartridge[];
      setCartridges(next);
      setSelected((current) => next.find((item) => item.id === current?.id) ?? next[0] ?? null);
      setMessage(next.length ? `${next.length} immutable cartridge${next.length === 1 ? "" : "s"} available.` : "No verified cartridge has crystallized yet.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Forge evidence is unavailable.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 8_000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  async function crystallize() {
    await onCommand("//CRYSTALLIZE blueprints/v10000.1");
    setMessage("Crystallization entered Iron Gate. The compiler will require matching verification evidence.");
  }

  async function execute() {
    if (!selected) return;
    await onCommand(`//EXECUTE_PROMPT ${selected.id}`);
    setMessage(`${selected.id} is awaiting operator approval.`);
  }

  return (
    <div className="cartridge-view forge-law-view" data-cartridge="forge-law">
      <section className="surface forge-command-band" aria-labelledby="forge-law-title">
        <div className="surface-heading">
          <div><p className="eyebrow">Forge Law v1</p><h2 id="forge-law-title">Verified upgrade pipeline</h2></div>
          <ShieldCheck aria-hidden="true" />
        </div>
        <div className="forge-command-actions">
          <button type="button" onClick={() => void crystallize()} disabled={busy}><Hammer aria-hidden="true" /> Crystallize verified source</button>
          <button type="button" onClick={() => void refresh()} disabled={loading} aria-label="Refresh Forge evidence" title="Refresh Forge evidence"><RefreshCw className={loading ? "spin" : ""} /></button>
        </div>
        <p className="surface-note" role="status">{message}</p>
      </section>

      <div className="forge-law-grid">
        <section className="surface forge-queue" aria-labelledby="forge-queue-title">
          <div className="surface-heading"><div><p className="eyebrow">LUKAS queue</p><h2 id="forge-queue-title">Bootstrap cartridges</h2></div><FileCode2 /></div>
          <div className="forge-cartridge-list">
            {cartridges.map((cartridge) => (
              <button key={cartridge.id} type="button" className={selected?.id === cartridge.id ? "forge-cartridge-row selected" : "forge-cartridge-row"} onClick={() => setSelected(cartridge)}>
                <span className={`forge-state state-${cartridge.state}`}>{cartridge.state === "verified" ? <CheckCircle2 /> : <CircleAlert />}</span>
                <span><strong>{cartridge.title}</strong><small>{cartridge.id} · {shortDigest(cartridge.digest)}</small></span>
                <b>{cartridge.state.replaceAll("_", " ")}</b>
              </button>
            ))}
            {!loading && cartridges.length === 0 ? <p className="empty-state">Crystallize the verified v10000.1 source bundle to create the first cartridge.</p> : null}
            {loading ? <div className="module-loading"><LoaderCircle className="spin" /> Reading Forge evidence</div> : null}
          </div>
        </section>

        <section className="surface forge-inspector" aria-labelledby="forge-inspector-title">
          <div className="surface-heading"><div><p className="eyebrow">Immutable contract</p><h2 id="forge-inspector-title">Execution scope</h2></div><ShieldCheck /></div>
          {selected ? (
            <>
              <dl className="forge-facts">
                <div><dt>State</dt><dd>{selected.state.replaceAll("_", " ")}</dd></div>
                <div><dt>Risk</dt><dd>{selected.risk.level}</dd></div>
                <div><dt>Target</dt><dd>{selected.targetRoot}</dd></div>
                <div><dt>Source</dt><dd>{selected.sourceDir}</dd></div>
              </dl>
              <div className="forge-dag" aria-label="Kinetic operation DAG">
                {selected.operations.map((operation, index) => (
                  <div key={operation.id}><span>{index + 1}</span><div><strong>{operation.id}</strong><small>{operation.type.replaceAll("_", " ")} · depends on {operation.dependsOn.join(", ") || "none"}</small></div></div>
                ))}
              </div>
              <button className="forge-execute" type="button" onClick={() => void execute()} disabled={busy || !executableStates.has(selected.state)}><Play aria-hidden="true" /> Request kinetic execution</button>
            </>
          ) : <p className="empty-state">Select a cartridge to inspect its exact operation boundary.</p>}
        </section>
      </div>
    </div>
  );
}

