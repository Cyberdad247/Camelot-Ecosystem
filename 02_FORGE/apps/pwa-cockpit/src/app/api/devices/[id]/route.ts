import { NextRequest, NextResponse } from "next/server";
import { isAuthorized, isCrossSiteRequest } from "@/lib/cockpit-auth";
import { revokeDevice } from "@/lib/device-control";
import { pushEvent } from "@/lib/control-plane";

export async function DELETE(request: NextRequest, context: { params: Promise<{ id: string }> }) {
  if (!isAuthorized(request)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  if (isCrossSiteRequest(request)) return NextResponse.json({ message: "Cross-site revocation is blocked." }, { status: 403 });
  const { id } = await context.params;
  const device = revokeDevice(id);
  if (!device) return NextResponse.json({ message: "Active device not found." }, { status: 404 });
  pushEvent({ level: "warn", source: "device-hall", message: `${device.name} was revoked; outstanding actions were rejected.` });
  return NextResponse.json({ device });
}
