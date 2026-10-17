export interface SwarmMessage {
  id: string;
  sender: string;
  recipient: string;
  intent: string;
  payload: string;
  signature?: string;
  timestamp: number;
}

export interface SanitizedPayload {
  cleanText: string;
  redactedKeys: string[];
}

const piiPatterns = [
  { name: 'API_KEY', regex: /(?:bearer\s+[a-zA-Z0-9_\-\.]{20,}|key-[a-zA-Z0-9]{16,})/gi },
  { name: 'SECRET_TOKEN', regex: /(?:ghp_[a-zA-Z0-9]{36}|xox[baprs]-[a-zA-Z0-9]{10,48})/gi },
  {
    name: 'PRIVATE_KEY',
    regex: /-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+PRIVATE KEY-----/gi,
  },
];

export function sanitizePayload(raw: string): SanitizedPayload {
  let cleanText = raw;
  const redactedKeys: string[] = [];

  for (const pattern of piiPatterns) {
    if (pattern.regex.test(cleanText)) {
      redactedKeys.push(pattern.name);
      cleanText = cleanText.replace(pattern.regex, `[REDACTED_${pattern.name}]`);
    }
  }

  return { cleanText, redactedKeys };
}

export function formatSymbolectEnvelope(msg: SwarmMessage): string {
  const { cleanText } = sanitizePayload(msg.payload);
  // Triple-QFT Symbolect serialization: |Sender⊗(⚡Recipient)⟩ ⟨Intent:Payload⟩
  return `|${msg.sender}⊗(⚡${msg.recipient})⟩ ⟨${msg.intent}:${cleanText}⟩`;
}

export const RufloSwarmHarness = {
  sanitizePayload,
  formatSymbolectEnvelope,
};
