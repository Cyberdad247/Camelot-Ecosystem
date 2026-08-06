import { validateA2ARequest } from '../../src/router/schema';
import { describe, it, expect } from 'vitest';

describe('A2A Schema Validation', () => {
    it('should validate a correct A2A JSON-RPC request', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{ \"@context\": \"...\" }",
                mcp_tools_allowed: ["read_file", "write_file"]
            },
            id: "123e4567-e89b-12d3-a456-426614174000"
        };
        expect(validateA2ARequest(payload)).toBe(true);
    });

    it('should reject a payload that is not an object', () => {
        expect(validateA2ARequest("string payload")).toBe(false);
        expect(validateA2ARequest(123)).toBe(false);
        expect(validateA2ARequest(true)).toBe(false);
        expect(validateA2ARequest(undefined)).toBe(false);
    });

    it('should reject a null payload', () => {
        expect(validateA2ARequest(null)).toBe(false);
    });

    it('should reject an empty object', () => {
        expect(validateA2ARequest({})).toBe(false);
    });

    it('should reject a payload with missing jsonrpc field', () => {
        const payload = {
            method: "execute_task",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: []
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload with missing method field', () => {
        const payload = {
            jsonrpc: "2.0",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: []
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload with missing params field', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload with incorrectly typed params field', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: "not an object",
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload with null params field', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: null,
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload with missing id field', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: []
            }
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload where mcp_tools_allowed contains non-strings', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: ["read_file", 123, "write_file"]
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload where mcp_tools_allowed is not an array', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: "read_file, write_file"
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should validate successfully with optional BitRouter, Persona, and Template parameters', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: ["read_file"],
                virtual_key: "brvk_token_abc123",
                spend_cap: 15.0,
                current_spend: 2.5,
                loop_count: 1,
                max_loops: 10,
                persona: "architect",
                template_params: {
                    user: "vizio",
                    env: "production"
                }
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(true);
    });

    it('should reject a payload with an invalid virtual key', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: ["read_file"],
                virtual_key: "invalid_prefix_abc123"
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload where spend_cap or current_spend are not numbers', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: ["read_file"],
                spend_cap: "ten dollars"
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should validate successfully with optional intent_text parameter', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: ["read_file"],
                intent_text: "scaffold a rapid prototype"
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(true);
    });

    it('should reject a payload with incorrectly typed intent_text parameter', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin_Ω",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: ["read_file"],
                intent_text: 12345
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload with missing or invalid source_agent', () => {
        const basePayload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: []
            },
            id: "123"
        };
        expect(validateA2ARequest(basePayload)).toBe(false);
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, source_agent: 123 } })).toBe(false);
    });

    it('should reject a payload with missing or invalid target_engine', () => {
        const basePayload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                context_payload: "{}",
                mcp_tools_allowed: []
            },
            id: "123"
        };
        expect(validateA2ARequest(basePayload)).toBe(false);
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, target_engine: 123 } })).toBe(false);
    });

    it('should reject a payload with missing or invalid context_payload', () => {
        const basePayload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                target_engine: "Goose",
                mcp_tools_allowed: []
            },
            id: "123"
        };
        expect(validateA2ARequest(basePayload)).toBe(false);
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, context_payload: 123 } })).toBe(false);
    });

    it('should reject a payload with incorrectly typed optional numeric parameters', () => {
        const basePayload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: []
            },
            id: "123"
        };
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, current_spend: "5.0" } })).toBe(false);
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, loop_count: "1" } })).toBe(false);
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, max_loops: "10" } })).toBe(false);
    });

    it('should reject a payload with incorrectly typed optional persona', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: [],
                persona: 123
            },
            id: "123"
        };
        expect(validateA2ARequest(payload)).toBe(false);
    });

    it('should reject a payload with incorrectly typed template_params', () => {
        const basePayload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin",
                target_engine: "Goose",
                context_payload: "{}",
                mcp_tools_allowed: []
            },
            id: "123"
        };
        // Not an object
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, template_params: "not an object" } })).toBe(false);
        // Null
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, template_params: null } })).toBe(false);
        // Object with non-string values
        expect(validateA2ARequest({ ...basePayload, params: { ...basePayload.params, template_params: { user: "vizio", count: 5 } } })).toBe(false);
    });
});
