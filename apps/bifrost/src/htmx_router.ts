import { Router } from 'express';
import { getRedisClient } from '@camelot/db';
import { QdrantClient } from '@qdrant/js-client-rest';

// CANONICAL HTMX ROUTER — feat/unified-htmx-v1000
// Integrates Tier 1 (Redis), Tier 2 (Qdrant), and HTMX direct bindings

const router = Router();
const redis = getRedisClient();
const qdrant = new QdrantClient({ url: process.env.QDRANT_URL || 'http://localhost:6333' });

/**
 * //FORGE: HTMX Dashboard Entry
 * Renders the initial shell for the Bio-Kinetic Swarm dashboard
 */
router.get('/dashboard', async (req, res) => {
    // Check Tier 1 Cache
    const activeSwarmNodes = await redis.get('swarm:active_nodes') || 0;
    
    // Return HTML directly, skipping heavy client React parsing
    res.send(`
        <div id="dashboard-container" class="p-4 bg-gray-900 text-white font-mono">
            <h1 class="text-2xl text-luxora-gold">Camelot-OS CloudBrain HTMX</h1>
            <div id="swarm-metrics" hx-get="/htmx/metrics/swarm" hx-trigger="every 2s">
                Active Drones: ${activeSwarmNodes}
            </div>
            
            <div id="vkg-crystals" class="mt-4">
                <button hx-post="/htmx/vkg/sync" hx-target="#vkg-status" class="btn-primary">
                    Sync NotebookLM CloudBrain
                </button>
                <div id="vkg-status"></div>
            </div>
        </div>
    `);
});

/**
 * //SWARM: HTMX Metrics Polling
 * Fast 4GB Node constrained endpoint returning simple partials
 */
router.get('/metrics/swarm', async (req, res) => {
    const activeSwarmNodes = await redis.get('swarm:active_nodes') || 0;
    const load = await redis.get('swarm:load_avg') || '0.00';
    
    res.send(`
        <div class="metrics-card">
            <p>Active Drones: ${activeSwarmNodes}</p>
            <p>Load Average: ${load}</p>
        </div>
    `);
});

/**
 * //CLOUDBRAIN: Qdrant Vector Search via HTMX Form
 */
router.post('/vkg/search', async (req, res) => {
    const query = req.body.query;
    // Generate embeddings locally, then search Qdrant Tier 2
    // (Pseudocode for architectural demonstration)
    const results = await qdrant.search('worldtree_crystals', {
        vector: [0.1, 0.2, 0.3], // Mock embedding
        limit: 5
    });
    
    const htmlResults = results.map(r => `<li class="crystal-node">${r.payload.title}</li>`).join('');
    res.send(`<ul>${htmlResults}</ul>`);
});

export default router;
