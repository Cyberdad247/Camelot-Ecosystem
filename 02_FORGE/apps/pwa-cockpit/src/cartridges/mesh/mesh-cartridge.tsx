"use client";

import { Boxes, Cable, Check, LockKeyhole, Network, PackageOpen, ShieldCheck } from "lucide-react";
import { cartridgeManifests } from "../manifests";
import type { CartridgeProps } from "../types";

export default function MeshCartridge({ status }: CartridgeProps) {
  return (
    <div className="cartridge-view" data-cartridge="mesh">
      <section className="surface catalog-surface" aria-labelledby="catalog-title">
        <div className="surface-heading">
          <div><p className="eyebrow">Trusted catalog</p><h2 id="catalog-title">Cartridge micro-frontends</h2></div>
          <Boxes aria-hidden="true" />
        </div>
        <div className="catalog-grid">
          {cartridgeManifests.map((manifest) => (
            <article key={manifest.id}>
              <div><PackageOpen aria-hidden="true" /><span className={`accent-${manifest.accent}`} /></div>
              <p>{manifest.phaseGlyph}</p>
              <h3>{manifest.label}</h3>
              <small>{manifest.lead}</small>
              <ul>{manifest.capabilities.map((capability) => <li key={capability}><Check />{capability}</li>)}</ul>
            </article>
          ))}
        </div>
      </section>

      <div className="mesh-grid">
        <section className="surface topology-surface" aria-labelledby="topology-title">
          <div className="surface-heading"><div><p className="eyebrow">Bridge topology</p><h2 id="topology-title">Data path</h2></div><Network /></div>
          <div className="topology-line">
            <span>Anya shell</span><Cable /><span>Next API</span><Cable /><span>Camelot control plane</span><Cable /><span>Knights</span>
          </div>
          <p className="surface-note">Remote cartridges cannot inject executable UI. Manifests map to pre-approved local React modules.</p>
        </section>
        <section className="surface policy-surface" aria-labelledby="policy-title">
          <div className="surface-heading"><div><p className="eyebrow">Governance</p><h2 id="policy-title">Trust ladder</h2></div><LockKeyhole /></div>
          <div className="policy-list">
            <div><span>READ</span><strong>Runtime and notebook views</strong><ShieldCheck /></div>
            <div><span>QUEUE</span><strong>Plans and swarm dispatch</strong><ShieldCheck /></div>
            <div><span>HITL</span><strong>Mutation and deployment</strong><ShieldCheck /></div>
          </div>
          <p className="surface-note">{status?.capabilities.commandExecution === "record-only" ? "Live command execution is intentionally disabled." : "Safe rune adapter is enabled."}</p>
        </section>
      </div>
    </div>
  );
}
