import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function source(path) {
  return readFile(new URL(`../${path}`, import.meta.url), "utf8");
}

// Strip block comments and line comments from source so the doesNotMatch
// regex checks below don't trigger on documentation strings. The strip
// preserves line numbers for debugging by replacing stripped regions with
// spaces. URL-like strings (https://example.com) are preserved because
// the line-comment regex requires a non-`:` character before `//` (so the
// `//` in `://` of a URL scheme is not treated as a comment start).
function stripComments(text) {
  return text
    .replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " "))
    .replace(/(^|[^:\\])\/\/.*$/gm, (m) => m.replace(/[^\n]/g, " "));
}

test("V2 types mirror the Python CartridgeManifestV2 contract", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  // Mandatory V2 fields named by the user.
  assert.match(file, /hostApiVersion/);
  assert.match(file, /\bentry\b/);
  assert.match(file, /\bsha256\b/);
  assert.match(file, /\broutes\b/);
  assert.match(file, /\bresourceBudget\b/);
  // Trusted-publisher registry surface.
  assert.match(file, /publisher_id/);
  // V2 magic constants match the Python V1_LEGACY_SHA256 bridge.
  assert.match(file, /V1_LEGACY_SHA256 = "v1-legacy-import"/);
  assert.match(file, /V1_HOST_API_VERSION = "1"/);
  assert.match(file, /V2_HOST_API_VERSION = "2"/);
});

test("V2 platform exports hydrateV2Cartridge and verifyV2Archive", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  assert.match(file, /export async function hydrateV2Cartridge/);
  assert.match(file, /export async function verifyV2Archive/);
  assert.match(file, /export function getTrustedPublisher/);
  assert.match(file, /export function registerTrustedPublisher/);
  assert.match(file, /export function loadTrustedPublishers/);
  assert.match(file, /export (async )?function bootstrapPublishersFromBundle/);
  assert.match(file, /export function isV1Legacy/);
  assert.match(file, /export const V1_LEGACY_SHA256/);
});

test("V2 platform wires loadTrustedPublishers for Phase 3 public key distribution", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  // The bundle loader must be exported, accept string|object input,
  // fail loud on version mismatch, and populate PublisherInfo.publicKeys.
  assert.match(file, /export function loadTrustedPublishers/);
  assert.match(file, /input: string \| object/);
  // Version check (fail loud on unknown versions for security).
  assert.match(file, /bundle\.version !== "1"/);
  assert.match(file, /unsupported publisher bundle version/);
  // Shape validation: publisherId + trustedKids + publicKeys.
  // Source uses a template literal `publishers[${i}].publisherId`; match
  // the literal source text (the `{}` are escaped to be treated as
  // literal characters rather than regex quantifiers).
  assert.match(file, /publishers\[\$\{i\}\]\.publisherId/);
  assert.match(file, /publishers\[\$\{i\}\]\.trustedKids/);
  // publicKeys is extracted from the bundle and passed through. The code
  // uses shorthand `publicKeys,` (equivalent to `publicKeys: publicKeys,`)
  // so the regex matches either form.
  assert.match(file, /publicKeys[,\s]/);
  // The helper routes through registerTrustedPublisher so getTrustedPublisher
  // can read the populated publicKeys back.
  assert.match(file, /registerTrustedPublisher\(\{/);
});

test("V1 legacy shim routes through the existing V1 trusted loader", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  // The hydrator must call manifestFor from src/cartridges/registry for
  // V1 legacy shims so the seven built-in cartridges stay reachable.
  assert.match(file, /import \{ manifestFor \} from "@\/cartridges\/registry"/);
  assert.match(file, /if \(isV1Legacy\(manifest\)\)/);
  assert.match(file, /manifestFor\(manifest\.cartridge_id/);
  // The V2 namespace must NOT modify the V1 trusted loader map; it only
  // consumes the existing manifestFor() helper. Comments are stripped
  // so documentation strings (e.g. "the V1 trusted loader") don't trigger.
  const code = stripComments(file);
  assert.doesNotMatch(code, /trustedLoaders\[/);
  assert.doesNotMatch(code, /registry\.tsx/);
});

test("Browser ZIP reader is uncompressed-only and rejects compressed members", async () => {
  const file = await source("src/lib/v2/cartridge-zip.ts");
  // Wire format constants from PKWARE APPNOTE.TXT.
  assert.match(file, /SIG_LOCAL_FILE_HEADER = 0x04034b50/);
  assert.match(file, /SIG_CENTRAL_DIRECTORY = 0x02014b50/);
  assert.match(file, /SIG_EOCD = 0x06054b50/);
  // Compressed members are explicitly refused in Phase 2.
  assert.match(file, /unsupported compression method/);
  // Web Crypto for SHA-256.
  assert.match(file, /crypto\.subtle\.digest\("SHA-256"/);
  // Phase 2 hard cap to avoid OOM on a malicious giant archive.
  assert.match(file, /MAX_ZIP_BYTES/);
});

test("V2 archive verifier checks sha256 + publisher + signature in that order", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  // verifyV2Archive must read the zip, then check sha256 BEFORE the
  // publisher check, so a tampered payload never reaches the registry.
  assert.match(file, /const actual = await sha256Hex\(payloadEntry\.data\)/);
  assert.match(file, /if \(actual !== manifest\.sha256\)/);
  // Publisher check is on a known publisher id.
  assert.match(file, /getTrustedPublisher\(manifest\.publisher_id\)/);
  // V1 legacy path short-circuits before sha256 (no payload to verify).
  assert.match(file, /if \(isV1Legacy\(manifest\)\)[\s\S]+reason: "v1-legacy-import accepted"/);
});

test("V2 in-browser trusted publishers seed the legacy-v1 entry at boot", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  // The V1 legacy publisher is bootstrapped so any V1 cartridge passes
  // the publisher check without requiring the operator to register it.
  assert.match(file, /trustedPublishers\.set\("legacy-v1"/);
  // The default registered legacy publisher owns both "default" and
  // "legacy" kids for V1 cartridges signed by either old or new keys.
  assert.match(file, /trustedKids: \["default", "legacy"\]/);
  // The V1 publisher is active by default; deactivation is a deliberate
  // operator action (registerTrustedPublisher with active: false).
  assert.match(file, /active: true/);
});

test("V2 namespace is browser-only and does not import any shell-exec primitive", async () => {
  const platform = await source("src/lib/v2/cartridge-platform.ts");
  const zip = await source("src/lib/v2/cartridge-zip.ts");
  for (const file of [platform, zip]) {
    // Comments are stripped so documentation strings (e.g. "no child_process")
    // don't trigger the check.
    const code = stripComments(file);
    assert.doesNotMatch(code, /child_process|powershell|cmd\.exe|exec\(/i);
    assert.doesNotMatch(code, /fs\.readFileSync|fs\.writeFileSync/);
    assert.doesNotMatch(code, /require\(|process\.cwd/);
  }
});

test("V2 namespace does not import remote URLs (sandbox contract preserved)", async () => {
  const platform = await source("src/lib/v2/cartridge-platform.ts");
  const zip = await source("src/lib/v2/cartridge-zip.ts");
  for (const file of [platform, zip]) {
    // Comments are stripped so documentation strings don't trigger.
    // No http(s) imports, no dynamic URL imports, no eval of remote code.
    const code = stripComments(file);
    assert.doesNotMatch(code, /import\(["']https?:/);
    assert.doesNotMatch(code, /fetch\(["']https?:/);
  }
});

test("V2 archive verifier uses real Ed25519 verification via @noble/ed25519", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  // Ed25519 must be wired with real verification, not an explicit refusal.
  // The @noble/ed25519 package is imported and verifyEd25519Signature is
  // called in the ed25519 branch of verifyV2Archive.
  assert.match(file, /import \* as ed from "@noble\/ed25519"/);
  assert.match(file, /verifyEd25519Signature/);
  assert.match(file, /ed\.verify\(/);
  // The publisher must carry public keys for Ed25519 verification.
  assert.match(file, /publicKeys\[parsed\.kid\]/);
  // The HMAC path must come BEFORE the ed25519 branch so existing HMAC
  // cartridges continue to verify.
  const hmacIdx = file.indexOf('parsed.scheme === "hmac"');
  const edIdx = file.indexOf('parsed.scheme === "ed25519"');
  assert.ok(hmacIdx > 0 && edIdx > 0, "both signature schemes must be referenced");
  assert.ok(hmacIdx < edIdx, "HMAC branch must be evaluated before ed25519");
});

test("V2 hydrator emits CartridgeProps so CartridgeMount can render unchanged", async () => {
  const file = await source("src/lib/v2/cartridge-platform.ts");
  // The returned props must include the four V1 CartridgeProps fields the
  // existing CartridgeMount component reads.
  assert.match(file, /onCommand/);
  assert.match(file, /onInterrupt/);
  assert.match(file, /\bbusy\b/);
  assert.match(file, /\btransport\b/);
  // The legacy V1 path returns the V1 id so the rail nav highlights the
  // correct cartridge.
  assert.match(file, /id: v1\.id/);
});

test("Phase 3 Agent abstraction is edge-safe and exports the expected surface", async () => {
  const types = await source("src/lib/agents/types.ts");
  const orchestrator = await source("src/lib/agents/orchestrator.ts");
  const routing = await source("src/lib/agents/routing-agent.ts");
  const voice = await source("src/lib/agents/voice-agent.ts");
  const cartridge = await source("src/lib/agents/cartridge-agent.ts");
  const index = await source("src/lib/agents/index.ts");
  // Types: Agent, Tool, IntelligenceAdapter, AgentBudget.
  assert.match(types, /export interface Agent\b/);
  assert.match(types, /export interface Tool\b/);
  assert.match(types, /export interface IntelligenceAdapter\b/);
  assert.match(types, /export interface AgentBudget\b/);
  assert.match(types, /export interface AgentResult\b/);
  // Orchestrator: ReAct loop class with dispatch method.
  assert.match(orchestrator, /export class AgentOrchestrator\b/);
  assert.match(orchestrator, /async dispatch\(/);
  assert.match(orchestrator, /Action: toolName/);
  // Uniform discriminated union (no null) so the orchestrator handles
  // every case exhaustively.
  assert.match(orchestrator, /kind: "no_action"/);
  assert.match(orchestrator, /kind: "ok"/);
  assert.match(orchestrator, /kind: "json_error"/);
  // Balanced-brace scanning (not a naive non-greedy regex) so nested
  // JSON like `Action: foo({"a": {"b": 1}})` parses correctly.
  assert.match(orchestrator, /inString = false/);
  assert.match(orchestrator, /JSON\.parse\(/);
  // parseError field on AgentStep surfaces JSON parse failures in the
  // step trace. ok: false on parse error (hard failure, not success).
  assert.match(orchestrator, /parseError/);
  assert.match(orchestrator, /ok: false/);
  // Concrete agents: routingAgent, voiceAgent, cartridgeAgent.
  assert.match(routing, /export const routingAgent\b/);
  assert.match(routing, /checkAuth/);
  assert.match(routing, /validatePath/);
  assert.match(voice, /export const voiceAgent\b/);
  assert.match(cartridge, /export const cartridgeAgent\b/);
  assert.match(cartridge, /listCartridges/);
  // The cartridge agent's hardcoded list must match trustedLoaders keys
  // in the registry (kept in sync by this test pair).
  const registry = await source("src/cartridges/registry.tsx");
  const trustedLoadersMatch = registry.match(/trustedLoaders = \{([\s\S]*?)\} satisfies/);
  assert.ok(trustedLoadersMatch, "trustedLoaders block must be present in registry.tsx");
  const trustedLoadersBody = trustedLoadersMatch[1];
  // For each key in trustedLoaders, the cartridge agent must list it.
  // The trustedLoaders body has unquoted keys (e.g. `command:`) and
  // quoted keys (e.g. `"forge-law":`) — `\bkey\b` matches the key as a
  // whole word regardless of surrounding quotes or trailing `:`.
  for (const key of ["command", "factory", "forge-law", "intelligence",
                     "interphase", "device-hall", "mesh"]) {
    assert.match(trustedLoadersBody, new RegExp(`\\b${key}\\b`));
    assert.match(cartridge, new RegExp(`"${key}"`));
  }
  // Barrel re-exports the orchestrator.
  assert.match(index, /export \* from "\.\/orchestrator"/);
  // No agent file may import React or Node primitives (edge-safe).
  for (const file of [types, orchestrator, routing, voice, cartridge, index]) {
    const code = stripComments(file);
    assert.doesNotMatch(code, /from "react"/);
    assert.doesNotMatch(code, /process\./);
    assert.doesNotMatch(code, /require\(/);
  }
});

test("Edge-runtime health variant at /api/health/edge is minimal and React-free", async () => {
  const file = await source("src/app/api/health/edge/route.ts");
  // Must use edge runtime.
  assert.match(file, /export const runtime = "edge"/);
  // Must declare edge: true in the response shape.
  assert.match(file, /edge: true/);
  // Must NOT import the V1 cartridge registry (React).
  assert.doesNotMatch(file, /from "@\/cartridges\/registry"/);
  // Must NOT import the V2 platform (transitively imports React).
  assert.doesNotMatch(file, /from "@\/lib\/v2\/cartridge-platform"/);
  // Must NOT use Node primitives.
  const code = stripComments(file);
  assert.doesNotMatch(code, /process\./);
  assert.doesNotMatch(code, /require\(/);
  // Must probe the telemetry buffer (the only edge-safe check).
  assert.match(file, /getRecentEvents/);
});

test("Phase 4 orchestrator splits no_action into no_action + depth_mismatch and bounds current growth", async () => {
  const orchestrator = await source("src/lib/agents/orchestrator.ts");
  // parseAction + ParseResult are now exported so the /api/agent/run
  // route and downstream consumers can use the parser directly.
  assert.match(orchestrator, /export function parseAction\b/);
  assert.match(orchestrator, /export type ParseResult\b/);
  // The discriminated union now distinguishes a final answer (no
  // `Action:` header) from malformed LLM output (header matched but
  // braces didn't close). The two cases must be enumerated together
  // so the dispatch loop's switch stays exhaustive.
  assert.match(orchestrator, /kind: "no_action"/);
  assert.match(orchestrator, /kind: "depth_mismatch"/);
  // The scanner must cap the snippet to keep parseError bounded when
  // the LLM emits a huge unclosed blob.
  assert.match(orchestrator, /SNIPPET_MAX/);
  // Prompt growth is bounded by digesting older observations past a
  // threshold so long-running agents don't hit token limits.
  assert.match(orchestrator, /DIGEST_THRESHOLD/);
  assert.match(orchestrator, /\[digest: \$\{digestCount\}/);
  assert.match(orchestrator, /buildCurrent/);
  // Dispatch must handle the new depth_mismatch case (hard failure,
  // mirrors the json_error shape).
  assert.match(orchestrator, /parsed\.kind === "depth_mismatch"/);
  assert.match(orchestrator, /action parse error: depth_mismatch/);
});

test("Phase 4 barrel exports getAgentById and re-exports the orchestrator", async () => {
  const index = await source("src/lib/agents/index.ts");
  // The orchestrator surface (AgentOrchestrator, parseAction, ParseResult)
  // is re-exported from the barrel so consumers can
  // `import { AgentOrchestrator, parseAction, ParseResult } from "@/lib/agents"`.
  assert.match(index, /export \* from "\.\/orchestrator"/);
  // The three named agents are re-exported for direct access.
  assert.match(index, /export \{ routingAgent, voiceAgent, cartridgeAgent \}/);
  // getAgentById resolves short ids ("routing" | "voice" | "cartridge")
  // against the AGENT_REGISTRY map. Lookup must be case-insensitive
  // so clients sending "Routing" or "VOICE" still resolve.
  assert.match(index, /export function getAgentById\b/);
  assert.match(index, /const AGENT_REGISTRY: Record<string, Agent>/);
  assert.match(index, /routing: routingAgent/);
  assert.match(index, /voice: voiceAgent/);
  assert.match(index, /cartridge: cartridgeAgent/);
  assert.match(index, /id\.toLowerCase\(\)/);
});

test("Phase 4 /api/agent/run edge route is edge-safe and wires the shared gate", async () => {
  const route = await source("src/app/api/agent/run/route.ts");
  // Edge runtime declaration matches the health/edge route style.
  assert.match(route, /export const runtime = "edge"/);
  assert.match(route, /export const dynamic = "force-dynamic"/);
  // Bearer validation reuses the shared gate so this handler stays
  // in lockstep with middleware.ts.
  assert.match(route, /import \{ isValidBearerToken \} from "@\/lib\/security\/gate"/);
  assert.match(route, /isValidBearerToken\(authHeader\)/);
  // Agent lookup + dispatch through the shared orchestrator.
  assert.match(route, /getAgentById/);
  assert.match(route, /AgentOrchestrator/);
  // POST handler shape.
  assert.match(route, /export async function POST\(/);
  // Phase 5: the route must use the env-configurable factory from
  // llm-adapter.ts (not the old inline StubIntelligenceAdapter class).
  assert.match(route, /createLLMAdapter/);
  assert.match(route, /from "@\/lib\/agents\/llm-adapter"/);
  assert.doesNotMatch(route, /class StubIntelligenceAdapter/);
  // No Node primitives (edge-safe).
  const code = stripComments(route);
  assert.doesNotMatch(code, /from "react"/);
  assert.doesNotMatch(code, /process\./);
  assert.doesNotMatch(code, /require\(/);
  assert.doesNotMatch(code, /fs\.|child_process|powershell/);
});
