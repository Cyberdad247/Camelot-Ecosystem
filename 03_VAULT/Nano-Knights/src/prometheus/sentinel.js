/**
 * Sentinel: Context Compression Engine
 * JS Port for Nano-Knights
 */

export class Sentinel {
  /**
   * Compress TOON nodes
   */
  static async compress(nodes, options = {}) {
    const targetTokens = options.target_tokens || 8000;
    const anchorStrategy = options.anchor_strategy || 'importance';
    const preserveEntities = options.preserve_entities ?? true;

    const originalTokens = this.estimateTokens(nodes);

    if (originalTokens <= targetTokens) {
      return {
        original_tokens: originalTokens,
        compressed_tokens: originalTokens,
        compression_ratio: 1.0,
        nodes,
        summary: 'No compression needed'
      };
    }

    const anchors = this.selectAnchors(nodes, anchorStrategy);

    const compressed = [];
    let currentTokens = 0;
    const anchorTokens = this.estimateTokens(anchors);

    compressed.push(...anchors);
    currentTokens += anchorTokens;

    const remaining = nodes.filter(n => !anchors.find(a => a.id === n.id));

    for (const node of remaining) {
      if (currentTokens >= targetTokens) break;

      const compNode = this.compressNode(node, preserveEntities);
      const nodeTokens = this.estimateTokens([compNode]);

      if (currentTokens + nodeTokens <= targetTokens) {
        compressed.push(compNode);
        currentTokens += nodeTokens;
      }
    }

    const summary = `Compressed ${nodes.length} nodes to ${compressed.length}.`;

    return {
      original_tokens: originalTokens,
      compressed_tokens: currentTokens,
      compression_ratio: originalTokens / currentTokens,
      nodes: compressed,
      summary
    };
  }

  static estimateTokens(nodes) {
    let chars = 0;
    for (const node of nodes) {
      chars += node.summary.length;
      chars += node.entities.join(', ').length;
    }
    return Math.ceil(chars * 0.75);
  }

  static selectAnchors(nodes, strategy) {
    const anchorCount = Math.max(3, Math.ceil(nodes.length * 0.2));

    if (strategy === 'recency') {
        return nodes
          .filter(n => n.timestamp)
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .slice(0, anchorCount);
    } else {
        // Default importance
        return nodes
          .map(n => ({
            node: n,
            score: this.calculateImportance(n)
          }))
          .sort((a, b) => b.score - a.score)
          .slice(0, anchorCount)
          .map(x => x.node);
    }
  }

  static calculateImportance(node) {
    let score = node.summary.length / 100;
    score += node.entities.length * 2;
    if (node['@type'].startsWith('CODE_')) score += 5;
    return score;
  }

  static compressNode(node, preserveEntities) {
    const compressedSummary = node.summary.split('.').slice(0, 2).join('.') + '...';
    return {
      ...node,
      summary: compressedSummary,
      entities: preserveEntities ? node.entities : node.entities.slice(0, 5)
    };
  }
}
