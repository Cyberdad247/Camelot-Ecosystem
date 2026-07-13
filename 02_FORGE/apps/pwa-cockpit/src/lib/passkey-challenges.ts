import "server-only";

import { randomBytes } from "node:crypto";

export const PASSKEY_CHALLENGE_COOKIE = "camelot_passkey_challenge";
export const PASSKEY_CHALLENGE_TTL_SECONDS = 5 * 60;
type ChallengeFlow = "registration" | "authentication";
type PendingChallenge = { challenge: string; flow: ChallengeFlow; expiresAt: number };

const globalChallenges = globalThis as typeof globalThis & {
  __camelotPasskeyChallenges?: Map<string, PendingChallenge>;
};
const challenges = globalChallenges.__camelotPasskeyChallenges ?? new Map<string, PendingChallenge>();
globalChallenges.__camelotPasskeyChallenges = challenges;

function prune(now = Date.now()) {
  challenges.forEach((challenge, id) => {
    if (challenge.expiresAt <= now) challenges.delete(id);
  });
}

export function issuePasskeyChallenge(flow: ChallengeFlow, challenge: string) {
  prune();
  const transactionId = randomBytes(24).toString("base64url");
  challenges.set(transactionId, {
    challenge,
    flow,
    expiresAt: Date.now() + PASSKEY_CHALLENGE_TTL_SECONDS * 1000,
  });
  return transactionId;
}

export function consumePasskeyChallenge(transactionId: string, flow: ChallengeFlow) {
  prune();
  const pending = challenges.get(transactionId);
  challenges.delete(transactionId);
  if (!pending || pending.flow !== flow || pending.expiresAt <= Date.now()) return null;
  return pending.challenge;
}
