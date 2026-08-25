const http = require('http');
const { execSync } = require('child_process');

const BIFROST_HOST = process.env.BIFROST_HOST || '100.118.224.52';
const BIFROST_PORT = process.env.BIFROST_PORT || 3001;
const LOCAL_PORT = process.env.MOBILE_NODE_PORT || 8090;
const NODE_NAME = process.env.NODE_NAME || 'vashawns-s26-ultra';
const NODE_IP = process.env.NODE_IP || '100.106.246.126';

function runTermuxApi(cmd) {
  try {
    const out = execSync('termux-' + cmd, { timeout: 3000, encoding: 'utf-8' });
    return JSON.parse(out);
  } catch (e) {
    return { error: e.message };
  }
}

function getDeviceInfo() {
  return {
    node_name: NODE_NAME,
    mesh_ip: NODE_IP,
    role: 'KINETIC_MOBILE_SENTINEL',
    bifrost_target: http:// + BIFROST_HOST + ':' + BIFROST_PORT,
    battery: runTermuxApi('battery-status'),
    timestamp: new Date().toISOString()
  };
}

function sendNotification(title, content) {
  try {
    execSync('termux-notification -t "' + title + '" -c "' + content + '" --id camelot_mobile', { timeout: 2000 });
    return true;
  } catch (e) {
    return false;
  }
}

function speakText(text) {
  try {
    execSync('termux-tts-speak "' + text + '"', { timeout: 4000 });
    return true;
  } catch (e) {
    return false;
  }
}

const server = http.createServer((req, res) => {
  const url = req.url;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (url === '/status' || url === '/') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'ONLINE', data: getDeviceInfo() }, null, 2));
    return;
  }

  if (url === '/notify' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        sendNotification(payload.title || 'Camelot-OS', payload.message || 'Notification');
        res.writeHead(200);
        res.end(JSON.stringify({ success: true }));
      } catch (e) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

if (url === '/speak' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body);
        speakText(payload.text || 'Camelot Online');
        res.writeHead(200);
        res.end(JSON.stringify({ success: true }));
      } catch (e) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Endpoint not found' }));
});

server.listen(LOCAL_PORT, '0.0.0.0', () => {
  console.log('[this-mobile-node] Active on 0.0.0.0:' + LOCAL_PORT);
  sendNotification('Camelot Mobile Node', 'Mobile Sentinel Active on Tailscale Mesh');
});
