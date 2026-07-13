// Next.js Edge Middleware — Camelot PWA Cockpit
// Runs on the edge runtime (Vercel Edge, Cloudflare Workers, Deno Deploy).
// Provides low-latency auth guards, PWA manifest routing, and
// agentic-control routing decisions before the request hits the page handler.
//
// This is a Phase 2 production-readiness addition. Tablet/PC/edge compatible.

import { NextRequest, NextResponse } from "next/server";
import { isValidBearerToken, isValidCartridgeId } from "@/lib/security/gate";

const PWA_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
} as const;

export const config = {
  // Match all routes except static assets, API routes, and the service
  // worker. The cockpit's page handler makes the final routing decision.
  matcher: [
    "/((?!_next/|favicon.ico|icons/|manifest.json|sw.js|api/health).*)",
  ],
};

export function middleware(request: NextRequest): NextResponse {
  const response = NextResponse.next();

  // Apply security headers to all matched routes.
  for (const [key, value] of Object.entries(PWA_HEADERS)) {
    response.headers.set(key, value);
  }

  const url = request.nextUrl;
  const pathname = url.pathname;

  // PWA manifest route — serve the production manifest.
  if (pathname === "/manifest.webmanifest" || pathname === "/manifest.json") {
    return NextResponse.rewrite(new URL("/manifest.json", request.url));
  }

  // Cartridge routes — guard against path traversal.
  if (pathname.startsWith("/cartridges/")) {
    const cartridgeId = pathname.split("/")[2] ?? "";
    if (!isValidCartridgeId(cartridgeId)) {
      return new NextResponse("Invalid cartridge id", { status: 400 });
    }
  }

  // Agentic control surface — /api/agent/* routes require a valid
  // session token. The token format check is a cheap pre-filter to
  // reject obvious garbage before hitting the heavy handler; the page
  // handler does the real verification (HMAC against the session
  // secret or a registry lookup). Format: `Bearer ` + 32+ chars of
  // base64url (A-Z, a-z, 0-9, -, _). The length + alphabet rules
  // raise the cost of a brute-force probe without coupling the edge
  // middleware to the session store.
  if (pathname.startsWith("/api/agent/")) {
    const auth = request.headers.get("authorization") ?? "";
    if (!isValidBearerToken(auth)) {
      return new NextResponse("Unauthorized", { status: 401 });
    }
  }

  return response;
}
