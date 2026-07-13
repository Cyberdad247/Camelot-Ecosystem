import { NextRequest, NextResponse } from "next/server";
import {
  CAPABILITIES_COOKIE,
  OPERATOR_COOKIE,
  OPERATOR_SESSION_TTL_SECONDS,
  allowPairingAttempt,
  capabilitiesCookieValue,
  defaultOperatorCapabilities,
  isCrossSiteRequest,
  isSecureRequest,
  operatorCapabilities,
  operatorSession,
  sessionCookieValue,
  validateOperatorToken,
} from "@/lib/cockpit-auth";

export function GET(request: NextRequest) {
  const session = operatorSession(request);
  // Phase 1 hardening (Item 3): the session advertises only the scopes
  // explicitly granted via CAMELOT_COCKPIT_DEFAULT_CAPABILITIES and bound
  // through the camelot_operator_caps cookie. Default empty behaves safely
  // in production until a minting endpoint is added in Phase 2.
  return NextResponse.json({
    ...session,
    capabilities: session.authenticated ? operatorCapabilities(request) : [],
  }, {
    headers: { "Cache-Control": "no-store" },
  });
}

export async function POST(request: NextRequest) {
  if (isCrossSiteRequest(request)) {
    return NextResponse.json({ authenticated: false, message: "Cross-site pairing requests are blocked." }, { status: 403 });
  }

  if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) {
    return NextResponse.json({ authenticated: false, message: "Content-Type must be application/json." }, { status: 415 });
  }

  if (!allowPairingAttempt(request)) {
    return NextResponse.json({ authenticated: false, message: "Too many pairing attempts. Retry in one minute." }, { status: 429 });
  }

  let body: { token?: unknown };
  try {
    body = (await request.json()) as { token?: unknown };
  } catch {
    return NextResponse.json({ authenticated: false, message: "Invalid pairing request." }, { status: 400 });
  }

  if (typeof body.token !== "string" || !validateOperatorToken(body.token)) {
    return NextResponse.json({ authenticated: false, message: "Operator token rejected." }, { status: 401 });
  }

  const response = NextResponse.json({ authenticated: true });
  response.cookies.set(OPERATOR_COOKIE, sessionCookieValue(), {
    httpOnly: true,
    sameSite: "strict",
    secure: isSecureRequest(request),
    path: "/",
    maxAge: OPERATOR_SESSION_TTL_SECONDS,
  });
  response.cookies.set(CAPABILITIES_COOKIE, capabilitiesCookieValue(defaultOperatorCapabilities()), {
    httpOnly: true,
    sameSite: "strict",
    secure: isSecureRequest(request),
    path: "/",
    maxAge: OPERATOR_SESSION_TTL_SECONDS,
  });
  return response;
}

export function DELETE(request: NextRequest) {
  if (isCrossSiteRequest(request)) {
    return NextResponse.json({ authenticated: false, message: "Cross-site session requests are blocked." }, { status: 403 });
  }

  const response = NextResponse.json({ authenticated: false });
  response.cookies.set(OPERATOR_COOKIE, "", {
    httpOnly: true,
    sameSite: "strict",
    secure: isSecureRequest(request),
    path: "/",
    maxAge: 0,
  });
  response.cookies.set(CAPABILITIES_COOKIE, "", {
    httpOnly: true,
    sameSite: "strict",
    secure: isSecureRequest(request),
    path: "/",
    maxAge: 0,
  });
  return response;
}

