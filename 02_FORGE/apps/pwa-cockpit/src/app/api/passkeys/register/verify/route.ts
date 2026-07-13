import { verifyRegistrationResponse, type RegistrationResponseJSON } from "@simplewebauthn/server";
import { NextRequest, NextResponse } from "next/server";
import { isAuthorized, isCrossSiteRequest } from "@/lib/cockpit-auth";
import { PASSKEY_CHALLENGE_COOKIE, consumePasskeyChallenge } from "@/lib/passkey-challenges";
import { encodePublicKey, withPasskeyStore } from "@/lib/passkey-store";
import { webauthnContext } from "@/lib/webauthn-context";

export async function POST(request: NextRequest) {
  if (!isAuthorized(request)) return NextResponse.json({ verified: false, message: "Operator session required." }, { status: 401 });
  if (isCrossSiteRequest(request)) return NextResponse.json({ verified: false, message: "Cross-site passkey requests are blocked." }, { status: 403 });
  if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) {
    return NextResponse.json({ verified: false, message: "Content-Type must be application/json." }, { status: 415 });
  }

  const transactionId = request.cookies.get(PASSKEY_CHALLENGE_COOKIE)?.value ?? "";
  const challenge = consumePasskeyChallenge(transactionId, "registration");
  if (!challenge) return NextResponse.json({ verified: false, message: "Passkey challenge expired or was already used." }, { status: 409 });

  let body: RegistrationResponseJSON;
  try {
    body = await request.json() as RegistrationResponseJSON;
  } catch {
    return NextResponse.json({ verified: false, message: "Invalid passkey response." }, { status: 400 });
  }

  try {
    const { rpID, origin } = webauthnContext(request);
    const verification = await verifyRegistrationResponse({
      response: body,
      expectedChallenge: challenge,
      expectedOrigin: origin,
      expectedRPID: rpID,
      requireUserVerification: true,
    });
    if (!verification.verified || !verification.registrationInfo) throw new Error("Passkey verification failed.");
    const info = verification.registrationInfo;
    await withPasskeyStore(async (store) => {
      if (store.credentials.some((credential) => credential.id === info.credential.id)) {
        throw new Error("This passkey is already registered.");
      }
      store.credentials.push({
        id: info.credential.id,
        publicKey: encodePublicKey(info.credential.publicKey),
        counter: info.credential.counter,
        transports: info.credential.transports,
        deviceType: info.credentialDeviceType,
        backedUp: info.credentialBackedUp,
        createdAt: new Date().toISOString(),
      });
      return { result: undefined, changed: true };
    });
    return NextResponse.json({ verified: true });
  } catch (error) {
    return NextResponse.json({
      verified: false,
      message: error instanceof Error ? error.message : "Passkey registration failed.",
    }, { status: 400 });
  }
}
