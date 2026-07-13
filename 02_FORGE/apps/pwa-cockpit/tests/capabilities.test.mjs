import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function source(path) {
  return readFile(new URL(`../${path}`, import.meta.url), "utf8");
}

const CAPABILITIES = [
  "status.read",
  "voice.use",
  "vision.capture",
  "approval.manage",
  "device.control",
  "forge.execute",
  "cartridge.install",
];

test("capabilities module exports the seven V2 capability scopes", async () => {
  const file = await source("src/lib/capabilities.ts");
  for (const capability of CAPABILITIES) {
    assert.match(file, new RegExp(`\\b${capability.replace(/\./g, "\\.")}\\b`));
  }
  assert.match(file, /export const ALL_CAPABILITIES/);
  assert.match(file, /export type Capability/);
  assert.match(file, /export function issueCapabilityGrant/);
  assert.match(file, /export function verifyCapabilityGrant/);
  assert.match(file, /export function requireCapability/);
  assert.match(file, /export function directiveToCapability/);
  assert.match(file, /export class CapabilityRejected/);
  // Phase 1 hardening (Item 2) exports for tests / recovery flows:
  assert.match(file, /export function clearSeenNonces/);
  // Phase 1.5 hardening (Q3) audit log helper:
  assert.match(file, /export function appendGrantAuditLog/);
  assert.match(file, /export type GrantAuditRecord/);
});

test("capability grants are HMAC(SHA-256, COCKPIT_TOKEN) over the v3 context", async () => {
  const file = await source("src/lib/capabilities.ts");
  assert.match(file, /createHmac\("sha256", key\)/);
  assert.match(file, /camelot-pwa-cockpit\/capability-grant\/v3/);
  assert.match(file, /CAPABILITY_GRANT_TTL_SECONDS\s*=\s*90/);
  assert.match(file, /timingSafeEqual/);
  assert.match(file, /consumeCapabilityNonce/);
  assert.match(file, /CAPABILITY_NONCE_TTL_MS/);
  assert.match(file, /randomBytes\(18\)/);
  // Phase 1 hardening (Item 2): disk-backed nonce store uses fsyncSync and
  // copyFileSync for atomic durability.
  assert.match(file, /fsyncSync/);
  assert.match(file, /copyFileSync/);
  assert.match(file, /NONCE_STORE_PATH/);
  assert.match(file, /NONCE_BACKUP_PATH/);
  assert.match(file, /\.corrupt-/);
  // Architecture-style safety grep: no shell exec, no child_process, no
  // PowerShell, no cmd.exe, no .exec() literals.
  assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
});

test("approval-grant encloses the V2 capability binding without regressing V1/V2 strings", async () => {
  const file = await source("src/lib/approval-grant.ts");
  assert.match(file, /GRANT_TTL_SECONDS = 90/);
  assert.match(file, /GRANT_CONTEXT_V2/);
  assert.match(file, /cartridgeDigest/);
  assert.match(file, /commandDigest/);
  assert.match(file, /createHmac\("sha256", key\)/);
  assert.match(file, /capability\?:\s*Capability/);
  assert.match(file, /payloadDigest\?:\s*string/);
  assert.match(file, /export type ApprovalGrantBinding/);
  assert.match(file, /target\?:\s*string/);
});

test("forge-law return type widens to ApprovalGrantBinding without any cast", async () => {
  const file = await source("src/lib/forge-law.ts");
  assert.match(file, /import type \{ ApprovalGrantBinding \} from "\.\/approval-grant"/);
  assert.match(file, /:\s*ApprovalGrantBinding\s*\|\s*null/);
  assert.match(file, /forgeApprovalBinding\(command:\s*string\):\s*ApprovalGrantBinding\s*\|\s*null/);
});

test("approvals [id] route threads capability binding into the v2 grant without a widening cast", async () => {
  const file = await source("src/app/api/approvals/[id]/route.ts");
  assert.match(file, /forgeApprovalBinding\(approval\.command\)/);
  assert.match(file, /issueApprovalGrant\(approval\.id, approval\.command, binding\)/);
  assert.match(file, /execution_blocked/);
  assert.match(file, /createReceipt\(approval\.command, "executed"\)/);
  assert.match(file, /resolveDeviceAction/);
  assert.match(file, /requireCapability/);
  assert.match(file, /CapabilityRejected/);
  assert.match(file, /missing capability grant for/);
  // Phase 1 hardening (Item 4): no widening cast remains on forgeApprovalBinding.
  assert.doesNotMatch(file, /forgeApprovalBinding\([^)]*\)\s*as\s*ApprovalGrantBinding/);
  assert.doesNotMatch(file, /child_process|cmd\.exe|powershell/);
});

test("commands route REQUIRES capability grants on mutating runes", async () => {
  const file = await source("src/app/api/commands/route.ts");
  assert.match(file, /readOnlyRunes = new Set\(\["\/\/STATUS"\]\)/);
  assert.match(file, /isRunic && !readOnlyRunes\.has/);
  assert.match(file, /isCrossSiteRequest/);
  assert.match(file, /isAuthorized/);
  assert.match(file, /requireCapability/);
  assert.match(file, /directiveToCapability/);
  assert.match(file, /CapabilityRejected/);
  assert.match(file, /no harness task was queued/);
  assert.match(file, /missing capability grant for/);
  // Phase 1 hardening (Item 1): the gate fires unconditionally on mutating
  // runes; the opt-in fallback is removed.
  assert.doesNotMatch(file, /runeCapability && incomingGrant/);
  assert.doesNotMatch(file, /child_process/);
  assert.doesNotMatch(file, /\bexec\s*\(/);
  assert.doesNotMatch(file, /directive === "\/\/LAUNCH_CELL"/);
  assert.doesNotMatch(file, /executeRunic/);
});

test("session route advertises per-session capability scopes via sidecar cookie", async () => {
  const file = await source("src/app/api/session/route.ts");
  // Architecture gates must remain intact:
  assert.match(file, /httpOnly: true/);
  assert.match(file, /sameSite: "strict"/);
  assert.match(file, /OPERATOR_SESSION_TTL_SECONDS/);
  assert.match(file, /secure: isSecureRequest\(request\)/);
  // Phase 1 hardening (Item 3): sidecar cookie advertised and cleared on logout.
  assert.match(file, /capabilities:\s*session\.authenticated\s*\?\s*operatorCapabilities\(request\)/);
  assert.match(file, /CAPABILITIES_COOKIE/);
  assert.match(file, /capabilitiesCookieValue\(defaultOperatorCapabilities\(\)\)/);
  assert.match(file, /maxAge:\s*0/);
});

test("cockpit-auth exposes sidecar cookie mint/verify and default-capability loader", async () => {
  const file = await source("src/lib/cockpit-auth.ts");
  // Architecture gates:
  assert.match(file, /CAMELOT_COCKPIT_TOKEN/);
  assert.match(file, /timingSafeEqual/);
  assert.match(file, /createHmac\("sha256", token\)/);
  assert.match(file, /randomBytes\(18\)/);
  assert.match(file, /expiresAt <= nowSeconds/);
  assert.match(file, /current\.count >= 5/);
  assert.match(file, /process\.env\.NODE_ENV !== "production"/);
  assert.doesNotMatch(file, /x-forwarded-host/);
  assert.match(file, /x-forwarded-proto/);
  // Phase 1 hardening (Item 3) new exports:
  assert.match(file, /export const CAPABILITIES_COOKIE = "camelot_operator_caps"/);
  assert.match(file, /camelot-pwa-cockpit\/capability-scope\/v1/);
  assert.match(file, /export function capabilitiesCookieValue/);
  assert.match(file, /export function operatorCapabilities/);
  assert.match(file, /export function defaultOperatorCapabilities/);
  assert.match(file, /CAMELOT_COCKPIT_DEFAULT_CAPABILITIES/);
});

test("bearer parser replaces the original regex without re-triggering safety grep", async () => {
  const file = await source("src/lib/capabilities.ts");
  assert.match(file, /function parseBearerOrRaw/);
  assert.match(file, /slice\(0, 6\)\.toLowerCase\(\)\s*!==\s*"bearer"/);
  assert.match(file, /\.test\(trimmed\[i\]\)/);
  // Source must not reintroduce any .exec() literal in the helper.
  const helperExec = new RegExp("\\.exec\\(");
  assert.doesNotMatch(file, helperExec);
});

test("POST /api/capabilities mints short-lived grants gated by session capability or admin override", async () => {
  const file = await source("src/app/api/capabilities/route.ts");
  // Route shape:
  assert.match(file, /import \{ NextRequest, NextResponse \} from "next\/server"/);
  assert.match(file, /export async function POST/);
  // Hardening gates (defense in depth, mirrors the mutating-rune route):
  assert.match(file, /isAuthorized\(request\)/);
  assert.match(file, /isCrossSiteRequest\(request\)/);
  assert.match(file, /content-type.*application\/json/is);
  // Authorization model: session capabilities OR admin override.
  assert.match(file, /operatorCapabilities\(request\)/);
  assert.match(file, /CAMELOT_COCKPIT_GRANT_ADMIN/);
  assert.match(file, /Session does not carry/);
  // Validation + binding:
  assert.match(file, /ALL_CAPABILITIES\.includes/);
  assert.match(file, /digestPayload/);
  // The route validates payloadDigest against a SHA-256 hex pattern.
  const sha256Pattern = new RegExp("\\[a-f0-9\\]\\{64\\}");
  assert.match(file, sha256Pattern);
  assert.match(file, /issueCapabilityGrant/);
  // Response shape: curated claims (no grantId, no nonce).
  assert.match(file, /capability:\s*minted\.claims\.capability/);
  assert.match(file, /payloadDigest:\s*minted\.claims\.payloadDigest/);
  assert.match(file, /target:\s*minted\.claims\.target/);
  assert.match(file, /approvalId:\s*minted\.claims\.approvalId/);
  assert.match(file, /issuedAt:\s*minted\.claims\.issuedAt/);
  assert.match(file, /expiresAt:\s*minted\.claims\.expiresAt/);
  assert.match(file, /expiresInSeconds/);
  assert.match(file, /Cache-Control.*no-store/);
  assert.match(file, /X-Camelot-Capability-Grant-Version/);
  // Admin-override path is audit-logged.
  assert.match(file, /appendGrantAuditLog/);
  assert.match(file, /admin-override/);
  // Safety grep: no shell exec / child_process / PowerShell.
  assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
});

test("forge-grant client helper wraps the mint endpoint with typed success/failure union", async () => {
  const file = await source("src/lib/forge-grant.ts");
  assert.match(file, /"use client"/);
  assert.match(file, /export async function forgeCapabilityGrant/);
  assert.match(file, /export type ForgeGrantRequest/);
  assert.match(file, /export type ForgeGrantSuccess/);
  assert.match(file, /export type ForgeGrantFailure/);
  assert.match(file, /export type ForgeGrantResult/);
  // Posts to the mint endpoint with the right contract:
  assert.match(file, /fetch\("\/api\/capabilities"/);
  assert.match(file, /method:\s*"POST"/);
  assert.match(file, /credentials:\s*"same-origin"/);
  assert.match(file, /cache:\s*"no-store"/);
  assert.match(file, /content-type.*application\/json/);
  // Typed failure path covers network errors and HTTP errors.
  assert.match(file, /ok:\s*false/);
  assert.match(file, /ok:\s*true/);
  // Safety grep: no client-side shell exec.
  assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
});

test("grant-mint audit log is append-only JSONL with best-effort semantics", async () => {
  const file = await source("src/lib/capabilities.ts");
  assert.match(file, /GRANT_AUDIT_LOG_PATH/);
  assert.match(file, /pwa_cockpit_grant_audit\.log/);
  assert.match(file, /export function appendGrantAuditLog/);
  assert.match(file, /appendFileSync/);
  assert.match(file, /mkdirSync/);
  // Best-effort: disk failure does not block the mint response.
  assert.match(file, /best-effort/);
  // Audit record is single-line JSON.
  assert.match(file, /JSON\.stringify\(record\)/);
  // Safety grep.
  assert.doesNotMatch(file, /child_process|powershell|cmd\.exe|exec\(/i);
});
