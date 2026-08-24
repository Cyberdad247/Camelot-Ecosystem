// SPDX-License-Identifier: MIT

export class ChunkManager {
    static DEBUG = true;

    /**
     * Splits text into overlapping chunks, preserving header.
     * @param {string} text - The full TOON text.
     * @param {number} size - Target chunk size (chars). Default 6000 (~1500 tokens).
     * @param {number} overlap - Overlap size (chars). Default 500 (~120 tokens).
     * @returns {string[]} Array of chunked text strings.
     */
    static chunk(text, size = 6000, overlap = 500) {
        // 1. Extract Header (TOON format starts with #@)
        // We assume valid TOON input has a header line or block.
        // Simple heuristic: Take first 2 lines as header if they start with #
        const lines = text.split('\n');
        let header = "";
        let bodyStartIndex = 0;

        for (let i = 0; i < Math.min(lines.length, 5); i++) {
            if (lines[i].trim().startsWith('#') || lines[i].trim().startsWith('[')) {
                header += lines[i] + "\n";
                bodyStartIndex = i + 1;
            } else {
                break;
            }
        }

        const body = lines.slice(bodyStartIndex).join('\n');

        if (body.length <= size) {
            return [text]; // No chunking needed
        }

        const chunks = [];
        let index = 0;

        while (index < body.length) {
            let end = index + size;

            // Adjust end to avoid splitting lines
            if (end < body.length) {
                const nextNewLine = body.indexOf('\n', end);
                if (nextNewLine !== -1 && nextNewLine - end < 200) {
                    end = nextNewLine; // Extend to end of line
                }
            }

            const chunkBody = body.substring(index, end);
            chunks.push((header + "\n[...CHUNK...]\n" + chunkBody).trim());

            // Break if we reached the end
            if (end >= body.length) break;

            // Move index forward by size - overlap
            index += (size - overlap);
        }

        if (this.DEBUG) console.log(`[CHUNK_MANAGER] Split ${text.length} chars into ${chunks.length} chunks.`);
        return chunks;
    }

    /**
     * Merges array of JSON results, deduplicating via _source.
     * @param {Array<object>} results - Array of JSON objects/arrays returned by LLM.
     * @param {object} schema - The expected schema (used to determine if root is array or object).
     * @returns {object|Array} Merged result.
     */
    static merge(results, schema) {
        // Normalize: Results should be arrays of items usually, or object with a key being an array.
        // Assumption: 'extract' usually returns an Array of objects from the prompt instruction.
        // OR an object { "items": [...] }.

        let allItems = [];

        results.forEach(res => {
            if (Array.isArray(res)) {
                allItems.push(...res);
            } else if (typeof res === 'object' && res !== null) {
                // Heuristic: Find the first array property
                const keys = Object.keys(res);
                const arrayKey = keys.find(k => Array.isArray(res[k]));
                if (arrayKey) {
                    allItems.push(...res[arrayKey]);
                } else {
                    // Treat strict object as single item
                    allItems.push(res);
                }
            }
        });

        // Deduplication Logic
        const unique = new Map();

        allItems.forEach(item => {
            if (!item) return;

            // Key: _source is the Gold Standard.
            // Fallback: SHA of content? No, just keep all if no source.

            if (item._source) {
                const existing = unique.get(item._source);
                if (!existing) {
                    unique.set(item._source, item);
                } else {
                    // Merge strategy: Keep the one with more keys?
                    // Or longer string values?
                    // Simple: Keep existing unless new one has non-null fields that existing lacks.
                    const merged = { ...existing };
                    Object.keys(item).forEach(k => {
                        if ((merged[k] === null || merged[k] === undefined) && item[k]) {
                            merged[k] = item[k];
                        }
                    });
                    unique.set(item._source, merged);
                }
            } else {
                // No source? We can't safely dedup. Add as new with random key or just index.
                // Or try to dedup by JSON stringify?
                const json = JSON.stringify(item);
                if (!unique.has(json)) unique.set(json, item);
            }
        });

        const mergedItems = Array.from(unique.values());

        // Return in likely format
        if (schema.type === 'array' || Array.isArray(schema)) {
            return mergedItems;
        } else {
            // If schema expects object wrapping (e.g. { employees: [] })
            // We'll guess the key or wrap in "extracted_data"
            // Or look at first result structure.
            const firstRes = results.find(r => typeof r === 'object' && !Array.isArray(r));
            if (firstRes) {
                // Use key from first result
                const key = Object.keys(firstRes).find(k => Array.isArray(firstRes[k]));
                if (key) return { [key]: mergedItems };
            }
            return mergedItems; // Default to array
        }
    }
}
