-- SPDX-License-Identifier: MIT

-- ==============================================================================
-- EXP_LEDGER SCHEMA v1.0
-- Camelot OS - Pure Experience Tracking (NO Ejection/Incentives)
-- ==============================================================================

-- Main EXP Ledger table (created per persona)
CREATE TABLE IF NOT EXISTS exp_ledger (
    exp_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    
    -- Trigger information
    prompt_hash TEXT NOT NULL,
    complication_type TEXT NOT NULL,
    cartridge TEXT NOT NULL,
    rune_phase TEXT,
    context_snapshot TEXT,  -- JSON object (max 5 key-value pairs)
    
    -- Resolution information
    solution_steps TEXT NOT NULL,  -- JSON array of strings
    fix_code_snippet TEXT,
    knight_responsible TEXT NOT NULL,
    validation_signature TEXT NOT NULL,  -- Sir_Zenith approval
    
    -- Outcome
    time_to_resolve_sec REAL,
    success INTEGER NOT NULL DEFAULT 1,  -- SQLite boolean
    
    -- Metadata
    tags TEXT,  -- JSON array of strings
    exp_value INTEGER NOT NULL DEFAULT 10,  -- ALWAYS 10, NO multipliers
    last_reused TEXT,  -- ISO8601 timestamp of last reuse
    
    -- System fields
    created_at TEXT DEFAULT (datetime('now')),
    archived INTEGER NOT NULL DEFAULT 0
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_exp_prompt_hash ON exp_ledger(prompt_hash);
CREATE INDEX IF NOT EXISTS idx_exp_complication_type ON exp_ledger(complication_type);
CREATE INDEX IF NOT EXISTS idx_exp_timestamp ON exp_ledger(timestamp);
CREATE INDEX IF NOT EXISTS idx_exp_tags ON exp_ledger(tags);
CREATE INDEX IF NOT EXISTS idx_exp_knight ON exp_ledger(knight_responsible);
CREATE INDEX IF NOT EXISTS idx_exp_archived ON exp_ledger(archived);

-- ==============================================================================
-- VERIFICATION CONSTRAINTS
-- ==============================================================================
-- NO ejection tables
-- NO incentive tables
-- NO badge/leaderboard tables
-- NO exp_level field
-- NO severity_multiplier field
-- NO efficiency_bonus field
-- exp_value is ALWAYS 10
-- ==============================================================================
