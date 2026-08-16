// SPDX-License-Identifier: MIT

export class ResourceSquire {
  static DEBUG = true;

  /**
   * Judges the best environment for a task based on complexity and config.
   * @param {string} prompt - The task prompt.
   * @param {string} complexity - 'LOW' | 'HIGH' override.
   * @param {object} config - The full LLM config object.
   * @returns {object} { environment: 'LOCAL'|'CLOUD', reason: string }
   */
  static judge(prompt, complexity, config) {
    const result = {
      environment: 'LOCAL',
      reason: 'Default to Edge',
    };

    // 1. Permission Check (Hard Gate)
    if (!config.allowCloudOffload) {
      result.environment = 'LOCAL';
      result.reason = 'Cloud Offloading Disabled by User';
      return result;
    }

    // 2. 8GB Constraint Check
    // If Low Memory Mode is ON, we are more aggressive about offloading HIGH complexity
    if (config.lowMemoryMode && complexity === 'HIGH') {
      result.environment = 'CLOUD';
      result.reason = '8GB Constraint + High Complexity';
      return result;
    }

    // 3. Heuristic Analysis (Keywords)
    const lowerPrompt = prompt.toLowerCase();
    const heavyKeywords = [
      'fine-tune',
      'train',
      'gradient',
      'comprehensive analysis',
      'deep dive',
      'audit entire',
      'reasoning chain',
      'step-by-step proof',
    ];

    if (heavyKeywords.some((kw) => lowerPrompt.includes(kw))) {
      result.environment = 'CLOUD';
      result.reason = 'Heavy Keyword Detected';
      return result;
    }

    // 4. Token Estimation (Rough)
    // If prompt is huge (~1000+ words), local model might choke on 2048 ctx
    if (prompt.length > 5000) {
      // Approx 1000-1200 tokens
      if (config.lowMemoryMode) {
        result.environment = 'CLOUD';
        result.reason = 'Context Length Exceeds Safety Margin';
        return result;
      }
    }

    if (this.DEBUG) console.log(`[SQUIRE] Judgement: ${result.environment} (${result.reason})`);
    return result;
  }
}
