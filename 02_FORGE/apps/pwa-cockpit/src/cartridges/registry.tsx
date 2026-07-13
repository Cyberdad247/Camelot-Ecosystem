"use client";

import dynamic from "next/dynamic";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { Component, type ComponentType, type ErrorInfo, type ReactNode } from "react";
import { cartridgeManifests } from "./manifests";
import type { CartridgeId, CartridgeProps } from "./types";

export { cartridgeManifests } from "./manifests";

const loading = () => (
  <div className="module-loading" role="status" aria-live="polite">
    <span />
    Mounting trusted cartridge
  </div>
);

const trustedLoaders = {
  command: () => import("./command/command-cartridge"),
  factory: () => import("./factory/factory-cartridge"),
  "forge-law": () => import("./forge-law/forge-law-cartridge"),
  intelligence: () => import("./intelligence/intelligence-cartridge"),
  interphase: () => import("./interphase/interphase-cartridge"),
  "device-hall": () => import("./device-hall/device-hall-cartridge"),
  mesh: () => import("./mesh/mesh-cartridge"),
} satisfies Record<CartridgeId, () => Promise<{ default: ComponentType<CartridgeProps> }>>;

const trustedCatalog: Record<CartridgeId, ComponentType<CartridgeProps>> = {
  command: dynamic(trustedLoaders.command, { loading }),
  factory: dynamic(trustedLoaders.factory, { loading }),
  "forge-law": dynamic(trustedLoaders["forge-law"], { loading }),
  intelligence: dynamic(trustedLoaders.intelligence, { loading }),
  interphase: dynamic(trustedLoaders.interphase, { loading }),
  "device-hall": dynamic(trustedLoaders["device-hall"], { loading }),
  mesh: dynamic(trustedLoaders.mesh, { loading }),
};

type BoundaryProps = { id: CartridgeId; children: ReactNode };
type BoundaryState = { failed: boolean };

class CartridgeBoundary extends Component<BoundaryProps, BoundaryState> {
  state: BoundaryState = { failed: false };

  static getDerivedStateFromError(): BoundaryState {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`Trusted cartridge ${this.props.id} failed`, error, info.componentStack);
  }

  componentDidUpdate(previous: BoundaryProps) {
    if (previous.id !== this.props.id && this.state.failed) this.setState({ failed: false });
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <section className="surface cartridge-failure" role="alert">
        <AlertTriangle aria-hidden="true" />
        <div><p className="eyebrow">Isolation boundary</p><h2>Cartridge mount failed</h2><p>The shell and command boundary remain online.</p></div>
        <button type="button" onClick={() => window.location.reload()}><RotateCcw aria-hidden="true" /> Retry</button>
      </section>
    );
  }
}

export async function preloadTrustedCartridges() {
  await Promise.allSettled(Object.values(trustedLoaders).map((load) => load()));
}

export function manifestFor(id: CartridgeId) {
  return cartridgeManifests.find((manifest) => manifest.id === id) ?? cartridgeManifests[0];
}

// Exported so the health endpoint (and any other server-side probe) can
// count the registered V1 cartridges without hardcoding the list. Adding
// a new cartridge to `trustedLoaders` automatically extends this list,
// so /api/health no longer silently underreports.
export function getCartridgeIds(): readonly CartridgeId[] {
  return Object.keys(trustedLoaders) as CartridgeId[];
}

export function CartridgeMount({ id, ...props }: CartridgeProps & { id: CartridgeId }) {
  const TrustedCartridge = trustedCatalog[id];
  return <CartridgeBoundary id={id}><TrustedCartridge {...props} /></CartridgeBoundary>;
}
