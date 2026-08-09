// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { z } from "zod";
import {
  UKGDeltaSchema,
} from "./types.js";
import {
  IronGateApprovalRequestSchema,
  IronGateApprovalResponseSchema,
} from "./ironGate.js";

export const ChatRoleSchema = z.enum(["user", "assistant", "system", "knight"]);
export type ChatRole = z.infer<typeof ChatRoleSchema>;

export const ChatMessageSchema = z.object({
  id: z.string(),
  role: ChatRoleSchema,
  text: z.string(),
  createdAt: z.string().datetime(),
  metadata: z.record(z.any()).optional(),
});

export type ChatMessage = z.infer<typeof ChatMessageSchema>;

export const TitanLinkEventSchema = z.discriminatedUnion("kind", [
  z.object({
    kind: z.literal("chat_delta"),
    conversationId: z.string(),
    delta: ChatMessageSchema,
  }),
  z.object({
    kind: z.literal("ukg_delta"),
    delta: UKGDeltaSchema,
  }),
  z.object({
    kind: z.literal("job_update"),
    jobId: z.string(),
    status: z.string(),               // e.g. "running", "completed", "failed"
    progress: z.number().min(0).max(1).optional(),
    summary: z.string().optional(),
  }),
  z.object({
    kind: z.literal("audio_chunk"),
    streamId: z.string(),
    data: z.string(), // Base64 encoded audio
    isFinal: z.boolean(),
  }),
  IronGateApprovalRequestSchema,
]);

export type TitanLinkEvent = z.infer<typeof TitanLinkEventSchema>;

export const RustDeskCommandSchema = z.discriminatedUnion('kind', [
  // 1. Connection Request
  z.object({
    kind: z.literal('rustdesk_connect'),
    deviceId: z.string(),
    authMethod: z.enum(['password', 'key', 'biometric']),
  }),
  // 2. Remote Control Action
  z.object({
    kind: z.literal('remote_control'),
    targetDeviceId: z.string(),
    action: z.enum(['voice_command', 'screen_capture', 'file_transfer', 'session_end']),
    voiceIntent: z.string().optional(),
  }),
  // 3. Screen Intelligence Stream
  z.object({
    kind: z.literal('rustdesk_screen_frame'),
    deviceId: z.string(),
    frameBuffer: z.string(), // Base64 encoded
    quality: z.enum(['low', 'medium', 'high']),
  })
]);

export type RustDeskCommand = z.infer<typeof RustDeskCommandSchema>;

export const TitanLinkCommandSchema = z.discriminatedUnion("kind", [
  z.object({
    kind: z.literal("send_message"),
    conversationId: z.string(),
    message: ChatMessageSchema,
  }),
  z.object({
    kind: z.literal("start_voice_stream"),
    persona: z.string(),
  }),
  z.object({
    kind: z.literal("memorize_intent"),
    text: z.string(),
    metadata: z.record(z.any()).optional(),
  }),
  z.object({
    kind: z.literal("request_approval"),
    actionId: z.string(),
  }),
  IronGateApprovalResponseSchema,
  z.object({
    kind: z.literal('rustdesk_command'),
    command: RustDeskCommandSchema
  })
]);

export type TitanLinkCommand = z.infer<typeof TitanLinkCommandSchema>;