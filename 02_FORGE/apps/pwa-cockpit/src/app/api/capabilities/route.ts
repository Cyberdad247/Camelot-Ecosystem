import { NextRequest, NextResponse } from "next/server";

import {
  ALL_CAPABILITIES,
  appendGrantAuditLog,
  digestPayload,
  issueCapabilityGrant,
  type Capability,
  type CapabilityGrantClaims,
} from "@/lib/capabilities";
import {
  isAuthorized,
  isCrossSiteRequest,
  isSecureRequest,
  operatorCapabilities,
} from "@/lib/cockpit-auth";

// Phase 1.5 hardening: the wire response never echoes the grant's internal
// claims. The grantId + nonce are operational metadata the client should not
// see — exposing the nonce enlarges the replay window if the response is
// logged or cached. The subset below is sufficient for the operator UI to
// confirm scope/target/expiry.
type GrantResponseClaims = Pick<
  CapabilityGrantClaims,
  "capability" | "payloadDigest" | "target" | "approvalId" | "issuedAt" | "expiresAt"
>;

type GrantResponse = {
  grant: string;
  claims: GrantResponseClaims;
  expiresInSeconds: number;
};

// POST /api/capabilities — mint a short-lived capability grant bound to
// (capability, payload digest, target, expiry, single-use nonce). The mint is
// itself capability-gated: the operator's session must already carry the
// requested scope, OR the deployment must opt into admin override via
// CAMELOT_COCKPIT_GRANT_ADMIN=true (used for bootstrap and recovery flows).
//
// Body shape:
//   {
//     "capability": "forge.execute",
//     "command": "//CRYSTALLIZE blueprints/v10000.1",   // optional, server hashes
//     "payloadDigest": "abc...",                       // optional override
//     "target": "//CRYSTALLIZE",                      // optional, defaults to command directive
//     "approvalId": "appr-..."                        // optional, binds grant to approval
//     "expiresAt": 1234567890                          // optional, max = now + 90s
//   }
//
// Returns 200 with { grant, claims, expiresInSeconds }, or 401/403/422 for
// auth/authorization/validation failures. The grant string is the same shape
// the existing verifyCapabilityGrant pipeline consumes.
export async function POST(request: NextRequest) {
  if (!isAuthorized(request)) {
    return NextResponse.json({ minted: false, message: "Operator pairing required." }, { status: 401 });
  }

  if (isCrossSiteRequest(request)) {
    return NextResponse.json({ minted: false, message: "Cross-site grant requests are blocked." }, { status: 403 });
  }

  if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) {
    return NextResponse.json({ minted: false, message: "Content-Type must be application/json." }, { status: 415 });
  }

  let body: {
    capability?: unknown;
    command?: unknown;
    payloadDigest?: unknown;
    target?: unknown;
    approvalId?: unknown;
    expiresAt?: unknown;
  };

  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ minted: false, message: "Invalid JSON body." }, { status: 400 });
  }

  if (typeof body.capability !== "string" || !ALL_CAPABILITIES.includes(body.capability as Capability)) {
    return NextResponse.json(
      { minted: false, message: `Unknown or missing capability: ${String(body.capability)}` },
      { status: 422 },
    );
  }
  const capability = body.capability as Capability;

  // Authorization: session must already carry the requested scope, or the
  // deployment is in admin-override mode (bootstrap, recovery, testing).
  const sessionCapabilities = operatorCapabilities(request);
  const adminOverride = process.env.CAMELOT_COCKPIT_GRANT_ADMIN === "true";
  if (!sessionCapabilities.includes(capability) && !adminOverride) {
    return NextResponse.json(
      {
        minted: false,
        message: `Session does not carry ${capability}; grant denied.`,
        capability,
        rejectionReason: "session-missing-scope",
      },
      { status: 403 },
    );
  }

  // Resolve the payload digest. If the caller supplies `command`, the server
  // hashes it; otherwise it must supply a pre-computed `payloadDigest`.
  let payloadDigest: string;
  if (typeof body.command === "string" && body.command.length > 0) {
    payloadDigest = digestPayload(body.command);
  } else if (typeof body.payloadDigest === "string" && /^[a-f0-9]{64}$/.test(body.payloadDigest)) {
    payloadDigest = body.payloadDigest;
  } else {
    return NextResponse.json(
      { minted: false, message: "payloadDigest (or command) is required to bind a grant." },
      { status: 422 },
    );
  }

  // Optional target: the directive name (e.g. "//CRYSTALLIZE") that the grant
  // will be restricted to. Defaults to the command's first word if available.
  let target: string | null = null;
  if (typeof body.target === "string" && body.target.trim().length > 0) {
    target = body.target.trim();
  } else if (typeof body.command === "string" && body.command.length > 0) {
    target = body.command.split(/\s+/)[0] ?? null;
  }

  let approvalId: string | null = null;
  if (typeof body.approvalId === "string" && body.approvalId.trim().length > 0) {
    approvalId = body.approvalId.trim();
  }

  let expiresAt: number | undefined;
  if (typeof body.expiresAt === "number" && Number.isFinite(body.expiresAt)) {
    expiresAt = body.expiresAt;
  }

  const minted = issueCapabilityGrant({
    capability,
    payloadDigest,
    target,
    approvalId,
    expiresAt,
  });

  // Phase 1.5 hardening: log admin-override grants so a compromised admin
  // env leaves a paper trail. Session-grant flow (the normal path) is not
  // logged; admin-override is the high-trust escape hatch and the only path
  // that warrants post-incident review.
  if (adminOverride && !sessionCapabilities.includes(capability)) {
    appendGrantAuditLog({
      ts: Date.now(),
      source: "admin-override",
      capability,
      target,
      approvalId,
      sessionCapabilities,
    });
  }

  const expiresInSeconds = Math.max(0, minted.claims.expiresAt - minted.claims.issuedAt);

  const response: GrantResponse = {
    grant: minted.grant,
    claims: {
      capability: minted.claims.capability,
      payloadDigest: minted.claims.payloadDigest,
      target: minted.claims.target,
      approvalId: minted.claims.approvalId,
      issuedAt: minted.claims.issuedAt,
      expiresAt: minted.claims.expiresAt,
    },
    expiresInSeconds,
  };

  // Mark the response as no-store so the grant is not cached by intermediaries.
  return NextResponse.json(response, {
    headers: {
      "Cache-Control": "no-store",
      "X-Camelot-Capability-Grant-Version": "3",
      ...(isSecureRequest(request) ? { "Strict-Transport-Security": "max-age=31536000; includeSubDomains" } : {}),
    },
  });
}
