import { NextRequest, NextResponse } from "next/server";
import { isAuthorized } from "@/lib/cockpit-auth";
import { readForgeCartridge } from "@/lib/forge-law";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest, context: { params: Promise<{ id: string }> }) {
  if (!isAuthorized(req)) return NextResponse.json({ message: "Operator pairing required." }, { status: 401 });
  const { id } = await context.params;
  try {
    return NextResponse.json(readForgeCartridge(id), {
      headers: { "Cache-Control": "no-store, max-age=0" },
    });
  } catch (error) {
    return NextResponse.json({ message: error instanceof Error ? error.message : "Forge cartridge unavailable." }, { status: 404 });
  }
}

