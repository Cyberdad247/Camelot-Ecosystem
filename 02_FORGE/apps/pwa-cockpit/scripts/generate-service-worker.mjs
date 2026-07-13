import { createHash } from "node:crypto";
import { readdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = fileURLToPath(new URL("..", import.meta.url));
const sourceRoot = path.join(root, "src");
const templatePath = path.join(root, "scripts", "sw.template.js");
const outputPath = path.join(root, "public", "sw.js");
const publicInputs = ["manifest.json", "offline.html", "icon.svg", "anya.png"];

async function filesUnder(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map((entry) => {
      const target = path.join(directory, entry.name);
      return entry.isDirectory() ? filesUnder(target) : [target];
    }),
  );
  return nested.flat();
}

const hash = createHash("sha256");
const inputs = [
  ...(await filesUnder(sourceRoot)),
  ...publicInputs.map((name) => path.join(root, "public", name)),
  path.join(root, "package-lock.json"),
].sort();

for (const input of inputs) {
  hash.update(path.relative(root, input).replaceAll("\\", "/"));
  hash.update(await readFile(input));
}

const version = `anya-cockpit-${hash.digest("hex").slice(0, 12)}`;
const template = await readFile(templatePath, "utf8");
await writeFile(outputPath, template.replace("__CACHE_VERSION__", version), "utf8");
console.log(`Generated service worker cache version: ${version}`);
