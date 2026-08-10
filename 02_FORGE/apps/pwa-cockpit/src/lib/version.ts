// src/lib/version.ts
//
// Single source of truth for the build VERSION string. Both /api/health
// (nodejs runtime) and /api/health/edge (edge runtime) import this so
// their `version` field can never drift. Bump VERSION on each shipped
// phase so operators can correlate the two endpoints and so any client
// that pins against the version can detect upgrades.
//
// Edge-runtime compatible: pure constant, no Node primitives, no
// React imports, no side effects.

export const VERSION = "1.0.0-phase8";
