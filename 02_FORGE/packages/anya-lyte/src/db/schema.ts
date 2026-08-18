// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';

/**
 * Anya Lyte: Local-First UKG Cache (SQLite)
 */

export const nodes = sqliteTable('nodes', {
  id: text('id').primaryKey(), // UKG Node ID (e.g. uuid)
  type: text('type'), // JSON-LD @type
  raw: text('raw').notNull(), // Full JSON-LD content
  lastUpdated: integer('last_updated', { mode: 'timestamp' }),
});

export const syncCheckpoints = sqliteTable('sync_checkpoints', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  checkpointHash: text('checkpoint_hash').notNull(),
  timestamp: integer('timestamp', { mode: 'timestamp' }),
});

export const pendingMutations = sqliteTable('pending_mutations', {
  id: text('id').primaryKey(), // UUID
  action: text('action').notNull(), // 'CREATE', 'UPDATE', 'DELETE'
  payload: text('payload').notNull(),
  status: text('status').default('PENDING'), // 'PENDING', 'SYNCING', 'FAILED'
  createdAt: integer('created_at', { mode: 'timestamp' }),
});

/**
 * Agency Factory Schema (Phase 10)
 */

export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  email: text('email').notNull().unique(),
  role: text('role').default('CLIENT'), // 'SOVEREIGN' | 'CLIENT'
  createdAt: integer('created_at', { mode: 'timestamp' }),
});

export const agencyDeliverables = sqliteTable('agency_deliverables', {
  id: text('id').primaryKey(),
  userId: text('user_id').references(() => users.id), // FK Constraint
  type: text('type').notNull(), // 'AUDIT' | 'CONTENT'
  status: text('status').default('PENDING'),
  path: text('path'), // Path to artifact (e.g. 02_FORGE/agency_factory/deliverables/...)
  createdAt: integer('created_at', { mode: 'timestamp' }),
});
