// Hermes voice adapter service. Routes: GET /healthz, POST /v1/stt,
// POST /v1/tts. That is the ENTIRE surface — no skills, no leases, no
// tools, no gateway access (ADR-001: Hermes is an adapter only).
//
// Engines (env):
//   HERMES_STT_ENGINE = fixture (default) | command   HERMES_STT_CMD=<binary>
//   HERMES_TTS_ENGINE = fixture (default) | command   HERMES_TTS_CMD=<binary>
//   HERMES_STT_SCRIPT = "utterance one|utterance two" (fixture override)
// External commands are user-configured and never auto-started/downloaded.

import http from 'node:http';
import {
  DEFAULT_STT_SCRIPT,
  commandStt,
  commandTts,
  fixtureTts,
  makeFixtureStt,
} from './engines.mjs';

const PORT = Number(process.env.HERMES_PORT) || 8790;
const STT_ENGINE = process.env.HERMES_STT_ENGINE || 'fixture';
const TTS_ENGINE = process.env.HERMES_TTS_ENGINE || 'fixture';
const STT_CMD = process.env.HERMES_STT_CMD || '';
const TTS_CMD = process.env.HERMES_TTS_CMD || '';
const MAX_BODY = 16 * 1024 * 1024;

const script = process.env.HERMES_STT_SCRIPT
  ? process.env.HERMES_STT_SCRIPT.split('|').map((s) => s.trim()).filter(Boolean)
  : DEFAULT_STT_SCRIPT;
const fixtureStt = makeFixtureStt(script);

function json(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'content-type': 'application/json',
    'access-control-allow-origin': '*',
    'access-control-allow-headers': 'content-type',
    'access-control-allow-methods': 'GET, POST, OPTIONS',
  });
  res.end(payload);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY) {
        reject(new Error('body too large'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'OPTIONS') {
    return json(res, 204, {});
  }
  try {
    if (req.method === 'GET' && req.url === '/healthz') {
      return json(res, 200, {
        status: 'ok',
        service: 'camelot-hermes-voice',
        version: '0.1.0',
        stt: STT_ENGINE,
        tts: TTS_ENGINE,
      });
    }

    if (req.method === 'POST' && req.url === '/v1/stt') {
      const body = JSON.parse((await readBody(req)).toString('utf8'));
      const sampleRate = Number(body.sampleRate) || 16000;
      const raw = Buffer.from(String(body.pcm16 ?? ''), 'base64');
      if (raw.length < 2) return json(res, 400, { error: 'pcm16 payload required' });
      const pcm16 = new Int16Array(raw.buffer, raw.byteOffset, Math.floor(raw.length / 2));
      const result =
        STT_ENGINE === 'command' && STT_CMD
          ? await commandStt(STT_CMD, pcm16, sampleRate)
          : await fixtureStt(pcm16, sampleRate);
      return json(res, 200, result); // pcm16 goes out of scope here — ephemeral
    }

    if (req.method === 'POST' && req.url === '/v1/tts') {
      const body = JSON.parse((await readBody(req)).toString('utf8'));
      const text = String(body.text ?? '').slice(0, 2000);
      if (!text) return json(res, 400, { error: 'text required' });
      const wav = TTS_ENGINE === 'command' && TTS_CMD ? await commandTts(TTS_CMD, text) : fixtureTts(text);
      res.writeHead(200, {
        'content-type': 'audio/wav',
        'content-length': wav.length,
        'access-control-allow-origin': '*',
      });
      return res.end(wav);
    }

    return json(res, 404, { error: 'not found' });
  } catch (err) {
    return json(res, 500, { error: String(err) });
  }
});

server.listen(PORT, () => {
  console.log(
    `camelot-hermes-voice 0.1.0 listening on :${PORT} (stt: ${STT_ENGINE}, tts: ${TTS_ENGINE})`,
  );
});

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => {
    server.close(() => {
      console.log('graceful shutdown complete');
      process.exit(0);
    });
    setTimeout(() => process.exit(0), 3000).unref();
  });
}
