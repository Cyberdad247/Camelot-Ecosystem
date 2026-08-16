/**
 * CognitiveParser: Extracts and separates cognitive metadata from LLM output.
 * Targeted at the [AttentionFocus] protocol.
 */
export class CognitiveParser {
  static TAG_REGEX = /\[([a-zA-Z]+):\s*([\s\S]*?)\]/g;
  static OUTPUT_MARKER = /\[OUTPUT START\]/i;

  /**
   * Parses the raw LLM response.
   * @param {any} rawInput
   * @returns {object} { tags: { TagName: Content }, content: any }
   */
  static parse(rawInput) {
    const result = {
      tags: {},
      content: rawInput,
    };

    if (rawInput === null || rawInput === undefined) return result;

    // If it's already an object/array, we just return it
    if (typeof rawInput !== 'string') {
      return result;
    }

    const rawText = rawInput;

    // 1. Extract Tags
    const matches = [...rawText.matchAll(this.TAG_REGEX)];

    matches.forEach((m) => {
      const tagName = m[1];
      const content = m[2].trim();
      result.tags[tagName] = content;
    });

    // 2. Identify and isolate core content
    const markerIndex = rawText.search(this.OUTPUT_MARKER);
    if (markerIndex !== -1) {
      // Content starts after marker
      const afterMarker = rawText.substring(markerIndex);
      result.content = afterMarker.replace(this.OUTPUT_MARKER, '').trim();
    } else if (matches.length > 0) {
      let cleanText = rawText;
      matches.forEach((m) => {
        cleanText = cleanText.replace(m[0], '');
      });
      result.content = cleanText.trim();
    }

    return result;
  }

  /**
   * Formats the content for UI display while retaining tags for metadata.
   */
  static getPresentation(parsedData) {
    return parsedData.content;
  }
}
