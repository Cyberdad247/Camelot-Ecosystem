const http = require('http');

const data = JSON.stringify({
  model: 'gemma3:1b',
  prompt: 'Ping',
  stream: false
});

const options = {
  hostname: '127.0.0.1',
  port: 11434,
  path: '/api/generate',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

const req = http.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    console.log('STATUS:', res.statusCode);
    try {
        const json = JSON.parse(body);
        console.log('RESPONSE:', json.response);
    } catch(e) { console.log('BODY:', body); }
  });
});

req.on('error', (error) => {
  console.error('ERROR:', error);
});

req.write(data);
req.end();
