import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = resolve(appRoot, "../../packages/voice-first-runtime/worklets/voice-capture.worklet.js");
const target = resolve(appRoot, "public/voice-capture.worklet.js");

await mkdir(dirname(target), { recursive: true });
await copyFile(source, target);
console.log("Synchronized Voice-First Cartridge AudioWorklet.");
