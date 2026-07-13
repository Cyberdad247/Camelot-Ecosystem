import { NextRequest, NextResponse } from "next/server";
import { authenticateDeviceRequest, pollDeviceAction } from "@/lib/device-control";

export function GET(request: NextRequest) {
  const device = authenticateDeviceRequest(request);
  if (!device) return NextResponse.json({ message: "Device signature rejected." }, { status: 401 });
  return NextResponse.json({ action: pollDeviceAction(device.id) }, { headers: { "Cache-Control": "no-store" } });
}
