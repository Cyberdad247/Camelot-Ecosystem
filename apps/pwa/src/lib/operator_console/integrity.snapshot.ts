// SPDX-License-Identifier: MIT

import { canonicalJson } from './integrity';

/**
 * Cheap integrity marker for a task snapshot: recomputes the canonical JSON
 * of the snapshot's evidence arrays and returns a stable digest the UI can
 * compare against a previous render to detect tampering-in-transit.
 */
export function snapshotDigest(payload: unknown): string {
  const text = canonicalJson(payload);
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) | 0;
  }
  return `digest:${hash}`;
}
