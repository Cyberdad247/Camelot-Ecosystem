import { verifyAuthenticationResponse, type AuthenticationResponseJSON } from "@simplewebauthn/server";
import { NextRequest, NextResponse } from "next/server";
import { OPERATOR_COOKIE, OPERATOR_SESSION_TTL_SECONDS, isCrossSiteRequest, isSecureRequest, sessionCookieValue } from "@/lib/cockpit-auth";
import { PASSKEY_CHALLENGE_COOKIE, consumePasskeyChallenge } from "@/lib/passkey-challenges";
import { decodePublicKey, withPasskeyStore } from "@/lib/passkey-store";
import { webauthnContext } from "@/lib/webauthn-context";

export async function POST(request: NextRequest) {
  if (isCrossSiteRequest(request)) return NextResponse.json({ verified: false, message: "Cross-site passkey requests are blocked." }, { status: 403 });
  if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) {
    return NextResponse.json({ verified: false, message: "Content-Type must be application/json." }, { status: 415 });
  }
  const transactionId = request.cookies.get(PASSKEY_CHALLENGE_COOKIE)?.value ?? "";
  const challenge = consumePasskeyChallenge(transactionId, "authentication");
  if (!challenge) return NextResponse.json({ verified: false, message: "Passkey challenge expired or was already used." }, { status: 409 });

  let body: AuthenticationResponseJSON;
  try {
    body = await request.json() as AuthenticationResponseJSON;
  } catch {
    return NextResponse.json({ verified: false, message: "Invalid passkey response." }, { status: 400 });
  }

  try {
    const { rpID, origin } = webauthnContext(request);
    await withPasskeyStore(async (store) => {
      const stored = store.credentials.find((credential) => credential.id === body.id);
      if (!stored) throw new Error("Passkey is not registered on this cockpit.");
      const verification = await verifyAuthenticationResponse({
        response: body,
        expectedChallenge: challenge,
        expectedOrigin: origin,
        expectedRPID: rpID,
        credential: {
          id: stored.id,
          publicKey: decodePublicKey(stored.publicKey),
          counter: stored.counter,
          transports: stored.transports,
        },
        requireUserVerification: true,
      });
      if (!verification.verified) throw new Error("Passkey verification failed.");
      stored.counter = verification.authenticationInfo.newCounter;
      stored.deviceType = verification.authenticationInfo.credentialDeviceType;
      stored.backedUp = verification.authenticationInfo.credentialBackedUp;
      stored.lastUsedAt = new Date().toISOString();
      return { result: undefined, changed: true };
    });

    const response = NextResponse.json({ verified: true });
    response.cookies.set(OPERATOR_COOKIE, sessionCookieValue(), {
      httpOnly: true,
      sameSite: "strict",
      secure: isSecureRequest(request),
      path: "/",
      maxAge: OPERATOR_SESSION_TTL_SECONDS,
    });
    response.cookies.set(PASSKEY_CHALLENGE_COOKIE, "", { path: "/api/passkeys", maxAge: 0 });
    return response;
  } catch (error) {
    return NextResponse.json({
      verified: false,
      message: error instanceof Error ? error.message : "Passkey authentication failed.",
    }, { status: 401 });
  }
}
