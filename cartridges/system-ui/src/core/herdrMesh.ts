export class HerdrMeshRouter {
  private nodes: Map<string, string> = new Map();
  private edges: Set<string> = new Set();

  public registerNode(id: string, type: string) {
    this.nodes.set(id, type);
  }

  public connectNodes(source: string, target: string) {
    this.edges.add(`${source}->${target}`);
  }

  public isConnected(source: string, target: string): boolean {
    return this.edges.has(`${source}->${target}`) || this.edges.has(`${target}->${source}`);
  }

  public getNodes() {
    return Array.from(this.nodes.entries()).map(([id, type]) => ({ id, type }));
  }
}
