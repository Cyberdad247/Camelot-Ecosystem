import { CryptoVault } from '../security/crypto_vault.js';

export class GraphRAG {
  constructor() {
    this.nodes = new Map();
    this.edges = [];
    this.vault = new CryptoVault();
  }

  /**
   * Load graph from encrypted storage
   */
  async load() {
    try {
      const stored = await chrome.storage.local.get('encrypted_graph');
      if (stored.encrypted_graph) {
        const data = await this.vault.decrypt(stored.encrypted_graph);
        this.nodes = new Map(data.nodes.map((n) => [n.id, n]));
        this.edges = data.edges;
        console.log(`[GraphRAG] Loaded ${this.nodes.size} nodes from vault.`);
      }
    } catch (e) {
      console.warn('[GraphRAG] Failed to load graph:', e);
    }
  }

  /**
   * Save graph to encrypted storage
   */
  async save() {
    const data = {
      nodes: Array.from(this.nodes.values()),
      edges: this.edges,
    };

    const encrypted = await this.vault.encrypt(data);
    await chrome.storage.local.set({ encrypted_graph: encrypted });
    console.log(`[GraphRAG] Saved ${this.nodes.size} nodes to vault.`);
  }

  /**
   * Clear all graph data (Memory + Storage)
   */
  async clear() {
    this.nodes.clear();
    this.edges = [];
    await chrome.storage.local.remove('encrypted_graph');
    console.log('[GraphRAG] System Purged.');
  }

  /**
   * Index TOON nodes into the graph
   */
  async indexNodes(nodes) {
    for (const node of nodes) {
      const graphNode = {
        ...node,
        edges: [],
      };

      this.nodes.set(node.id, graphNode);
    }

    await this.autoLinkNodes();
    await this.save(); // Persist changes
  }

  /**
   * Add explicit edge between nodes
   */
  addEdge(from, to, type, metadata = {}) {
    const edge = { from, to, type, metadata };

    const fromNode = this.nodes.get(from);
    if (fromNode) {
      fromNode.edges.push(edge);
    }

    this.edges.push(edge);
  }

  /**
   * Query the graph
   */
  async query(question, options = {}) {
    if (this.nodes.size === 0) await this.load(); // Lazy Load

    const maxResults = options.maxResults || 10;
    const hopDistance = options.hopDistance || 2;

    const startNodes = this.semanticSearch(question, maxResults * 2);

    const expandedNodes = new Set();
    for (const node of startNodes) {
      expandedNodes.add(node);
      const neighbors = this.getNeighbors(node.id, hopDistance);
      neighbors.forEach((n) => expandedNodes.add(n));
    }

    const ranked = Array.from(expandedNodes)
      .map((node) => ({
        node,
        score: this.scoreRelevance(node, question),
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, maxResults);

    return {
      nodes: ranked.map((r) => r.node),
      confidence: ranked[0]?.score || 0,
    };
  }

  // ===== PRIVATE HELPERS =====

  async autoLinkNodes() {
    const nodes = Array.from(this.nodes.values());

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const nodeA = nodes[i];
        const nodeB = nodes[j];

        const sharedEntities = nodeA.entities.filter((e) => nodeB.entities.includes(e));

        if (sharedEntities.length > 0) {
          this.addEdge(nodeA.id, nodeB.id, 'RELATES_TO', {
            sharedEntities,
            strength: sharedEntities.length,
          });
        }
      }
    }
  }

  semanticSearch(query, limit) {
    const queryTokens = query.toLowerCase().split(/\s+/);

    const scored = Array.from(this.nodes.values()).map((node) => {
      const text = (node.summary + ' ' + node.entities.join(' ')).toLowerCase();
      const score = queryTokens.filter((token) => text.includes(token)).length;
      return { node, score };
    });

    return scored
      .filter((s) => s.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map((s) => s.node);
  }

  getNeighbors(nodeId, maxHops) {
    const visited = new Set();
    const result = [];

    const explore = (id, hopsLeft) => {
      if (hopsLeft === 0 || visited.has(id)) return;
      visited.add(id);

      const node = this.nodes.get(id);
      if (!node) return;

      result.push(node);

      for (const edge of node.edges) {
        explore(edge.to, hopsLeft - 1);
      }
    };

    explore(nodeId, maxHops);
    return result.filter((n) => n.id !== nodeId);
  }

  scoreRelevance(node, query) {
    const queryTokens = query.toLowerCase().split(/\s+/);
    const text = (node.summary + ' ' + node.entities.join(' ')).toLowerCase();

    let score = 0;
    for (const token of queryTokens) {
      if (text.includes(token)) {
        score += 1;
      }
    }

    for (const entity of node.entities) {
      if (query.toLowerCase().includes(entity.toLowerCase())) {
        score += 2;
      }
    }

    return score / queryTokens.length;
  }
}
