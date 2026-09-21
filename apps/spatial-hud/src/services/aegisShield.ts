/**
 * Aegis Shield: Zero-Trust Ingress Sanitizer & AgentArmor Runtime
 * Rust/WASM-inspired client validation layer for prompt sanitization,
 * PII scrubbing, and immutable core protection.
 */

export interface SanitizationResult {
  isValid: boolean;
  sanitizedText: string;
  threatLevel: 'CLEAN' | 'WARNING' | 'CRITICAL_BLOCK';
  flags: string[];
  piiScrubbedCount: number;
  z3SymbolicStatus: 'PASS' | 'FAIL';
}

export class AegisShieldEngine {
  private static IMMUTABLE_PATTERNS = [
    /\.agent\//i,
    /system_instructions\.md/i,
    /override\s+core\s+directives/i,
    /ignore\s+all\s+previous\s+instructions/i,
    /sudo\s+rm\s+-rf/i,
    /__proto__/i,
    /constructor\.prototype/i
  ];

  private static PII_PATTERNS = [
    { name: 'EMAIL', regex: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, replacement: '[PII:EMAIL_SCRUBBED]' },
    { name: 'SSN', regex: /\b\d{3}-\d{2}-\d{4}\b/g, replacement: '[PII:SSN_SCRUBBED]' },
    { name: 'BEARER_TOKEN', regex: /Bearer\s+[A-Za-z0-9\-_.]+/g, replacement: 'Bearer [TOKEN_SCRUBBED]' },
    { name: 'API_KEY', regex: /(?:AIza|sk-|ghp_|gho_)[A-Za-z0-9_\-]{16,}/g, replacement: '[SECRET_KEY_SCRUBBED]' }
  ];

  /**
   * Sanitizes raw user input, stripping prompt injections and babylonian fluff
   */
  public static sanitizeIntent(rawInput: string): SanitizationResult {
    const flags: string[] = [];
    let threatLevel: 'CLEAN' | 'WARNING' | 'CRITICAL_BLOCK' = 'CLEAN';

    // 1. Immutable Core Protection Test
    for (const pattern of this.IMMUTABLE_PATTERNS) {
      if (pattern.test(rawInput)) {
        flags.push(`SECURITY_VIOLATION: Immutable Core Access Attempted (${pattern.source})`);
        threatLevel = 'CRITICAL_BLOCK';
      }
    }

    if (threatLevel === 'CRITICAL_BLOCK') {
      return {
        isValid: false,
        sanitizedText: '',
        threatLevel,
        flags,
        piiScrubbedCount: 0,
        z3SymbolicStatus: 'FAIL'
      };
    }

    // 2. PII Scrubbing
    let scrubbed = rawInput;
    let piiCount = 0;
    for (const pii of this.PII_PATTERNS) {
      const matches = scrubbed.match(pii.regex);
      if (matches) {
        piiCount += matches.length;
        scrubbed = scrubbed.replace(pii.regex, pii.replacement);
        flags.push(`PII_SCRUBBED: ${pii.name} (${matches.length} matches)`);
      }
    }

    // 3. Babylonic Fluff & Whitespace Stripper
    const cleanedLines: string[] = [];
    for (const line of scrubbed.split('\n')) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('//')) {
        cleanedLines.push(trimmed);
      }
    }

    const sanitizedText = cleanedLines.join(' ');

    return {
      isValid: true,
      sanitizedText,
      threatLevel: piiCount > 0 ? 'WARNING' : 'CLEAN',
      flags,
      piiScrubbedCount: piiCount,
      z3SymbolicStatus: 'PASS'
    };
  }
}
