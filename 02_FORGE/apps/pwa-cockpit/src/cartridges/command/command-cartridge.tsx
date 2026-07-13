"use client";

import { Activity, ArrowUpRight, Cpu, Database, MemoryStick, Radio, ShieldCheck } from "lucide-react";
import type { CartridgeProps } from "../types";

function value(value: number | null | undefined, suffix = "") {
  return typeof value === "number" ? `${value}${suffix}` : "--";
}

export default function CommandCartridge({ status, onCommand, busy }: CartridgeProps) {
  const telemetry = status?.telemetry;
  const activeServices = status?.services.filter((service) => service.status === "online").length ?? 0;
  const totalServices = status?.services.length ?? 0;

  return (
    <div className="cartridge-view" data-cartridge="command">
      <section className="metric-strip" aria-label="Runtime telemetry">
        <div><Cpu aria-hidden="true" /><span>CPU</span><strong>{value(telemetry?.cpuPercent, "%")}</strong></div>
        <div><MemoryStick aria-hidden="true" /><span>Memory</span><strong>{value(telemetry?.memoryPercent, "%")}</strong></div>
        <div><Radio aria-hidden="true" /><span>Services</span><strong>{activeServices}/{totalServices}</strong></div>
        <div><Database aria-hidden="true" /><span>Queue</span><strong>{telemetry?.queuePending ?? 0}</strong></div>
      </section>

      <div className="command-grid">
        <section className="surface command-primary" aria-labelledby="mission-title">
          <div className="surface-heading">
            <div>
              <p className="eyebrow">Current mission</p>
              <h2 id="mission-title">Agent OS production lane</h2>
            </div>
            <span className="phase-badge phase-live">[EXECUTE]</span>
          </div>

          <div className="mission-progress" aria-label="Mission progress">
            <div className="mission-line complete"><span>01</span><div><strong>Assimilate</strong><small>Notebook + Blueprint OS</small></div></div>
            <div className="mission-line active"><span>02</span><div><strong>Forge</strong><small>PWA shell + cartridge catalog</small></div></div>
            <div className="mission-line"><span>03</span><div><strong>Validate</strong><small>Build, browser, mobile, offline</small></div></div>
            <div className="mission-line"><span>04</span><div><strong>Release</strong><small>Operator-gated deployment</small></div></div>
          </div>

          <div className="command-actions">
            <button type="button" onClick={() => void onCommand("//STATUS")} disabled={busy}>
              <Activity aria-hidden="true" /> Refresh status
            </button>
            <button type="button" onClick={() => void onCommand("//PLAN production release")} disabled={busy}>
              <ArrowUpRight aria-hidden="true" /> Plan release
            </button>
          </div>
        </section>

        <section className="surface service-surface" aria-labelledby="service-title">
          <div className="surface-heading">
            <div><p className="eyebrow">Local mesh</p><h2 id="service-title">Runtime services</h2></div>
            <ShieldCheck aria-hidden="true" />
          </div>
          <div className="service-list">
            {(status?.services ?? []).slice(0, 8).map((service) => (
              <div className="service-row" key={service.id}>
                <span className={`status-dot status-${service.status}`} aria-hidden="true" />
                <div><strong>{service.label}</strong><small>{service.detail}</small></div>
                <span className="service-latency">{service.latencyMs ? `${service.latencyMs}ms` : service.status}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

