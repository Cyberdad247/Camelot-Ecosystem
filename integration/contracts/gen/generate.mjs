#!/usr/bin/env node
// Generate the Go skill registry and the TypeScript skill contract from the
// canonical manifest (contracts/skills.manifest.json).
//
// WHY A MANIFEST AND NOT "GO IS THE SOURCE":
//   Go owns policy enforcement, TypeScript owns the UI contract, and Rust may
//   own node-side effects later. Letting one of them own the product
//   definition makes the other two downstream of an implementation language.
//   The manifest is downstream of nobody.
//
// The generated files are COMMITTED. Nothing generates at build time, so
// `make dev-up` keeps working with no toolchain beyond the compilers it
// already needs. `make test` runs check-generated.sh, which regenerates into
// a temp dir and diffs — drift fails the build locally, not only in CI.
//
// Zero dependencies. Output must be byte-stable for the drift check to work.

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const here = fileURLToPath(new URL('.', import.meta.url));
// CAMELOT_SKILLS_MANIFEST lets a caller validate a candidate manifest without
// touching the committed one — tests need that, and mutating the real file
// would race with any suite that reads it from a parallel worker.
const MANIFEST = process.env.CAMELOT_SKILLS_MANIFEST || `${here}../skills.manifest.json`;

const VALID_EFFECTS = new Set(['read_only', 'local_effect', 'remote_effect']);
const VALID_IDEMPOTENCY = new Set(['natural', 'lease_single_use']);
const VALID_RETRY = new Set(['safe', 'never']);

/** Fail loudly on a malformed manifest — a bad catalog is a policy bug. */
function validate(m) {
  const errors = [];
  if (m.manifestVersion !== 1) errors.push(`unsupported manifestVersion ${m.manifestVersion}`);
  if (typeof m.policyVersion !== 'string' || !m.policyVersion) errors.push('policyVersion must be a non-empty string');
  if (!Array.isArray(m.skills) || m.skills.length === 0) errors.push('skills must be a non-empty array');

  const seen = new Set();
  const phraseOwner = new Map();
  for (const s of m.skills ?? []) {
    const at = `skill ${s.id ?? '<missing id>'}`;
    if (!s.id) errors.push(`${at}: id is required`);
    if (seen.has(s.id)) errors.push(`${at}: duplicate id`);
    seen.add(s.id);
    if (!Number.isInteger(s.tier) || s.tier < 1 || s.tier > 3) errors.push(`${at}: tier must be 1..3`);
    if (!VALID_EFFECTS.has(s.effect)) errors.push(`${at}: effect must be one of ${[...VALID_EFFECTS].join('|')}`);
    if (!VALID_IDEMPOTENCY.has(s.idempotency)) errors.push(`${at}: bad idempotency`);
    if (!VALID_RETRY.has(s.retry)) errors.push(`${at}: bad retry`);
    if (!Array.isArray(s.intent?.phrases) || s.intent.phrases.length === 0) {
      errors.push(`${at}: intent.phrases must be a non-empty array`);
    }
    for (const p of s.intent?.phrases ?? []) {
      if (p !== p.toLowerCase()) errors.push(`${at}: phrase ${JSON.stringify(p)} must be lower-case`);
      // Two skills claiming the identical phrase is unresolvable by any
      // precedence rule, so it is a manifest error rather than a runtime coin toss.
      if (phraseOwner.has(p)) errors.push(`${at}: phrase ${JSON.stringify(p)} already claimed by ${phraseOwner.get(p)}`);
      phraseOwner.set(p, s.id);
    }
    // Tier 3 without confirmation would silently downgrade a human gate.
    if (s.tier === 3 && !s.confirmationRequired) errors.push(`${at}: tier 3 requires confirmationRequired:true`);
    // THE ONE THAT MATTERS MOST. Tier is what the broker gates on, so a
    // tier-1 durable skill would take the no-lease branch in handleTurn and
    // produce a real side effect with no authorization at all.
    if (s.effect !== 'read_only' && s.tier < 2) {
      errors.push(`${at}: effect ${s.effect} requires tier >= 2 — tier 1 runs without a lease`);
    }
    // A durable effect that is retryable would let one approval act twice.
    if (s.effect !== 'read_only' && s.retry !== 'never') {
      errors.push(`${at}: effect ${s.effect} must set retry:"never"`);
    }
    if (s.effect !== 'read_only' && s.idempotency !== 'lease_single_use') {
      errors.push(`${at}: effect ${s.effect} must set idempotency:"lease_single_use"`);
    }
  }
  if (errors.length) {
    console.error('skills.manifest.json is invalid:');
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }
}

const goString = (s) => JSON.stringify(s);
const goStrings = (xs) => `[]string{${xs.map(goString).join(', ')}}`;

/** Emit gofmt-aligned keyed fields, so the generated file is already
 *  canonical and `gofmt -l` stays silent without invoking gofmt here (the
 *  drift check would otherwise need the Go toolchain too). */
function goFields(pairs) {
  const width = Math.max(...pairs.map(([k]) => k.length)) + 1; // +1 for ':'
  return pairs.map(([k, v]) => `${(k + ':').padEnd(width)} ${v}`);
}

function renderGo(m) {
  const rows = m.skills
    .map((s) => {
      const f = goFields([
        ['ID', goString(s.id)],
        ['Version', String(s.version)],
        ['Tier', String(s.tier)],
        ['Effect', goString(s.effect)],
        ['Effectful', String(s.tier >= 2)],
        ['Durable', String(s.effect !== 'read_only')],
        ['ConfirmationRequired', String(Boolean(s.confirmationRequired))],
        ['Phrases', goStrings(s.intent.phrases)],
        ['Priority', String(s.intent.priority ?? 0)],
        ['Idempotency', goString(s.idempotency)],
        ['Retry', goString(s.retry)],
        ['ArtifactKind', goString(s.artifactKind)],
        ['AuditKind', goString(s.audit.kind)],
        ['RedactTranscript', String(Boolean(s.audit.redactTranscript))],
      ]);
      return `\t{\n\t\t${f.join(',\n\t\t')},\n\t},`;
    })
    .join('\n');

  return `// Code generated by contracts/gen/generate.mjs. DO NOT EDIT.
// Source of truth: integration/contracts/skills.manifest.json
// Regenerate with \`make generate\`; \`make test\` fails on drift.

package main

// manifestVersion / manifestPolicyVersion pin the catalog the binary was
// built against, so an audit record can be traced to a definition.
const (
\tmanifestVersion       = ${m.manifestVersion}
\tmanifestPolicyVersion = ${goString(m.policyVersion)}
)

// Skill is one governed capability, as declared in the manifest.
//
//\tEffectful — tier >= 2: requires an approved lease before the broker runs it.
//\tDurable   — effect != read_only: produces a side effect outside this process.
//
// Effectful and Durable are independent: a tier-2 draft is Effectful (policy
// gates it) but not Durable (nothing outside memory changes).
type Skill struct {
\tID                   string
\tVersion              int
\tTier                 int
\tEffect               string
\tEffectful            bool
\tDurable              bool
\tConfirmationRequired bool
\tPhrases              []string
\tPriority             int
\tIdempotency          string
\tRetry                string
\tArtifactKind         string
\tAuditKind            string
\tRedactTranscript     bool
}

var skillRegistry = []Skill{
${rows}
}
`;
}

function renderTS(m) {
  const rows = m.skills
    .map((s) => {
      const f = [
        `id: ${JSON.stringify(s.id)}`,
        `version: ${s.version}`,
        `tier: ${s.tier}`,
        `effect: ${JSON.stringify(s.effect)}`,
        `effectful: ${s.tier >= 2}`,
        `durable: ${s.effect !== 'read_only'}`,
        `confirmationRequired: ${Boolean(s.confirmationRequired)}`,
        `phrases: [${s.intent.phrases.map((p) => JSON.stringify(p)).join(', ')}]`,
        `priority: ${s.intent.priority ?? 0}`,
        `idempotency: ${JSON.stringify(s.idempotency)}`,
        `retry: ${JSON.stringify(s.retry)}`,
        `artifactKind: ${JSON.stringify(s.artifactKind)}`,
        `auditKind: ${JSON.stringify(s.audit.kind)}`,
        `redactTranscript: ${Boolean(s.audit.redactTranscript)}`,
      ];
      return `  {\n    ${f.join(',\n    ')},\n  },`;
    })
    .join('\n');

  return `// Code generated by contracts/gen/generate.mjs. DO NOT EDIT.
// Source of truth: integration/contracts/skills.manifest.json
// Regenerate with \`make generate\`; \`make test\` fails on drift.

import type { SkillTier } from './types.js';

export const MANIFEST_VERSION = ${m.manifestVersion};
export const MANIFEST_POLICY_VERSION = ${JSON.stringify(m.policyVersion)};

/** How far a skill's consequences reach outside this process. */
export type SkillEffect = 'read_only' | 'local_effect' | 'remote_effect';

export interface SkillDefinition {
  readonly id: string;
  readonly version: number;
  readonly tier: SkillTier;
  readonly effect: SkillEffect;
  /** tier >= 2: the broker requires an approved lease. */
  readonly effectful: boolean;
  /** effect !== 'read_only': something outside this process changes. */
  readonly durable: boolean;
  readonly confirmationRequired: boolean;
  /** Lower-cased trigger phrases; longest match wins, then priority. */
  readonly phrases: readonly string[];
  readonly priority: number;
  readonly idempotency: 'natural' | 'lease_single_use';
  readonly retry: 'safe' | 'never';
  readonly artifactKind: string;
  readonly auditKind: string;
  readonly redactTranscript: boolean;
}

export const SKILLS: readonly SkillDefinition[] = [
${rows}
] as const;

export function skillById(id: string): SkillDefinition | null {
  return SKILLS.find((s) => s.id === id) ?? null;
}
`;
}

const manifest = JSON.parse(readFileSync(MANIFEST, 'utf8'));
validate(manifest);

const targets = [
  [`${here}../../gateway/skills_gen.go`, renderGo(manifest)],
  [`${here}../src/skills.gen.ts`, renderTS(manifest)],
];

const outDir = process.argv[2]; // optional: write elsewhere (drift check)
for (const [path, content] of targets) {
  const dest = outDir ? `${outDir}/${path.split('/').pop()}` : path;
  writeFileSync(dest, content);
  if (!outDir) console.log(`generated ${dest.replace(/.*\/integration\//, 'integration/')}`);
}
