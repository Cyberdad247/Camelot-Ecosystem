import { NextRequest, NextResponse } from "next/server";
import { isAuthorized, isCrossSiteRequest } from "@/lib/cockpit-auth";
import { createDeviceAction } from "@/lib/device-control";
import { createApproval } from "@/lib/control-plane";

function primitiveArguments(value: unknown): value is Record<string, string | number | boolean> {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    && Object.values(value).every((entry) => typeof entry === "string" || typeof entry === "number" || typeof entry === "boolean");
}

export async function POST(request: NextRequest, context: { params: Promise<{ id: string }> }) {
  if (!isAuthorized(request)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  if (isCrossSiteRequest(request)) return NextResponse.json({ message: "Cross-site device actions are blocked." }, { status: 403 });
  if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) return NextResponse.json({ message: "Content-Type must be application/json." }, { status: 415 });
  const { id } = await context.params;
  let body: { capability?: unknown; arguments?: unknown };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }
  const actionArguments = body.arguments === undefined ? {} : body.arguments;
  if (typeof body.capability !== "string" || !primitiveArguments(actionArguments)) return NextResponse.json({ message: "A capability and primitive arguments object are required." }, { status: 400 });
  try {
    const action = createDeviceAction(id, body.capability, actionArguments);
    const approval = createApproval(`//DEVICE ${action.id}`, `Allow ${action.capability} on enrolled device ${id}.`);
    return NextResponse.json({ action, approval }, { status: 202 });
  } catch (error) {
    return NextResponse.json({ message: error instanceof Error ? error.message : "Device action could not be created." }, { status: 400 });
  }
}
