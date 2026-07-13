import { NextRequest, NextResponse } from "next/server";
import { isAuthorized, isCrossSiteRequest } from "@/lib/cockpit-auth";
import { deviceHallSnapshot, enrollDevice } from "@/lib/device-control";
import { capabilitiesFor, type DevicePlatform } from "@/lib/device-contract";
import { pushEvent } from "@/lib/control-plane";

const platforms = new Set<DevicePlatform>(["desktop", "ios", "android"]);

export function GET(request: NextRequest) {
  if (!isAuthorized(request)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  return NextResponse.json(deviceHallSnapshot(), { headers: { "Cache-Control": "no-store" } });
}

export async function POST(request: NextRequest) {
  if (!isAuthorized(request)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  if (isCrossSiteRequest(request)) return NextResponse.json({ message: "Cross-site enrollment is blocked." }, { status: 403 });
  if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) return NextResponse.json({ message: "Content-Type must be application/json." }, { status: 415 });
  let body: { name?: unknown; platform?: unknown; publicKey?: unknown; capabilities?: unknown };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON body." }, { status: 400 });
  }
  if (typeof body.name !== "string" || typeof body.platform !== "string" || !platforms.has(body.platform as DevicePlatform) || typeof body.publicKey !== "string") {
    return NextResponse.json({ message: "name, platform, and Ed25519 publicKey are required." }, { status: 400 });
  }
  const platform = body.platform as DevicePlatform;
  const capabilities = Array.isArray(body.capabilities) ? body.capabilities.filter((value): value is string => typeof value === "string") : capabilitiesFor(platform);
  try {
    const device = enrollDevice({ name: body.name, platform, publicKey: body.publicKey, capabilities });
    pushEvent({ level: "info", source: "device-hall", message: `${device.name} enrolled with ${device.capabilities.length} explicit capabilities.` });
    return NextResponse.json({ device }, { status: 201 });
  } catch (error) {
    return NextResponse.json({ message: error instanceof Error ? error.message : "Device enrollment failed." }, { status: 400 });
  }
}
