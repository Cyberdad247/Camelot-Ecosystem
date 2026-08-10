// tests/parse-action.test.ts
//
// Phase 5: runtime tests for `parseAction` in src/lib/agents/orchestrator.ts.
// The existing v2.test.mjs uses regex-on-source checks; this file actually
// imports and exercises the function so a logic bug in the scanner
// (wrong depth tracking, wrong snippet slice) would be caught.
//
// Runs under `node --import tsx --test tests/*.test.ts` (see package.json).

import assert from "node:assert/strict";
import test from "node:test";
import { parseAction } from "../src/lib/agents/orchestrator";
import type { ParseResult } from "../src/lib/agents/orchestrator";

// ── no_action ───────────────────────────────────────────────────────────

test("parseAction returns no_action for inputs with no Action: header", () => {
  assert.deepEqual(parseAction(""), { kind: "no_action" });
  assert.deepEqual(parseAction("   \n\t  "), { kind: "no_action" });
  assert.deepEqual(parseAction("I think therefore I am."), {
    kind: "no_action",
  });
  // "Action:" without the opening paren is NOT an action header.
  assert.deepEqual(parseAction("Action: but no parens"), {
    kind: "no_action",
  });
});

// ── ok ──────────────────────────────────────────────────────────────────

test("parseAction returns ok for a well-formed action call", () => {
  assert.deepEqual(parseAction('Action: toolName({"key": "value"})'), {
    kind: "ok",
    name: "toolName",
    args: { key: "value" },
  });
});

test("parseAction returns ok for an empty-args action call", () => {
  assert.deepEqual(parseAction("Action: check_auth({})"), {
    kind: "ok",
    name: "check_auth",
    args: {},
  });
});

test("parseAction handles action names with underscores", () => {
  // The regex [A-Za-z_][A-Za-z0-9_]* allows underscores in the name.
  assert.deepEqual(parseAction("Action: my_long_tool_name({})"), {
    kind: "ok",
    name: "my_long_tool_name",
    args: {},
  });
});

test("parseAction does NOT unbalance on string-embedded }", () => {
  // The `}` inside the string value must be skipped by the in-string
  // state machine, not treated as a closing brace.
  assert.deepEqual(parseAction('Action: foo({"a": "}"})'), {
    kind: "ok",
    name: "foo",
    args: { a: "}" },
  });
});

test("parseAction handles backslash-escaped quotes inside strings", () => {
  // The `\"` inside the string value must be treated as an escaped
  // quote, not a string terminator.
  assert.deepEqual(parseAction('Action: foo({"a": "\\""})'), {
    kind: "ok",
    name: "foo",
    args: { a: '"' },
  });
});

test("parseAction handles nested objects and arrays", () => {
  assert.deepEqual(parseAction('Action: foo({"a": {"b": [1, 2, 3]}})'), {
    kind: "ok",
    name: "foo",
    args: { a: { b: [1, 2, 3] } },
  });
});

test("parseAction ignores trailing text after the action call", () => {
  assert.deepEqual(
    parseAction('Action: foo({}) then some trailing text!'),
    { kind: "ok", name: "foo", args: {} },
  );
});

// ── json_error ──────────────────────────────────────────────────────────

test("parseAction returns json_error for balanced-but-invalid JSON", () => {
  // Braces balance, but the body is not valid JSON (unquoted key).
  const res = parseAction("Action: foo({invalid_no_quotes: true})");
  assert.equal(res.kind, "json_error");
  if (res.kind === "json_error") {
    assert.ok(typeof res.error === "string" && res.error.length > 0);
  }
});

// ── depth_mismatch ──────────────────────────────────────────────────────

test("parseAction returns depth_mismatch for unclosed braces", () => {
  const res = parseAction('Action: tool({"unfinished": true');
  assert.equal(res.kind, "depth_mismatch");
  if (res.kind === "depth_mismatch") {
    // snippet is the unfinished tail AFTER the opening `(`.
    assert.equal(res.snippet, '{"unfinished": true');
  }
});

test("parseAction caps the depth_mismatch snippet at 256 chars", () => {
  // 10KB+ unclosed tail: snippet must be capped to keep parseError bounded.
  const longTail = '{"a": 1' + " ".repeat(15_000);
  const res = parseAction("Action: tool(" + longTail);
  assert.equal(res.kind, "depth_mismatch");
  if (res.kind === "depth_mismatch") {
    assert.equal(res.snippet.length, 256);
    assert.ok(res.snippet.startsWith('{"a": 1'));
  }
});
