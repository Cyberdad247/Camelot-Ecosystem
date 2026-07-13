import { NextResponse } from "next/server";
import { passkeyStatus } from "@/lib/passkey-store";

export async function GET() {
  return NextResponse.json(await passkeyStatus(), {
    headers: { "Cache-Control": "no-store" },
  });
}
