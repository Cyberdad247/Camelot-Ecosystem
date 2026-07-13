import { NextRequest, NextResponse } from "next/server";
import { createApproval, createReceipt, pushEvent } from "@/lib/control-plane";
import { isAuthorized, isCrossSiteRequest } from "@/lib/cockpit-auth";
import {
  CapabilityRejected,
  digestPayload,
  directiveToCapability,
  requireCapability,
} from "@/lib/capabilities";

const readOnlyRunes = new Set(["//STATUS"]);

export async function POST(req: NextRequest) {
  if (!isAuthorized(req)) {
    return NextResponse.json({ accepted: false, message: "Operator pairing required." }, { status: 401 });
  }

  if (isCrossSiteRequest(req)) {
    return NextResponse.json({ accepted: false, message: "Cross-site command requests are blocked." }, { status: 403 });
  }

  if (!req.headers.get("content-type")?.toLowerCase().includes("application/json")) {
    return NextResponse.json({ accepted: false, message: "Content-Type must be application/json." }, { status: 415 });
  }

  let body: { command?: unknown; capabilityGrant?: unknown };
  try {
    body = (await req.json()) as { command?: unknown; capabilityGrant?: unknown };
  } catch {
    return NextResponse.json({ accepted: false, message: "Invalid JSON body." }, { status: 400 });
  }

  if (typeof body.command !== "string" || !body.command.trim()) {
    return NextResponse.json({ accepted: false, message: "command is required." }, { status: 400 });
  }

  const command = body.command.trim();
  if (command.length > 1200) {
    return NextResponse.json({ accepted: false, message: "command exceeds the 1200 character limit." }, { status: 413 });
  }

  const directive = command.split(/\s+/)[0];
  const isRunic = directive.startsWith("//") || directive.startsWith("Omega_");

  if (isRunic && !readOnlyRunes.has(directive)) {
    // Phase 1 hardening (Item 1): bind the rune to its Capability before
    // entering Iron Gate. The capability grant is REQUIRED for any mutating
    // rune; missing or invalid grants are rejected with a targeted 403 so
    // Iron Gate evidence still records the attempt.
    const runeCapability = directiveToCapability(directive);
    const incomingGrant = typeof body.capabilityGrant === "string" ? body.capabilityGrant : null;
    if (runeCapability) {
      if (!incomingGrant) {
        return NextResponse.json(
          {
            accepted: false,
            message: `missing capability grant for ${directive}`,
            capability: runeCapability,
            rejectionReason: "missing-grant",
          },
          { status: 403 },
        );
      }
      try {
        requireCapability(req, runeCapability, {
          payloadDigest: digestPayload(command),
          target: directive,
          grant: incomingGrant,
        });
      } catch (error) {
        if (error instanceof CapabilityRejected) {
          return NextResponse.json(
            {
              accepted: false,
              message: `Capability rejected: ${error.capability} (${error.reason}).`,
              capability: error.capability,
              rejectionReason: error.reason,
            },
            { status: error.status },
          );
        }
        throw error;
      }
    }
    const approval = createApproval(
      command,
      "This runic directive may mutate Camelot state. Manual operator clearance is required before a live adapter may execute it.",
    );
    return NextResponse.json({
      accepted: true,
      approvalId: approval.id,
      message: `Iron Gate approval queued for ${directive}.`,
      ...(runeCapability ? { capability: runeCapability } : {}),
    });
  }

  const receipt = createReceipt(command, "accepted");
  pushEvent({
    level: "info",
    source: readOnlyRunes.has(directive) ? "runtime-status" : "command-router",
    message: readOnlyRunes.has(directive)
      ? `${directive} resolved from the read-only Cockpit runtime API; no harness task was queued.`
      : `Accepted ${directive}; durable receipt created.`,
  });

  return NextResponse.json({
    accepted: true,
    receiptId: receipt.id,
    message: readOnlyRunes.has(directive)
      ? `${directive} refreshed from local runtime evidence and was recorded as ${receipt.id}.`
      : `Intent recorded as ${receipt.id}. Anya will preserve it for the active cartridge handoff.`,
  });
}
