import { NextRequest, NextResponse } from "next/server";
import { isAuthorized, isCrossSiteRequest, isLocalRequest, operatorCapabilities } from "@/lib/cockpit-auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_FRAME_BYTES = 3_200;
const SESSION_ID = /^vfc-[a-f0-9]{24}$/;

function omniVoiceEndpoint(): URL | null {
  const raw = process.env.CAMELOT_OMNIVOICE_URL?.trim() || "http://127.0.0.1:3002/ingest_pcm";
  try {
    const endpoint = new URL(raw);
    if (endpoint.protocol !== "http:") return null;
    if (!new Set(["127.0.0.1", "localhost", "::1"]).has(endpoint.hostname)) return null;
    if (endpoint.username || endpoint.password) return null;
    endpoint.pathname = "/ingest_pcm";
    endpoint.search = "";
    return endpoint;
  } catch {
    return null;
  }
}

export async function POST(request: NextRequest) {
  if (!isAuthorized(request)) {
    return NextResponse.json({ accepted: false, message: "Operator pairing required." }, { status: 401 });
  }
  if (isCrossSiteRequest(request)) {
    return NextResponse.json({ accepted: false, message: "Cross-site voice frames are blocked." }, { status: 403 });
  }
  const developmentBypass = process.env.NODE_ENV !== "production" && isLocalRequest(request);
  if (!developmentBypass && !operatorCapabilities(request).includes("voice.use")) {
    return NextResponse.json({ accepted: false, message: "The operator session lacks voice.use." }, { status: 403 });
  }
  if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/octet-stream")) {
    return NextResponse.json({ accepted: false, message: "Content-Type must be application/octet-stream." }, { status: 415 });
  }

  const session = request.headers.get("x-voice-session") ?? "";
  const sequence = Number(request.headers.get("x-voice-sequence"));
  const sampleRate = Number(request.headers.get("x-voice-sample-rate"));
  if (!SESSION_ID.test(session) || !Number.isSafeInteger(sequence) || sequence < 0 || sampleRate !== 16_000) {
    return NextResponse.json({ accepted: false, message: "Invalid voice frame metadata." }, { status: 400 });
  }
  const declaredLength = Number(request.headers.get("content-length") ?? 0);
  if (declaredLength > MAX_FRAME_BYTES) {
    return NextResponse.json({ accepted: false, message: "Voice frame exceeds 3,200 bytes." }, { status: 413 });
  }
  const body = await request.arrayBuffer();
  if (body.byteLength < 2 || body.byteLength > MAX_FRAME_BYTES || body.byteLength % 2 !== 0) {
    return NextResponse.json({ accepted: false, message: "Voice frame must contain bounded Int16 PCM." }, { status: 413 });
  }

  const endpoint = omniVoiceEndpoint();
  if (!endpoint) {
    return NextResponse.json({ accepted: false, message: "OmniVoice loopback endpoint is invalid." }, { status: 503 });
  }
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "content-type": "application/octet-stream",
        "content-length": String(body.byteLength),
        "x-voice-session": session,
        "x-voice-sequence": String(sequence),
        "x-voice-sample-rate": "16000",
        "x-voice-discontinuity": request.headers.get("x-voice-discontinuity") === "1" ? "1" : "0",
      },
      body,
      signal: AbortSignal.timeout(750),
      cache: "no-store",
    });
    if (!response.ok) throw new Error(`OmniVoice returned ${response.status}.`);
    return NextResponse.json({ accepted: true }, { status: 202, headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    return NextResponse.json(
      { accepted: false, message: error instanceof Error ? error.message : "OmniVoice unavailable." },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
}
