// SPDX-License-Identifier: MIT

/**
 * MESH MANAGER (Phase 48: P2P Swarm Cluster)
 * Enables WebRTC-based communication between Knights for decentralized intelligence.
 */

export class MeshManager {
  constructor() {
    this.peers = {}; // peerId -> RTCPeerConnection
    this.dataChannels = {}; // peerId -> RTCDataChannel
    this.myId = this._generateId();
    console.log(`[MESH] My PeerID: ${this.myId}`);
  }

  _generateId() {
    return 'knight_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Broadcasts a "Whisper" to all connected peers in the mesh.
   * Whispers are high-velocity, low-latency tips (e.g. resolved selectors).
   */
  whisper(type, data) {
    const payload = JSON.stringify({
      from: this.myId,
      type: type,
      data: data,
      timestamp: Date.now(),
    });

    console.log(`[MESH] Whispering ${type} to Cluster...`);

    Object.values(this.dataChannels).forEach((channel) => {
      if (channel.readyState === 'open') {
        channel.send(payload);
      }
    });
  }

  /**
   * Handles an incoming whisper from a fellow Knight.
   */
  onWhisper(payload) {
    const msg = JSON.parse(payload);
    console.log(`[MESH] Received Whisper from ${msg.from}:`, msg.type);

    // Logic for specific whisper types
    switch (msg.type) {
      case 'RESOLVED_SELECTOR':
        // Cache locally to save future recon cycles
        console.log(`[MESH] Learning selector for ${msg.data.target}: ${msg.data.selector}`);
        break;
      case 'MISSION_TIP':
        console.log(`[MESH] Swarm intelligence boost: ${msg.data.tip}`);
        break;
    }
  }

  // --- WEBRTC SIGNALING HANDLERS ---
  // Phase 57: Cross-Device Signaling (Expansion)
  // Note: Signaling uses TitanLink as the 'Rendezvous Point'.

  async processSignal(signalEnvelope) {
    const { from, type, deviceType, data } = signalEnvelope;
    console.log(`[MESH] Processing Signal from ${from} (${deviceType || 'UNKNOWN'})`);

    if (type === 'OFFER') {
      return await this.handleOffer(from, data);
    } else if (type === 'ANSWER') {
      await this.handleAnswer(from, data);
    } else if (type === 'ICE') {
      await this.handleCandidate(from, data);
    }
  }

  async handleCandidate(peerId, candidate) {
    const pc = this.peers[peerId];
    if (pc) {
      await pc.addIceCandidate(new RTCIceCandidate(candidate));
    }
  }

  async createOffer(peerId) {
    const pc = this._createPeerConnection(peerId);
    const channel = pc.createDataChannel('swarm_whisper');
    this._setupDataChannel(peerId, channel);

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    return offer;
  }

  async handleOffer(peerId, offer) {
    const pc = this._createPeerConnection(peerId);
    pc.ondatachannel = (event) => {
      this._setupDataChannel(peerId, event.channel);
    };

    await pc.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    return answer;
  }

  async handleAnswer(peerId, answer) {
    const pc = this.peers[peerId];
    if (pc) {
      await pc.setRemoteDescription(new RTCSessionDescription(answer));
    }
  }

  _createPeerConnection(peerId) {
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
    });

    pc.onicecandidate = (event) => {
      if (event.candidate) {
        // Signal ICE candidate to peer via TitanLink
      }
    };

    this.peers[peerId] = pc;
    return pc;
  }

  _setupDataChannel(peerId, channel) {
    channel.onmessage = (event) => this.onWhisper(event.data);
    channel.onopen = () => console.log(`[MESH] DataChannel to ${peerId} OPEN.`);
    this.dataChannels[peerId] = channel;
  }
}
