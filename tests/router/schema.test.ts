import { validateA2ARequest } from '../../src/router/schema';
import { describe, it, expect } from 'vitest';

describe('A2A Schema Validation', () => {
    it('should validate a correct A2A JSON-RPC request', () => {
        const payload = {
            jsonrpc: "2.0",
            method: "execute_task",
            params: {
                source_agent: "Merlin_Î©",
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
                source_agent: "Merlin_Î©",
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
                source_agent: "Merlin_Î©",
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
});
