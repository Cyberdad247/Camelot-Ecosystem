import { Router, Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { NodeRecord } from '../types';

export const registryRouter = Router();

// Ed25519/X-Camelot-Lease-ID middleware scaffold
const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const leaseId = req.headers['x-camelot-lease-id'];
  // In production, validate this Ed25519 signature
  if (!leaseId && process.env.NODE_ENV === 'production') {
    res.status(401).json({ error: 'Unauthorized: Missing X-Camelot-Lease-ID' });
    return;
  }
  next();
};

// In-memory registry, initialized with VPS Hub #001 seed
let nodes: Map<string, NodeRecord> = new Map([
  ['vps-hub-cybertronia', {
    id: 'vps-hub-cybertronia',
    name: 'VPS Hub #001',
    status: 'ACTIVE',
    ip: '10.0.0.1',
    load: 12.4,
    lastSeen: Date.now(),
    coordinates: { x: 0, y: 0 }
  }],
  ['edge-rust-dsp', {
    id: 'edge-rust-dsp',
    name: 'Audio DSP Node',
    status: 'online',
    ip: '10.0.0.2',
    load: 4.2,
    lastSeen: Date.now()
  }],
  ['auth-go-gateway', {
    id: 'auth-go-gateway',
    name: 'Camelot Registry',
    status: 'syncing',
    ip: '10.0.0.3',
    load: 85.1,
    lastSeen: Date.now() - 60000
  }]
]);

const nodeSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.enum(['online', 'offline', 'syncing', 'isolated', 'ACTIVE']),
  ip: z.string(),
  load: z.number().min(0).max(100),
  coordinates: z.object({ x: z.number(), y: z.number() }).optional()
});

registryRouter.use(authMiddleware);

registryRouter.get('/', (req, res) => {
  res.json(Array.from(nodes.values()));
});

registryRouter.post('/', (req, res) => {
  try {
    const payload = nodeSchema.parse(req.body);
    const newNode: NodeRecord = {
      ...payload,
      lastSeen: Date.now()
    };
    nodes.set(newNode.id, newNode);
    res.status(201).json(newNode);
  } catch (error) {
    res.status(400).json({ error: 'Invalid node payload', details: error });
  }
});

registryRouter.put('/:id', (req, res) => {
  try {
    const { id } = req.params;
    if (!nodes.has(id)) {
      res.status(404).json({ error: 'Node not found' });
      return;
    }
    
    // Partial update validation
    const partialSchema = nodeSchema.partial().omit({ id: true });
    const payload = partialSchema.parse(req.body);
    
    const existing = nodes.get(id)!;
    const updated = {
      ...existing,
      ...payload,
      lastSeen: Date.now()
    };
    
    nodes.set(id, updated);
    res.json(updated);
  } catch (error) {
    res.status(400).json({ error: 'Invalid update payload', details: error });
  }
});

registryRouter.post('/:id/action', (req, res) => {
  const { id } = req.params;
  const { action } = req.body; // e.g., 'reboot', 'isolate'
  
  if (!nodes.has(id)) {
    res.status(404).json({ error: 'Node not found' });
    return;
  }
  
  const node = nodes.get(id)!;
  if (action === 'isolate') {
    node.status = 'isolated';
  } else if (action === 'reboot') {
    node.status = 'offline';
  }
  node.lastSeen = Date.now();
  
  nodes.set(id, node);
  res.json({ success: true, node });
});
