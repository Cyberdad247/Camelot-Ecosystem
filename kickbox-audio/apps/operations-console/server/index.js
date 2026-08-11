// [THE CONVERGENCE (MASTER ENTRY)]
// Unified Node.js Cluster for Bifrost Backend

import { WebRTC_SFU } from './webrtc_sfu.js';
import { CognitiveRouter } from './cognitive_router.js';
import { AvatarGenerator } from './avatar_generator.js';

class BifrostCluster {
  constructor() {
    this.transport = new WebRTC_SFU(4433);
    this.cognition = new CognitiveRouter();
    this.resonance = new AvatarGenerator();
  }

  async boot() {
    console.log('[MASTER_CLUSTER] Booting the Bio-Kinetic Swarm...');
    
    // Initialize in parallel
    await Promise.all([
      this.transport.initialize(),
      this.cognition.initialize(),
      this.resonance.initialize()
    ]);

    console.log('[MASTER_CLUSTER] All threads running. Establishing internal pipeline.');

    // Wire the threads together
    this.transport.onAudioBufferReceived = async (pcmBuffer) => {
      // 1. Send audio to Cognition (Thread B)
      const cognitiveResponse = await this.cognition.processAudio(pcmBuffer);
      
      // 2. Send cognitive response to Resonance (Thread C)
      const videoFrames = await this.resonance.generateAvatarResponse(cognitiveResponse);
      
      // 3. Pipe video frames back to Transport (Thread A)
      videoFrames.forEach(frame => {
        this.transport.transmitVideoFrame(frame);
      });
    };

    console.log('[MASTER_CLUSTER] Unified Pipeline Established. Factory Independent.');
  }
}

// Start the Cluster
const cluster = new BifrostCluster();
cluster.boot();
