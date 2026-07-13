"use client";

import { Box, Braces, CheckCircle2, Gauge, GitBranch, Hammer, Play, Workflow } from "lucide-react";
import type { CartridgeProps } from "../types";

const stages = [
  { id: "INTAKE", title: "Intent intake", owner: "Anya", status: "complete" },
  { id: "BLUEPRINT", title: "Blueprint OS", owner: "Sir Alex", status: "complete" },
  { id: "SWARM", title: "Bio-Kinetic lanes", owner: "Sir Boris", status: "active" },
  { id: "FORGE", title: "Kinetic build", owner: "Sir Codex", status: "active" },
  { id: "VERIFY", title: "Crucible QA", owner: "Gideon", status: "queued" },
  { id: "RELEASE", title: "Operator release", owner: "Vaelen", status: "gated" },
] as const;

export default function FactoryCartridge({ status, events, onCommand, busy }: CartridgeProps) {
  return (
    <div className="cartridge-view" data-cartridge="factory">
      <div className="factory-grid">
        <section className="surface factory-flow" aria-labelledby="factory-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Blueprint OS</p><h2 id="factory-title">Digital Creation Factory</h2></div>
            <Workflow aria-hidden="true" />
          </div>
          <div className="stage-list">
            {stages.map((stage, index) => (
              <div className={`stage-row stage-${stage.status}`} key={stage.id}>
                <span className="stage-index">{String(index + 1).padStart(2, "0")}</span>
                <div><strong>{stage.title}</strong><small>{stage.owner}</small></div>
                <span>{stage.status}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="surface swarm-surface" aria-labelledby="swarm-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Rapid development</p><h2 id="swarm-title">Bio-Kinetic cells</h2></div>
            <Gauge aria-hidden="true" />
          </div>
          <div className="swarm-core">
            <div className="swarm-count"><strong>{status?.telemetry.swarmCells ?? 0}</strong><span>active cell</span></div>
            <div className="swarm-stats">
              <span><CheckCircle2 /> Preflight passed</span>
              <span><GitBranch /> Deterministic queue</span>
              <span><Braces /> Evidence v1</span>
            </div>
          </div>
          <button className="wide-action" type="button" onClick={() => void onCommand("//SWARM verify pwa cockpit release")} disabled={busy}>
            <Play aria-hidden="true" /> Queue verification swarm
          </button>
        </section>

        <section className="surface artifact-surface" aria-labelledby="artifact-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Build outputs</p><h2 id="artifact-title">Release artifacts</h2></div>
            <Box aria-hidden="true" />
          </div>
          <div className="artifact-list">
            <div><Hammer /><span>Interface shell</span><strong>FORGING</strong></div>
            <div><Braces /><span>Typed contracts</span><strong>BOUND</strong></div>
            <div><Workflow /><span>Cartridge chunks</span><strong>4 MOUNTED</strong></div>
            <div><CheckCircle2 /><span>Production build</span><strong>PENDING QA</strong></div>
          </div>
          <p className="surface-note">{events[0]?.message ?? "Waiting for Cockpit evidence."}</p>
        </section>
      </div>
    </div>
  );
}

