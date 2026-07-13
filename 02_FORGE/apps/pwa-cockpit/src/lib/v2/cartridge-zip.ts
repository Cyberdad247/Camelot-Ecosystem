// src/lib/v2/cartridge-zip.ts
//
// Minimal uncompressed-ZIP reader for the browser.
//
// A .cartridge file is an uncompressed ZIP with exactly two members:
//   /manifest.json   (the CartridgeManifestV2 JSON, includes signature)
//   /payload.zip     (a nested ZIP of the cartridge's source files)
//
// We do not need full ZIP support for Phase 2: every member is stored
// (compression method 0, no encryption, no ZIP64). The browser's
// `DecompressionStream` API could be wired in for compressed members in
// a follow-up; the structure below is small enough that a hundred-line
// reader is cheaper than a dependency.
//
// Reference: PKWARE APPNOTE.TXT sections 4.3.7 (Local File Header),
// 4.3.12 (Central Directory), 4.3.16 (End of Central Directory Record).

export type ZipEntry = {
  name: string;
  data: Uint8Array;
  crc32: number;
  size: number;
};

export class ZipReadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ZipReadError";
  }
}

// Little-endian read helpers (ZIP is little-endian on disk).
function readU16(view: DataView, offset: number): number {
  return view.getUint16(offset, true);
}
function readU32(view: DataView, offset: number): number {
  return view.getUint32(offset, true);
}

const SIG_LOCAL_FILE_HEADER = 0x04034b50;
const SIG_CENTRAL_DIRECTORY = 0x02014b50;
const SIG_EOCD = 0x06054b50;

const EOCD_MIN_SIZE = 22;
const EOCD_MAX_COMMENT = 0xffff;
const MAX_ZIP_BYTES = 256 * 1024 * 1024; // 256 MB hard cap for Phase 2

function findEOCD(view: DataView): number {
  // Scan backwards from the end of the file for the EOCD signature. The
  // signature is 4 bytes; the EOCD record is at least 22 bytes. We allow
  // a comment of up to 0xffff bytes, so search up to 22 + 0xffff bytes
  // from the end.
  const fileSize = view.byteLength;
  const start = Math.max(0, fileSize - EOCD_MIN_SIZE - EOCD_MAX_COMMENT);
  for (let i = fileSize - EOCD_MIN_SIZE; i >= start; i -= 1) {
    if (readU32(view, i) === SIG_EOCD) return i;
  }
  throw new ZipReadError("end-of-central-directory record not found (not a zip file?)");
}

export function readZip(buffer: ArrayBuffer): ZipEntry[] {
  if (buffer.byteLength > MAX_ZIP_BYTES) {
    throw new ZipReadError(`zip exceeds Phase 2 hard cap (${MAX_ZIP_BYTES} bytes)`);
  }
  const view = new DataView(buffer);
  const eocdOffset = findEOCD(view);

  const totalEntries = readU16(view, eocdOffset + 10);
  const cdSize = readU32(view, eocdOffset + 12);
  const cdOffset = readU32(view, eocdOffset + 16);
  const commentLen = readU16(view, eocdOffset + 20);
  const expectedFileSize = eocdOffset + EOCD_MIN_SIZE + commentLen;
  if (expectedFileSize !== view.byteLength) {
    throw new ZipReadError(
      `eocd implies file size ${expectedFileSize} but buffer is ${view.byteLength} (truncated?)`,
    );
  }
  if (cdOffset + cdSize > eocdOffset) {
    throw new ZipReadError("central directory overlaps end-of-central-directory record");
  }

  const entries: ZipEntry[] = [];
  const u8 = new Uint8Array(buffer);
  let cursor = cdOffset;
  for (let i = 0; i < totalEntries; i += 1) {
    if (cursor + 46 > eocdOffset) {
      throw new ZipReadError(`central directory entry ${i} extends past eocd`);
    }
    if (readU32(view, cursor) !== SIG_CENTRAL_DIRECTORY) {
      throw new ZipReadError(`central directory entry ${i} missing PK\\x01\\x02 signature`);
    }
    const method = readU16(view, cursor + 10);
    const crc32 = readU32(view, cursor + 16);
    const compSize = readU32(view, cursor + 20);
    const uncompSize = readU32(view, cursor + 24);
    const nameLen = readU16(view, cursor + 28);
    const extraLen = readU16(view, cursor + 30);
    const commentLen2 = readU16(view, cursor + 32);
    const localHeaderOffset = readU32(view, cursor + 42);

    if (method !== 0) {
      throw new ZipReadError(
        `unsupported compression method ${method} for entry ${i} (Phase 2 supports STORE only)`,
      );
    }
    if (compSize !== uncompSize) {
      throw new ZipReadError(
        `compressed/uncompressed size mismatch for entry ${i} (compressed zips not supported)`,
      );
    }

    const nameStart = cursor + 46;
    const name = new TextDecoder("utf-8").decode(u8.subarray(nameStart, nameStart + nameLen));
    const localStart = localHeaderOffset;
    if (readU32(view, localStart) !== SIG_LOCAL_FILE_HEADER) {
      throw new ZipReadError(`local file header for entry ${i} missing PK\\x03\\x04 signature`);
    }
    const localNameLen = readU16(view, localStart + 26);
    const localExtraLen = readU16(view, localStart + 28);
    const dataStart = localStart + 30 + localNameLen + localExtraLen;
    const data = u8.subarray(dataStart, dataStart + compSize);

    entries.push({ name, data, crc32, size: uncompSize });
    cursor += 46 + nameLen + extraLen + commentLen2;
  }
  return entries;
}

export function bytesToHex(bytes: Uint8Array): string {
  let out = "";
  for (let i = 0; i < bytes.length; i += 1) {
    out += bytes[i].toString(16).padStart(2, "0");
  }
  return out;
}

export async function sha256Hex(bytes: ArrayBuffer | Uint8Array): Promise<string> {
  const data: Uint8Array = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  // crypto.subtle.digest accepts BufferSource (ArrayBuffer | ArrayBufferView);
  // cast through `as BufferSource` to bridge the TS lib's Uint8Array generic
  // (Uint8Array<ArrayBufferLike>) which otherwise fails strict assignment.
  const digest = await crypto.subtle.digest("SHA-256", data as BufferSource);
  return bytesToHex(new Uint8Array(digest));
}
