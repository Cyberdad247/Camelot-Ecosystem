import { generateRegistrationOptions } from "@simplewebauthn/server";
import { NextRequest, NextResponse } from "next/server";
import { isAuthorized, isCrossSiteRequest, isSecureRequest } from "@/lib/cockpit-auth";
import { PASSKEY_CHALLENGE_COOKIE, PASSKEY_CHALLENGE_TTL_SECONDS, issuePasskeyChallenge } from "@/lib/passkey-challenges";
import { withPasskeyStore } from "@/lib/passkey-store";
import { webauthnContext } from "@/lib/webauthn-context";

export async function POST(request: NextRequest) {
  if (!isAuthorized(request)) return NextResponse.json({ message: "Operator session required." }, { status: 401 });
  if (isCrossSiteRequest(request)) return NextResponse.json({ message: "Cross-site passkey requests are blocked." }, { status: 403 });

  const { rpID, rpName } = webauthnContext(request);
  const options = await withPasskeyStore(async (store) => ({
    result: await generateRegistrationOptions({
      rpName,
      rpID,
      userName: "camelot-operator",
      userDisplayName: "Camelot Operator",
      userID: new Uint8Array(Buffer.from(store.userId, "base64url")),
      attestationType: "none",
      excludeCredentials: store.credentials.map((credential) => ({ id: credential.id, transports: credential.transports })),
      authenticatorSelection: {
        residentKey: "preferred",
        userVerification: "required",
      },
      supportedAlgorithmIDs: [-7, -257],
      timeout: 60_000,
    }),
    changed: true,
  }));

  const response = NextResponse.json(options, { headers: { "Cache-Control": "no-store" } });
  response.cookies.set(PASSKEY_CHALLENGE_COOKIE, issuePasskeyChallenge("registration", options.challenge), {
    httpOnly: true,
    sameSite: "strict",
    secure: isSecureRequest(request),
    path: "/api/passkeys",
    maxAge: PASSKEY_CHALLENGE_TTL_SECONDS,
  });
  return response;
}
