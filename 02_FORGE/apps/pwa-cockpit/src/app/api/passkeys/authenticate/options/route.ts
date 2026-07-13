import { generateAuthenticationOptions } from "@simplewebauthn/server";
import { NextRequest, NextResponse } from "next/server";
import { allowPairingAttempt, isCrossSiteRequest, isSecureRequest } from "@/lib/cockpit-auth";
import { PASSKEY_CHALLENGE_COOKIE, PASSKEY_CHALLENGE_TTL_SECONDS, issuePasskeyChallenge } from "@/lib/passkey-challenges";
import { withPasskeyStore } from "@/lib/passkey-store";
import { webauthnContext } from "@/lib/webauthn-context";

export async function POST(request: NextRequest) {
  if (isCrossSiteRequest(request)) return NextResponse.json({ message: "Cross-site passkey requests are blocked." }, { status: 403 });
  if (!allowPairingAttempt(request)) return NextResponse.json({ message: "Too many authentication attempts. Retry in one minute." }, { status: 429 });

  const { rpID } = webauthnContext(request);
  let options: Awaited<ReturnType<typeof generateAuthenticationOptions>>;
  try {
    options = await withPasskeyStore(async (store) => {
      if (store.credentials.length === 0) throw new Error("No passkey is enrolled.");
      return {
        result: await generateAuthenticationOptions({
          rpID,
          allowCredentials: store.credentials.map((credential) => ({ id: credential.id, transports: credential.transports })),
          userVerification: "required",
          timeout: 60_000,
        }),
      };
    });
  } catch (error) {
    return NextResponse.json({ message: error instanceof Error ? error.message : "No passkey is enrolled." }, { status: 404 });
  }

  const response = NextResponse.json(options, { headers: { "Cache-Control": "no-store" } });
  response.cookies.set(PASSKEY_CHALLENGE_COOKIE, issuePasskeyChallenge("authentication", options.challenge), {
    httpOnly: true,
    sameSite: "strict",
    secure: isSecureRequest(request),
    path: "/api/passkeys",
    maxAge: PASSKEY_CHALLENGE_TTL_SECONDS,
  });
  return response;
}
