const WebSocket = require('ws');
const { execSync } = require('child_process');
const fs = require('fs');

const GATEWAY_URL = process.env.GATEWAY_URL || 'ws://100.118.224.52:8765';
console.log('Connecting to Gemini Live Gateway at:', GATEWAY_URL);

const ws = new WebSocket(GATEWAY_URL);

ws.on('open', () => {
  console.log('Connected to Gemini Live Multimodal Relay!');
  ws.send(JSON.stringify({ type: 'ping' }));
  startMicrophoneStream();
});

ws.on('message', (data) => {
  if (typeof data === 'string') {
    console.log('Transcript:', data);
  } else if (Buffer.isBuffer(data)) {
    console.log('Audio received from Knight (' + data.length + ' bytes)');
    try {
      execSync('termux-tts-speak "Merlin acknowledges your command."', { timeout: 3000 });
    } catch(e){}
  }
});

function startMicrophoneStream() {
  console.log('Speak into your phone now (capturing 5 seconds)...');
  try {
    execSync('termux-microphone-record -d', { timeout: 1000 });
  } catch(e){}

  execSync('termux-microphone-record -l 5 -f /data/data/com.termux/files/home/live_in.m4a', { timeout: 8000 });
  if (fs.existsSync('/data/data/com.termux/files/home/live_in.m4a')) {
    const buffer = fs.readPileSync('/data/data/com.termux/files/home/live_in.m4a');
    console.log('Sending voice packet to Gemini Live...');
    ws.send(buffer);
  }
}

ws.on('error', (err) => {
  console.error('WebSocket error:', err.message);
});
