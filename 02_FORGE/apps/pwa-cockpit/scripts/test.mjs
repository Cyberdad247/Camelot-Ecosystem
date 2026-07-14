// scripts/test.mjs
//
// Shared test runner for pwa-cockpit.
//
//   tests/**/*.test.ts   → tsx + node:test
//   tests/**/*.test.tsx  → vitest (only when vitest is installed AND
//                            at least one .test.tsx file exists)
//
// One-shot entry point: `npm test`            runs both kinds.
// Selective tsx-only:    `npm run test:node`  (or pass --node-only).
//
// Why a Node script and not a pure `&&` chain in package.json:
//   - shell glob expansion (`tests/**/*.test.ts`) doesn't work on
//     Windows cmd.exe; we walk the tree ourselves.
//   - the "skip vitest silently when absent" branch is awkward to
//     express without a script — it'd push us into bash-specific
//     conditionals or npx's noisy "command not found" output.
//   - aggregating exit codes from both runners (so a partial failure
//     still returns 1) is cleaner here.
//
// Exit code: 0 only if every runner returned 0. We always run BOTH
// even if the first failed, so devs see the full picture before
// fixing.

import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, "..");
const testsDir = path.join(rootDir, "tests");

const isNodeOnly = process.argv.includes("--node-only");

// Recursive walk that splits .test.ts and .test.tsx into two buckets.
// Skips dotted entries (.git, .agent-browser, …) so hidden dirs and
// node_modules never enter the discovered list.
function discover(dir) {
  const tsTests = [];
  const tsxTests = [];
  if (!fs.existsSync(dir)) return { tsTests, tsxTests };

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".")) continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const sub = discover(fullPath);
      tsTests.push(...sub.tsTests);
      tsxTests.push(...sub.tsxTests);
    } else if (entry.isFile()) {
      if (entry.name.endsWith(".test.ts")) tsTests.push(fullPath);
      else if (entry.name.endsWith(".test.tsx")) tsxTests.push(fullPath);
    }
  }
  return { tsTests, tsxTests };
}

const { tsTests, tsxTests } = discover(testsDir);

// Normalize to forward-slash relative paths so child invocations
// (vitest on Windows especially) see POSIX-style args.
const rel = (abs) => path.relative(rootDir, abs).replace(/\\/g, "/");

let exitCode = 0;

// ---------- tsx + node:test for .test.ts ----------
if (tsTests.length === 0) {
  console.log("\n> [test] no `tests/**/*.test.ts` files found — skipping tsx");
} else {
  console.log(`\n> [test] tsx (node:test) → ${tsTests.length} file(s):`);
  for (const f of tsTests) console.log(`    - ${rel(f)}`);

  const args = ["--import", "tsx", "--test", ...tsTests.map(rel)];
  const res = spawnSync(process.execPath, args, {
    cwd: rootDir,
    stdio: "inherit",
  });
  if (res.status !== 0) exitCode = res.status ?? 1;
  if (res.error) {
    // surfaces spawn-level failures (e.g. node binary gone, EACCES)
    console.error(`> [test] tsx spawn failed: ${res.error.message}`);
  }
}

// ---------- vitest for .test.tsx ----------
if (!isNodeOnly) {
  if (tsxTests.length === 0) {
    console.log(
      "\n> [test] no `tests/**/*.test.tsx` files found — skipping vitest",
    );
  } else {
    const vitestPkg = path.join(rootDir, "node_modules", "vitest", "package.json");
    if (!fs.existsSync(vitestPkg)) {
      console.log(
        `\n> [test] found ${tsxTests.length} .test.tsx file(s), but 'vitest' is not installed — skipping vitest`,
      );
      console.log(
        "> [test] hint: pnpm add -D vitest jsdom @vitejs/plugin-react @testing-library/react",
      );
    } else {
      console.log(`\n> [test] vitest → ${tsxTests.length} file(s):`);
      for (const f of tsxTests) console.log(`    - ${rel(f)}`);

      // npx on Windows is a `.cmd` shim; calling it directly via
      // spawnSync needs the extension resolved by the OS. Spawn it
      // through `shell: true` so Windows picks npx.cmd naturally and
      // POSIX uses the bare `npx`. (No shell injection risk — args are
      // relative paths we just built.)
      const npxCmd = process.platform === "win32" ? "npx.cmd" : "npx";
      const args = ["vitest", "run", ...tsxTests.map(rel)];
      const res = spawnSync(npxCmd, args, {
        cwd: rootDir,
        stdio: "inherit",
        shell: process.platform === "win32",
      });
      if (res.status !== 0) exitCode = res.status ?? 1;
      if (res.error) {
        console.error(`> [test] vitest spawn failed: ${res.error.message}`);
      }
    }
  }
}

if (exitCode === 0) {
  console.log("\n> [test] all suites passed");
} else {
  console.error(`\n> [test] one or more suites failed (exit ${exitCode})`);
}
process.exit(exitCode);
