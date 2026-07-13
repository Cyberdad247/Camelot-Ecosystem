import "server-only";

import { createHash, createHmac, randomUUID } from "node:crypto";

import type { Capability } from "./capabilities";

const GRANT_TTL_SECONDS = 90;
const GRANT_CONTEXT_V1 = "camelot-pwa-cockpit/approval-grant/v1";
const GRANT_CONTEXT_V2 = "camelot-pwa-cockpit/approval-grant/v2";

type ApprovalGrantClaims = {
  version: number;
  grantId: string;
  approvalId: string;
  commandDigest: string;
  issuedAt: number;
  expiresAt: number;
  cartridgeDigest?: string;
  targetRoot?: string;
  // Phase 1: optional capability binding threaded into the V2 envelope so every
  // approval carries (session, capability, payload digest, target, expiry) as
  // required by the Camelot V2 plan.
  capability?: Capability;
  payloadDigest?: string;
  target?: string;
};

export type ApprovalGrantBinding = {
  cartridgeDigest: string;
  targetRoot: string;
  capability?: Capability;
  payloadDigest?: string;
  target?: string;
};

function encode(value: string) {
  return Buffer.from(value, "utf8").toString("base64url");
}

export function issueApprovalGrant(
  approvalId: string,
  command: string,
  binding?: ApprovalGrantBinding | null,
) {
  const key = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  if (key.length < 16) throw new Error("Cockpit signing key is not configured.");

  const issuedAt = Math.floor(Date.now() / 1000);
  const version = binding ? 2 : 1;
  const claims: ApprovalGrantClaims = {
    version,
    grantId: randomUUID(),
    approvalId,
    commandDigest: createHash("sha256").update(command, "utf8").digest("hex"),
    issuedAt,
    expiresAt: issuedAt + GRANT_TTL_SECONDS,
    ...(binding ?? {}),
  };
  const payload = encode(JSON.stringify(claims));
  const context = version === 2 ? GRANT_CONTEXT_V2 : GRANT_CONTEXT_V1;
  const signature = createHmac("sha256", key).update(`${context}:${payload}`).digest("base64url");
  return `${payload}.${signature}`;
}
