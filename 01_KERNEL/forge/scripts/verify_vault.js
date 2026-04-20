const http = require('http');

const options = {
  hostname: 'localhost',
  port: 8001,
  path: '/system/health',
  method: 'GET'
};

const req = http.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    console.log('STATUS:', res.statusCode);
    console.log('BODY:', body);
  });
});

req.on('error', (error) => {
  console.error('ERROR:', error);
});

req.end();
