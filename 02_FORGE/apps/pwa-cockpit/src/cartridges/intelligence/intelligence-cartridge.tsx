"use client";

import { BookOpen, BrainCircuit, Cloud, Database, ExternalLink, FileClock, ShieldAlert, Sparkles, Users } from "lucide-react";
import type { CartridgeProps } from "../types";
import { JarvisGraph } from "@/components/jarvis-graph";
import { councilPlan, recommendKnights } from "@/lib/knight-recommendations";

export default function IntelligenceCartridge({ status, onCommand, busy }: CartridgeProps) {
  const cloud = status?.services.find((service) => service.id === "cloudbrain");
  const recommendations = recommendKnights(status);

  return (
    <div className="cartridge-view" data-cartridge="intelligence">
      <div className="intel-grid">
        <JarvisGraph />

        <section className="surface brain-surface" aria-labelledby="brain-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Memory topology</p><h2 id="brain-title">Cloud Brain</h2></div>
            <BrainCircuit aria-hidden="true" />
          </div>
          <div className="brain-topology">
            <div><Database /><span>Long-term</span><strong>Excalibur Brain</strong><small>Remote runtime alive</small></div>
            <div><BookOpen /><span>Design source</span><strong>Mastering Professional UI/UX</strong><small>17 source notebook consulted</small></div>
            <div><Cloud /><span>Sync state</span><strong>{cloud?.status ?? "offline"}</strong><small>{cloud?.detail ?? "No audit evidence"}</small></div>
          </div>
        </section>

        <section className="surface guidance-surface" aria-labelledby="guidance-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Notebook synthesis</p><h2 id="guidance-title">Interface laws</h2></div>
            <FileClock aria-hidden="true" />
          </div>
          <ol className="guidance-list">
            <li><span>01</span><div><strong>Voice first, never voice only</strong><small>Every spoken action retains visible and keyboard-operable controls.</small></div></li>
            <li><span>02</span><div><strong>Render agent UI as trusted data</strong><small>Cartridges mount only from the local component catalog.</small></div></li>
            <li><span>03</span><div><strong>Expose phase, source, and freshness</strong><small>No silent stubs and no fabricated live telemetry.</small></div></li>
            <li><span>04</span><div><strong>Motion yields to capability</strong><small>Reduced-motion and low-memory paths remain first-class.</small></div></li>
          </ol>
        </section>

        <section className="surface council-surface" aria-labelledby="council-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Anya routing</p><h2 id="council-title">Recommended council</h2></div>
            <Users aria-hidden="true" />
          </div>
          <div className="council-list">
            {recommendations.map((knight, index) => (
              <article className={`council-item council-${knight.severity}`} key={knight.id}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div><strong>{knight.name}</strong><small>{knight.role}</small><p>{knight.reason}</p><em>{knight.recommendation}</em></div>
                <b>{knight.score}</b>
              </article>
            ))}
          </div>
          <button className="council-action" type="button" onClick={() => void onCommand(councilPlan(recommendations))} disabled={busy || recommendations.length === 0}>
            <Sparkles aria-hidden="true" /> Convene governed plan
          </button>
        </section>

        <section className="surface provenance-surface" aria-labelledby="provenance-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Source chain</p><h2 id="provenance-title">Provenance</h2></div>
            <ShieldAlert aria-hidden="true" />
          </div>
          <div className="provenance-list">
            <a href="https://notebooklm.google.com/notebook/5ffaf13c-4db5-4619-9d6d-4bb1f660e91a" target="_blank" rel="noreferrer">
              NotebookLM design brain <ExternalLink aria-hidden="true" />
            </a>
            <span>Blueprint OS factory overhaul / 2026-07-08</span>
            <span>PWA Ecosystem Cartridge vMAX / 2026-07-10</span>
            <span>Bio-Swarm release evidence / local runtime</span>
          </div>
        </section>
      </div>
    </div>
  );
}
