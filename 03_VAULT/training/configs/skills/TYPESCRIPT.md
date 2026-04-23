# Skill: TypeScript (SIR_SYNTAX)
# Loaded dynamically when agent touches .ts/.tsx files

## Titanium Type-Safety
- NEVER use `any` type. Use `unknown` + type guards.
- All state uses Discriminated Unions: `IDLE | MINING | ANCHORED | ERROR`
- Defensive error parsing: `result.error.issues?.[0]?.message ?? "Error"`
- Zod schemas for ALL external data boundaries

## Stack
- Next.js 16 (App Router), React 19, Tailwind CSS v4
- Framer Motion for spring physics animations
- Monospace + Sans fonts, Celestial Void theme

## Patterns
- Server Components by default; 'use client' only when needed
- Direct Client-to-Modal fetches (bypass Vercel 10s timeout)
- Streaming responses for long-running operations
