import express from 'express';
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import { HeliosHarness } from './ai/HeliosHarness';
import { swarmMatrix } from './swarm/MicrocubicSwarm';

const app = express();
app.use(express.static('public'));
const server = createServer(app);
const wss = new WebSocketServer({ server });

let state = {
  vault: { balance: 1400000000 },
  properties: [],
  swarm: { active: false, tasks: 0, completed: 0 }
};

const broadcast = (data: any) => {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(data));
    }
  });
};

wss.on('connection', (ws) => {
  console.log('[WebSocket] Client connected');
  ws.send(JSON.stringify({ type: 'STATE_UPDATE', payload: state }));

  ws.on('message', async (messageBuffer) => {
    try {
      const data = JSON.parse(messageBuffer.toString());
      
      if (data.type === 'VOICE_COMMAND') {
        const textCommand = data.payload;
        
        ws.send(JSON.stringify({ type: 'VOICE_FEEDBACK', payload: { text: "Ingesting command into Helios Core..." } }));

        const lakishaResponse = await HeliosHarness.askLakisha(textCommand, state);
        
        if (lakishaResponse.mutations) {
          lakishaResponse.mutations.forEach((mutation: any) => {
            console.log("[State Mutation]:", mutation);
            // Apply logic here
          });
        }

        if (lakishaResponse.swarm_tasks && lakishaResponse.swarm_tasks.length > 0) {
          const tasksToSpawn = lakishaResponse.swarm_tasks.map((task: any, index: number) => ({
            id: `cube-${Date.now()}-${index}`,
            type: task.type,
            payload: task.payload
          }));
          
          state.swarm.active = true;
          state.swarm.tasks = tasksToSpawn.length;
          state.swarm.completed = 0;
          
          swarmMatrix.unleash(tasksToSpawn);
          ws.send(JSON.stringify({ type: 'VOICE_FEEDBACK', payload: { text: `${lakishaResponse.feedback} Spawning ${tasksToSpawn.length} Microcubes.` } }));
        } else {
          ws.send(JSON.stringify({ type: 'VOICE_FEEDBACK', payload: { text: lakishaResponse.feedback } }));
        }

        broadcast({ type: 'STATE_UPDATE', payload: state });
      }
    } catch (err) {
      console.error('[WebSocket] Error:', err);
    }
  });
});

swarmMatrix.on('cube_collapsed', (data) => {
  state.swarm.completed++;
  if (state.swarm.completed === state.swarm.tasks) {
    state.swarm.active = false;
  }
  broadcast({ type: 'STATE_UPDATE', payload: state });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`[Bifrost Bridge] Running on port ${PORT}`);
});
