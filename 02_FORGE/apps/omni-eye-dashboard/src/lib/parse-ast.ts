import { z } from 'zod';

// --- SCHEMA (Zod v4) ---

export const ASTSchema = z.object({
  id:    z.uuid(),
  pid:   z.uuid().nullable(),
  tag:   z.string().min(1),
  props: z.record(z.string(), z.unknown()),
});

export type ASTNode = z.infer<typeof ASTSchema>;

// --- JSON EXTRACTION ---
// Model output may wrap JSON in markdown fences or include preamble prose.

const JSON_FENCE_RE  = /```(?:json)?\s*([\s\S]*?)```/;
const FIRST_BRACE_RE = /(\{[\s\S]*\})/;

export function extractJson(raw: string): unknown {
  const fenced = JSON_FENCE_RE.exec(raw);
  const source = fenced ? fenced[1] : (FIRST_BRACE_RE.exec(raw)?.[1] ?? raw);
  return JSON.parse(source.trim());
}

export class ParseError extends Error {
  constructor(
    public readonly stage: 'json' | 'schema',
    public readonly detail: string,
    cause?: unknown,
  ) {
    super(`[PARSE:${stage.toUpperCase()}] ${detail}`);
    this.cause = cause;
  }
}

export function parseASTNode(raw: string): ASTNode {
  let parsed: unknown;
  try {
    parsed = extractJson(raw);
  } catch (e) {
    throw new ParseError('json', `Cannot extract JSON from inference output: ${String(e)}`, e);
  }

  const result = ASTSchema.safeParse(parsed);
  if (!result.success) {
    const issues = result.error.issues
      .map(i => `${i.path.join('.')}: ${i.message}`)
      .join('; ');
    throw new ParseError('schema', issues, result.error);
  }

  return result.data;
}

// --- THEMING ---

function linearize(c: number): number {
  const s = c / 255;
  return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
}

function relativeLuminance(hex: string): number {
  const h = hex.replace('#', '');
  const [r, g, b] = [0, 2, 4].map(o => linearize(parseInt(h.slice(o, o + 2), 16)));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrastRatio(hexA: string, hexB: string): number {
  const [la, lb] = [relativeLuminance(hexA), relativeLuminance(hexB)].sort((a, b) => b - a);
  return (la + 0.05) / (lb + 0.05);
}

function wcagForeground(bg: string, threshold = 7.0): string {
  return contrastRatio('#FFFFFF', bg) >= threshold ? '#FFFFFF' : '#000000';
}

function blend(hex: string, target: '#FFFFFF' | '#000000', amount: number): string {
  const h = hex.replace('#', '');
  const t = target === '#FFFFFF' ? 255 : 0;
  const result = [0, 2, 4].map(o => {
    const channel = parseInt(h.slice(o, o + 2), 16);
    return Math.round(channel + (t - channel) * amount)
      .toString(16).padStart(2, '0');
  });
  return `#${result.join('')}`;
}

export interface ThemeTokens {
  bg:            string;
  fg:            string;
  surface:       string;
  surfaceFg:     string;
  border:        string;
  focusRing:     string;
  contrastRatio: number;
}

export function deriveTheme(bgHex: string): ThemeTokens {
  const fg      = wcagForeground(bgHex);
  const isDark  = fg === '#FFFFFF';
  const surface = blend(bgHex, isDark ? '#FFFFFF' : '#000000', 0.08);

  return {
    bg:            bgHex,
    fg,
    surface,
    surfaceFg:     wcagForeground(surface),
    border:        blend(bgHex, isDark ? '#FFFFFF' : '#000000', 0.2),
    focusRing:     isDark ? '#60A5FA' : '#1D4ED8',
    contrastRatio: contrastRatio(fg, bgHex),
  };
}

export function parseAndTheme(raw: string, bgHex: string): ASTNode {
  const node  = parseASTNode(raw);
  const theme = deriveTheme(bgHex);
  return { ...node, props: { ...node.props, theme } };
}
