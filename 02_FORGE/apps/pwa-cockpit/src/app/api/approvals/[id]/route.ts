import { NextRequest, NextResponse } from "next/server";
import { createReceipt, pushEvent, resolveApproval } from "@/lib/control-plane";
import { isAuthorized, isCrossSiteRequest } from "@/lib/cockpit-auth";
import { executeRunic } from "@/lib/runic-adapter";
import { issueApprovalGrant } from "@/lib/approval-grant";
import { forgeApprovalBinding } from "@/lib/forge-law";
import { resolveDeviceAction } from "@/lib/device-control";
import {
  CapabilityRejected,
  digestPayload,
  directiveToCapability,
  requireCapability,
  type Capability,
} from "@/lib/capabilities";

type ApprovalGrantCapability = {
  capability: Capability;
  payloadDigest: string;
  target: string;
};

export async function POST(req: NextRequest, context: { params: Promise<{ id: string }> }) {
  if (!isAuthorized(req)) {
    return NextResponse.json({ accepted: false, message: "Operator pairing required." }, { status: 401 });
  }

  if (isCrossSiteRequest(req)) {
    return NextResponse.json({ accepted: false, message: "Cross-site approval requests are blocked." }, { status: 403 });
  }

  if (!req.headers.get("content-type")?.toLowerCase().includes("application/json")) {
    return NextResponse.json({ accepted: false, message: "Content-Type must be application/json." }, { status: 415 });
  }

  const { id } = await context.params;
  let body: { decision?: unknown; capabilityGrant?: unknown };

  try {
    body = (await req.json()) as { decision?: unknown; capabilityGrant?: unknown };
  } catch {
    return NextResponse.json({ accepted: false, message: "Invalid JSON body." }, { status: 400 });
  }

  if (body.decision !== "approved" && body.decision !== "rejected") {
    return NextResponse.json({ accepted: false, message: "decision must be approved or rejected." }, { status: 400 });
  }

  const result = resolveApproval(id, body.decision);
  if (!result) {
    return NextResponse.json({ accepted: false, message: "approval not found or already resolved." }, { status: 409 });
  }

  const { approval, receipt } = result;
  const deviceResolution = resolveDeviceAction(approval.command, body.decision === "approved");
  if (deviceResolution) {
    const queued = body.decision === "approved" && deviceResolution.queued;
    pushEvent({
      level: queued ? "info" : "warn",
      source: "device-hall",
      message: queued ? `${approval.command} entered the signed device delivery queue.` : `${approval.command} was not queued.`,
    });
    return NextResponse.json({
      accepted: queued || body.decision === "rejected",
      receiptId: receipt.id,
      message: queued ? `${approval.command} approved and queued for its enrolled device.` : `${approval.command} rejected or unavailable; no device action was delivered.`,
    }, { status: queued || body.decision === "rejected" ? 200 : 409 });
  }
  let execution = null;
  if (body.decision === "approved") {
    let binding = forgeApprovalBinding(approval.command);
    const directive = approval.command.split(/\s+/)[0];
    const runeCapability = directiveToCapability(directive);
    // Phase 1 hardening: capability grants are REQUIRED for mutating rune
    // approval resolution. Missing or invalid grants are rejected with a
    // targeted 403 so Iron Gate evidence still records the attempt.
    const incomingGrant = typeof body.capabilityGrant === "string" ? body.capabilityGrant : null;
    if (runeCapability) {
      if (!incomingGrant) {
        pushEvent({
          level: "warn",
          source: "iron-gate",
          message: `${approval.command} approval rejected: missing capability grant for ${directive}.`,
        });
        return NextResponse.json(
          {
            accepted: false,
            message: `missing capability grant for ${directive}`,
            capability: runeCapability,
            rejectionReason: "missing-grant",
            receiptId: receipt.id,
          },
          { status: 403 },
        );
      }
      let carriedCapability: ApprovalGrantCapability | null = null;
      try {
        const claims = requireCapability(req, runeCapability, {
          payloadDigest: digestPayload(`${approval.id}:${approval.command}:${binding?.cartridgeDigest ?? ""}`),
          target: directive,
          grant: incomingGrant,
        });
        carriedCapability = { capability: claims.capability, payloadDigest: claims.payloadDigest, target: directive };
      } catch (error) {
        if (error instanceof CapabilityRejected) {
          pushEvent({
            level: "warn",
            source: "iron-gate",
            message: `${approval.command} approval rejected by capability gate: ${error.capability} (${error.reason}).`,
          });
          return NextResponse.json(
            {
              accepted: false,
              message: `Capability rejected: ${error.capability} (${error.reason}).`,
              capability: error.capability,
              rejectionReason: error.reason,
              receiptId: receipt.id,
            },
            { status: error.status },
          );
        }
        throw error;
      }
      if (binding && carriedCapability) {
        binding = {
          cartridgeDigest: binding.cartridgeDigest,
          targetRoot: binding.targetRoot,
          capability: carriedCapability.capability,
          payloadDigest: carriedCapability.payloadDigest,
          target: carriedCapability.target,
        };
      }
    }
    try {
      execution = await executeRunic(approval.command, issueApprovalGrant(approval.id, approval.command, binding));
    } catch (error) {
      execution = {
        executed: false,
        status: "failed" as const,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }
  let outcomeReceipt = receipt;
  if (execution?.status === "failed") {
    outcomeReceipt = createReceipt(approval.command, "failed");
    pushEvent({ level: "error", source: "command-adapter", message: `${approval.command} was approved but execution failed: ${execution.error}` });
  } else if (execution?.status === "blocked") {
    outcomeReceipt = createReceipt(approval.command, "execution_blocked");
    pushEvent({ level: "warn", source: "command-policy", message: `${approval.command} was approved but blocked by the explicit rune allowlist.` });
  } else if (execution?.status === "complete") {
    outcomeReceipt = createReceipt(approval.command, "executed");
    pushEvent({ level: "info", source: "camelot-adapter", message: `${approval.command} executed after operator approval.` });
  }
  return NextResponse.json({
    accepted: true,
    receiptId: outcomeReceipt.id,
    message:
      body.decision === "approved"
        ? execution?.status === "complete"
          ? `${approval.command} approved, executed, and recorded as ${outcomeReceipt.id}.`
          : execution?.status === "failed"
            ? `${approval.command} approved, but execution failed and was recorded as ${outcomeReceipt.id}. Review the event trace.`
            : execution?.status === "blocked"
              ? `${approval.command} approved, but the rune allowlist blocked execution. Recorded as ${outcomeReceipt.id}.`
              : `${approval.command} approved and recorded as ${receipt.id}. Execution adapter remains environment-gated.`
        : `${approval.command} rejected and recorded as ${receipt.id}.`,
  });
}
