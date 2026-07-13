import "server-only";

import type { NextRequest } from "next/server";
import { isSecureRequest } from "./cockpit-auth";

export function webauthnContext(request: NextRequest) {
  const host = (request.headers.get("host") ?? request.nextUrl.host).toLowerCase();
  const rpID = host.split(":")[0].replace(/^\[|\]$/g, "");
  const protocol = isSecureRequest(request) ? "https" : "http";
  return { rpID, origin: `${protocol}://${host}`, rpName: "Camelot OS" };
}
