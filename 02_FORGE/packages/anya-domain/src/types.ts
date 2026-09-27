// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { z } from 'zod';

/** UKG node + edge **/

export const UKGNodeSchema = z.object({
  id: z.string(),
  type: z.string(), // e.g. "Agent", "Gateway", "Device", "Memory"
  label: z.string(),
  props: z.record(z.any()),
  createdAt: z.string().datetime().optional(),
  updatedAt: z.string().datetime().optional(),
});

export type UKGNode = z.infer<typeof UKGNodeSchema>;

export const UKGEdgeSchema = z.object({
  id: z.string(),
  from: z.string(),
  to: z.string(),
  rel: z.string(), // e.g. "uses_as_gateway", "peer_node"
  props: z.record(z.any()).optional(),
});

export type UKGEdge = z.infer<typeof UKGEdgeSchema>;

/** UKG delta for sync **/

export const UKGDeltaSchema = z.object({
  seq: z.number(),
  timestamp: z.string().datetime(),
  nodesUpserted: z.array(UKGNodeSchema),
  nodesDeleted: z.array(z.string()),
  edgesUpserted: z.array(UKGEdgeSchema),
  edgesDeleted: z.array(z.string()),
});

export type UKGDelta = z.infer<typeof UKGDeltaSchema>;
