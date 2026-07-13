"use client";

// Client-side helper for the operator UI. Before submitting a mutating rune
// (//CRYSTALLIZE, //EXECUTE_PROMPT, //DEVICE_*, //CARTRIDGE_*, //PLAN, //SWARM),
// the shell calls forgeCapabilityGrant to mint a short-lived grant bound to
// (capability, payload digest, target, expiry, single-use nonce). The returned
// `grant` string is then attached to the command submission either via the
// `capabilityGrant` body field or the `X-Camelot-Capability-Grant` header.
//
// This helper is intentionally minimal: it does not retry, does not refresh
// tokens, and does not surface human-readable errors. The mutating-rune route
// is the source of truth for rejection messages.

import type { Capability, CapabilityGrantClaims } from "./capabilities";

export type ForgeGrantRequest = {
  capability: Capability;
  command?: string;
  payloadDigest?: string;
  target?: string;
  approvalId?: string;
  expiresAt?: number;
};

export type ForgeGrantSuccess = {
  ok: true;
  grant: string;
  claims: CapabilityGrantClaims;
  expiresInSeconds: number;
};

export type ForgeGrantFailure = {
  ok: false;
  status: number;
  message: string;
  capability?: Capability;
  rejectionReason?: string;
};

export type ForgeGrantResult = ForgeGrantSuccess | ForgeGrantFailure;

export async function forgeCapabilityGrant(input: ForgeGrantRequest, init: RequestInit = {}): Promise<ForgeGrantResult> {
  if (typeof fetch !== "function") {
    return { ok: false, status: 0, message: "fetch is not available in this runtime." };
  }
  let response: Response;
  try {
    response = await fetch("/api/capabilities", {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "content-type": "application/json", ...(init.headers ?? {}) },
      body: JSON.stringify(input),
      ...init,
    });
  } catch (error) {
    return {
      ok: false,
      status: 0,
      message: error instanceof Error ? error.message : "Network error while minting capability grant.",
    };
  }
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  const record = (payload && typeof payload === "object") ? payload as Record<string, unknown> : {};
  if (!response.ok) {
    return {
      ok: false,
      status: response.status,
      message: typeof record.message === "string" ? record.message : `Grant mint failed with HTTP ${response.status}.`,
      capability: typeof record.capability === "string" ? (record.capability as Capability) : undefined,
      rejectionReason: typeof record.rejectionReason === "string" ? record.rejectionReason : undefined,
    };
  }
  if (typeof record.grant !== "string" || !record.claims) {
    return { ok: false, status: response.status, message: "Grant mint response was malformed." };
  }
  return {
    ok: true,
    grant: record.grant,
    claims: record.claims as CapabilityGrantClaims,
    expiresInSeconds: typeof record.expiresInSeconds === "number" ? record.expiresInSeconds : 90,
  };
}
