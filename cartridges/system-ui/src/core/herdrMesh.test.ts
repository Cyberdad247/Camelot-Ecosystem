import { describe, expect, it } from 'vitest';
import { HerdrMeshRouter } from './herdrMesh';

describe('HerdrMeshRouter', () => {
  it('should track active nodes and link connections', () => {
    const mesh = new HerdrMeshRouter();
    mesh.registerNode('s26', 'EDGE');
    mesh.registerNode('nC', 'ROUTER');
    mesh.connectNodes('s26', 'nC');

    expect(mesh.isConnected('s26', 'nC')).toBe(true);
    expect(mesh.isConnected('s26', 'nonexistent')).toBe(false);
  });

  it('should list all registered nodes with types', () => {
    const mesh = new HerdrMeshRouter();
    mesh.registerNode('s26', 'EDGE');
    mesh.registerNode('nC', 'ROUTER');

    const nodes = mesh.getNodes();
    expect(nodes).toHaveLength(2);
    expect(nodes[0]).toEqual({ id: 's26', type: 'EDGE' });
  });
});
