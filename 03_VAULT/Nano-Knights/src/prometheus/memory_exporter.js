/**
 * MEMORY EXPORTER (OUROBOROS BRIDGE)
 * Serializes internal GraphRAG knowledge into OS-compatible JSON-LD.
 */

export class MemoryExporter {
    
    /**
     * Export the active Knowledge Graph
     * @param {GraphRAG} graph 
     */
    static export(graph) {
        const timestamp = new Date().toISOString();
        
        // 1. Convert Nodes to Standard Schema
        const nodes = Array.from(graph.nodes.values()).map(node => ({
            "@id": node.id,
            "@type": node['@type'] || 'Concept',
            "name": node.metadata?.title || node.id,
            "description": node.summary,
            "url": node.metadata?.url,
            "dateCreated": node.timestamp,
            "mentions": node.entities
        }));

        // 2. Convert Edges
        const edges = graph.edges.map(edge => ({
            "@type": "Relationship",
            "source": edge.from,
            "target": edge.to,
            "relationType": edge.type,
            "weight": edge.metadata?.strength || 1
        }));

        // 3. Construct JSON-LD Bundle
        return {
            "@context": "http://schema.org",
            "@graph": [
                {
                    "@id": "urn:nano:session:" + timestamp,
                    "@type": "ResearchSession",
                    "startTime": timestamp,
                    "agent": "Nano-Knights v3.2",
                    "nodes": nodes,
                    "edges": edges
                }
            ]
        };
    }
}
