// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
/**
 * RustDesk TitanLink Protocol Extensions
 * =======================================
 * 
 * Extends the TitanLink protocol with RustDesk-specific commands and events
 * for remote desktop control via the Anya Mobile Bridge.
 * 
 * Author: Sir Bridge (The Integrator)
 * Version: 1.0.0
 * Created: 2026-01-29
 */

import { z } from 'zod';

// =============================================================================
// ENUMS & CONSTANTS
// =============================================================================

export const AuthMethodSchema = z.enum(['password', 'key', 'biometric']);
export type AuthMethod = z.infer<typeof AuthMethodSchema>;

export const SessionStatusSchema = z.enum([
    'pending',
    'connecting',
    'connected',
    'disconnected',
    'error',
    'denied'
]);
export type SessionStatus = z.infer<typeof SessionStatusSchema>;

export const RemoteActionSchema = z.enum([
    'voice_command',
    'screen_capture',
    'file_transfer',
    'session_start',
    'session_end',
    'swarm_execute'
]);
export type RemoteAction = z.infer<typeof RemoteActionSchema>;

export const ScreenQualitySchema = z.enum(['low', 'medium', 'high']);
export type ScreenQuality = z.infer<typeof ScreenQualitySchema>;

// =============================================================================
// DEVICE TOPOLOGY (UKG Integration)
// =============================================================================

export const RemoteDeviceSchema = z.object({
    id: z.string(),                    // RustDesk peer ID
    label: z.string(),                 // Human-readable name
    os: z.string().optional(),         // Operating system
    lastSeen: z.string().datetime().optional(),
    trustLevel: z.enum(['LOW', 'MEDIUM', 'HIGH']).default('MEDIUM'),
    capabilities: z.array(z.string()).default(['terminal', 'gui', 'file_transfer']),
    tailscaleIp: z.string().optional(),
    isOnline: z.boolean().default(false),
});

export type RemoteDevice = z.infer<typeof RemoteDeviceSchema>;

export const DeviceTopologySchema = z.object({
    devices: z.array(RemoteDeviceSchema),
    edges: z.array(z.object({
        from: z.string(),
        to: z.string(),
        rel: z.string(),  // e.g., "mesh_peer", "relay_via"
    })).optional(),
    lastUpdated: z.string().datetime(),
});

export type DeviceTopology = z.infer<typeof DeviceTopologySchema>;

// =============================================================================
// SESSION MANAGEMENT
// =============================================================================

export const RemoteSessionSchema = z.object({
    sessionId: z.string().uuid(),
    deviceId: z.string(),
    status: SessionStatusSchema,
    startedAt: z.string().datetime(),
    authMethod: AuthMethodSchema,
    approvalId: z.string().optional(),
    endedAt: z.string().datetime().optional(),
    commandsExecuted: z.number().default(0),
});

export type RemoteSession = z.infer<typeof RemoteSessionSchema>;

// =============================================================================
// TITANLINK COMMANDS (Mobile → Kernel)
// =============================================================================

/**
 * Request to start a RustDesk session
 */
export const RustDeskConnectCommandSchema = z.object({
    kind: z.literal('rustdesk_connect'),
    deviceId: z.string(),
    authMethod: AuthMethodSchema.default('biometric'),
    requireApproval: z.boolean().default(true),
});

/**
 * Remote control action (voice command, screen capture, etc.)
 */
export const RemoteControlCommandSchema = z.object({
    kind: z.literal('remote_control'),
    sessionId: z.string().uuid(),
    action: RemoteActionSchema,
    voiceIntent: z.string().optional(),     // Natural language command
    shellCommand: z.string().optional(),    // Direct shell command
    filePath: z.string().optional(),        // For file transfers
    quality: ScreenQualitySchema.optional(), // For screen capture
});

/**
 * End a RustDesk session
 */
export const RustDeskDisconnectCommandSchema = z.object({
    kind: z.literal('rustdesk_disconnect'),
    sessionId: z.string().uuid(),
});

/**
 * Swarm remote control - execute on multiple devices
 */
export const SwarmRemoteCommandSchema = z.object({
    kind: z.literal('swarm_remote'),
    deviceIds: z.array(z.string()),
    command: z.string(),
    requireSwarmApproval: z.boolean().default(true),
});

/**
 * Request device topology from UKG
 */
export const DeviceTopologyRequestSchema = z.object({
    kind: z.literal('device_topology_request'),
    includeOffline: z.boolean().default(true),
});

/**
 * Register a new device
 */
export const RegisterDeviceCommandSchema = z.object({
    kind: z.literal('register_device'),
    device: RemoteDeviceSchema,
});

/**
 * File transfer command
 */
export const FileTransferCommandSchema = z.object({
    kind: z.literal('rustdesk_file_transfer'),
    sessionId: z.string().uuid(),
    localPath: z.string(),
    remotePath: z.string(),
    direction: z.enum(['upload', 'download']),
});

// Combined RustDesk Commands Schema
export const RustDeskCommandSchema = z.discriminatedUnion('kind', [
    RustDeskConnectCommandSchema,
    RemoteControlCommandSchema,
    RustDeskDisconnectCommandSchema,
    SwarmRemoteCommandSchema,
    DeviceTopologyRequestSchema,
    RegisterDeviceCommandSchema,
    FileTransferCommandSchema,
]);

export type RustDeskCommand = z.infer<typeof RustDeskCommandSchema>;

// =============================================================================
// TITANLINK EVENTS (Kernel → Mobile)
// =============================================================================

/**
 * Session status update
 */
export const RustDeskSessionEventSchema = z.object({
    kind: z.literal('rustdesk_session'),
    sessionId: z.string().uuid(),
    deviceId: z.string(),
    status: SessionStatusSchema,
    startedAt: z.string().datetime().optional(),
    endedAt: z.string().datetime().optional(),
    error: z.string().optional(),
});

/**
 * Command execution result
 */
export const RemoteCommandResultSchema = z.object({
    kind: z.literal('remote_command_result'),
    sessionId: z.string().uuid(),
    status: z.enum(['executed', 'denied', 'error']),
    command: z.string().optional(),
    voiceIntent: z.string().optional(),
    translatedCommand: z.string().optional(),
    output: z.string().optional(),
    executedAt: z.string().datetime(),
    error: z.string().optional(),
});

/**
 * Screen capture result
 */
export const ScreenCaptureEventSchema = z.object({
    kind: z.literal('screen_capture'),
    sessionId: z.string().uuid(),
    deviceId: z.string(),
    quality: ScreenQualitySchema,
    imageData: z.string().optional(),  // Base64 encoded
    dimensions: z.object({
        width: z.number(),
        height: z.number(),
    }),
    timestamp: z.string().datetime(),
});

/**
 * Device topology update
 */
export const DeviceTopologyEventSchema = z.object({
    kind: z.literal('device_topology'),
    topology: DeviceTopologySchema,
});

/**
 * Swarm execution result
 */
export const SwarmResultEventSchema = z.object({
    kind: z.literal('swarm_result'),
    command: z.string(),
    totalDevices: z.number(),
    successful: z.number(),
    failed: z.number(),
    results: z.array(z.object({
        deviceId: z.string(),
        status: z.string(),
        error: z.string().optional(),
    })),
    completedAt: z.string().datetime(),
});

/**
 * File transfer result
 */
export const FileTransferResultSchema = z.object({
    kind: z.literal('file_transfer_result'),
    sessionId: z.string().uuid(),
    status: z.enum(['transferred', 'denied', 'error']),
    direction: z.enum(['upload', 'download']),
    localPath: z.string(),
    remotePath: z.string(),
    timestamp: z.string().datetime(),
    error: z.string().optional(),
});

// Combined RustDesk Events Schema
export const RustDeskEventSchema = z.discriminatedUnion('kind', [
    RustDeskSessionEventSchema,
    RemoteCommandResultSchema,
    ScreenCaptureEventSchema,
    DeviceTopologyEventSchema,
    SwarmResultEventSchema,
    FileTransferResultSchema,
]);

export type RustDeskEvent = z.infer<typeof RustDeskEventSchema>;

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Create a RustDesk connect command
 */
export function createConnectCommand(
    deviceId: string,
    authMethod: AuthMethod = 'biometric'
): z.infer<typeof RustDeskConnectCommandSchema> {
    return {
        kind: 'rustdesk_connect',
        deviceId,
        authMethod,
        requireApproval: true,
    };
}

/**
 * Create a voice command
 */
export function createVoiceCommand(
    sessionId: string,
    voiceIntent: string
): z.infer<typeof RemoteControlCommandSchema> {
    return {
        kind: 'remote_control',
        sessionId,
        action: 'voice_command',
        voiceIntent,
    };
}

/**
 * Create a swarm execute command
 */
export function createSwarmCommand(
    deviceIds: string[],
    command: string
): z.infer<typeof SwarmRemoteCommandSchema> {
    return {
        kind: 'swarm_remote',
        deviceIds,
        command,
        requireSwarmApproval: true,
    };
}

/**
 * Create a screen capture command
 */
export function createScreenCaptureCommand(
    sessionId: string,
    quality: ScreenQuality = 'medium'
): z.infer<typeof RemoteControlCommandSchema> {
    return {
        kind: 'remote_control',
        sessionId,
        action: 'screen_capture',
        quality,
    };
}