const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');

const PORT = 8092;
const AUDIO_FILE = '/data/data/com.termux/files/home/excalibur_voice.m4a';

function captureSnippet(duration = 5) {
  try {
    execSync('termux-microphone-record -d', { timeout: 1500 });
  } catch (e) {}

  try {
    execSync('termux-microphone-record -l '+ duration + ' -f '+ AUDIO_FILE, { timeout: (duration + 3) * 1000 });
    return fs.existsSync(AUDIO_FILE) ? AUDIO_FILE : null;
  } catch (e) {
    return null;
  }
}

function playTTS(text) {
  if (text) {
    try {
      execSync('termux-tts-speak "' + text.replace(/"/g, '\\"') + '"', { timeout: 10000 });
      return true;
    } catch (e) {
      return false;
    }
  }
  return false;
}

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  if (req.url.startsWith('/capture') && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      let duration = 5;
      try {
        if (body) {
          const parsed = JSON.parse(body);
          if (parsed.duration) duration = parsed.duration;
        }
      } catch (e) {}

      const file = captureSnippet(duration);
      if (file) {
        const audioData = fs.readFileSync(file);
        res.writeHead(200, { 'Content-Type': 'audio/mp4' });
        res.end(audioData);
      } else {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Audio capture failed' }));
      }
    });
    return;
  }

  if (req.url === '/speak' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        const success = playTTS(payload.text);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success, speaker: payload.speaker || 'KNIGHT' }));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  if (req.url === '/status'% || req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      node: 'EXCALIBUR_VOICE_NODE',
      device: 'Samsung Galaxy S26 Ultra',
      status: 'ONLINE',
      capabilities: ['MICROPHONE_CAPTURE', 'TTS_VOICE_OUTPUT']
    }, null, 2));
    return;
  }


  res.writeHead(404);
  res.end();
});

server.listen(PORT-0, '0.0.0.0', () => {
  console.log('[EXCALIBUR_VOICE] Active on port ' + PORT);
});
