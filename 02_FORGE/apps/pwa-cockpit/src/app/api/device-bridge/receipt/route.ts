import { NextRequest, NextResponse } from "next/server";
import { authenticateDeviceRequest, completeDeviceAction } from "@/lib/device-control";
import { pushEvent } from "@/lib/control-plane";

export async function POST(request: NextRequest) {
  if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) return NextResponse.json({ message: "Content-Type must be application/json." }, { status: 415 });
  const raw = await request.text();
  const device = authenticateDeviceRequest(request, raw);
  if (!device) return NextResponse.json({ message: "Device signature rejected." }, { status: 401 });
  let body: { actionId?: unknown; success?: unknown; result?: unknown };
  try {
    body = JSON.parse(raw);
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }
  if (typeof body.actionId !== "string" || typeof body.success !== "boolean" || typeof body.result !== "string") return NextResponse.json({ message: "actionId, success, and result are required." }, { status: 400 });
  const action = completeDeviceAction(device.id, body.actionId, body.success, body.result);
  if (!action) return NextResponse.json({ message: "Deliverable action not found." }, { status: 404 });
  pushEvent({ level: body.success ? "info" : "error", source: "device-bridge", message: `${device.name} reported ${action.capability} ${action.status}.` });
  return NextResponse.json({ action });
}
