import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import { registryRouter } from './src/server/registry';
import { telemetryRouter } from './src/server/telemetry';
import { authRouter } from './src/server/auth';

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Security headers compatible with AI Studio iframe preview
  app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    next();
  });

  // API Routes
  app.use('/api/auth', authRouter);
  app.use('/api/v1', authRouter);
  app.use('/api/nodes', registryRouter);
  app.use('/api/telemetry', telemetryRouter);
  
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', time: new Date().toISOString() });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    // Production static serving
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Camelot-OS Control Plane running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
