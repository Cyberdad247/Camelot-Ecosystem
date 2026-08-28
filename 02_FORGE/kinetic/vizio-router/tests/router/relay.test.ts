// tests/router/relay.test.ts
import { describe, it, expect } from 'vitest';
import { Channel, ChannelPool, HealthProbeEngine, ChannelRelay, ChannelStatus } from '../../src/router/relay';

describe('Channel Multi-Key Rotation', () => {
    it('should rotate keys round-robin across invocations', () => {
        const channel = new Channel({
            id: 'ch_test_keys',
            name: 'Test Multi-Key Node',
            type: 'openai',
            keys: ['key-a', 'key-b', 'key-c'],
            models: ['gpt-4o']
        });

        const keys: string[] = [];
        for (let i = 0; i < 6; i++) {
            keys.push(channel.getNextKey());
        }

        expect(keys).toEqual(['key-a', 'key-b', 'key-c', 'key-a', 'key-b', 'key-c']);
    });
});

describe('Channel Pooling & Priority Selection', () => {
    it('should pick from highest priority bucket and respect weights', () => {
        const pool = new ChannelPool();

        pool.registerChannel({
            id: 'ch_p10_heavy',
            name: 'Priority 10 Heavy',
            type: 'openai',
            keys: ['k1'],
            models: ['gpt-4o'],
            group: 'default',
            priority: 10,
            weight: 90
        });

        pool.registerChannel({
            id: 'ch_p10_light',
            name: 'Priority 10 Light',
            type: 'openai',
            keys: ['k2'],
            models: ['gpt-4o'],
            group: 'default',
            priority: 10,
            weight: 10
        });

        pool.registerChannel({
            id: 'ch_p5_fallback',
            name: 'Priority 5 Fallback',
            type: 'openai',
            keys: ['k3'],
            models: ['gpt-4o'],
            group: 'default',
            priority: 5,
            weight: 100
        });

        // Retry 0: must pick Priority 10
        const counts: Record<string, number> = { ch_p10_heavy: 0, ch_p10_light: 0, ch_p5_fallback: 0 };
        for (let i = 0; i < 500; i++) {
            const ch = pool.selectChannel('default', 'gpt-4o', 0);
            expect(ch).not.toBeNull();
            counts[ch!.id]++;
        }

        expect(counts.ch_p5_fallback).toBe(0);
        expect(counts.ch_p10_heavy).toBeGreaterThan(counts.ch_p10_light);

        // Retry 1: must fallback to Priority 5
        const fallback = pool.selectChannel('default', 'gpt-4o', 1);
        expect(fallback?.id).toBe('ch_p5_fallback');
    });
});

describe('Health Probe & Auto-Ban', () => {
    it('should identify auto-ban conditions for 401, 429, 503, and quota errors', () => {
        const pool = new ChannelPool();
        const probe = new HealthProbeEngine(pool);

        expect(probe.shouldDisableChannel(401)).toBe(true);
        expect(probe.shouldDisableChannel(429)).toBe(true);
        expect(probe.shouldDisableChannel(503)).toBe(true);
        expect(probe.shouldDisableChannel(200)).toBe(false);
        expect(probe.shouldDisableChannel(400)).toBe(false);
        expect(probe.shouldDisableChannel(undefined, new Error('insufficient_quota for organization'))).toBe(true);
    });

    it('should auto-enable an auto-disabled channel when requested', () => {
        const pool = new ChannelPool();
        const probe = new HealthProbeEngine(pool);

        const ch = pool.registerChannel({
            id: 'ch_recov',
            name: 'Auto-Recover Node',
            type: 'gemini',
            keys: ['k1'],
            models: ['gemini-2.0-flash'],
            autoEnable: true,
            status: ChannelStatus.AUTO_DISABLED
        });

        expect(ch.isAvailable()).toBe(false);
        probe.autoEnable(ch);
        expect(ch.isAvailable()).toBe(true);
        expect(ch.status).toBe(ChannelStatus.ENABLED);
    });
});

describe('Zero-Cost Failover Integration', () => {
    it('should seamlessly failover across zero-cost channels when primary fails', async () => {
        const pool = new ChannelPool();
        const probe = new HealthProbeEngine(pool);
        const relay = new ChannelRelay(pool, probe);

        // Primary zero-cost channel: Local Ollama (Priority 10)
        const chLocal = pool.registerChannel({
            id: 'ch_ollama_local',
            name: 'Local Ollama Node',
            type: 'ollama',
            keys: ['ollama-local-key'],
            group: 'zero_cost',
            models: ['llama3', 'gpt-4o'],
            priority: 10,
            weight: 100,
            costTier: 'zero_cost',
            costPerToken: 0,
            autoBan: true
        });

        // Secondary zero-cost channel: Gemini Free Tier (Priority 8)
        const chGeminiFree = pool.registerChannel({
            id: 'ch_gemini_free',
            name: 'Gemini Free Tier',
            type: 'gemini',
            keys: ['gemini-free-key'],
            group: 'zero_cost',
            models: ['llama3', 'gpt-4o'],
            priority: 8,
            weight: 100,
            costTier: 'zero_cost',
            costPerToken: 0,
            autoBan: true
        });

        // Commercial paid channel (Priority 1)
        pool.registerChannel({
            id: 'ch_openai_paid',
            name: 'OpenAI Commercial',
            type: 'openai',
            keys: ['sk-paid-key'],
            group: 'default',
            models: ['llama3', 'gpt-4o'],
            priority: 1,
            weight: 100,
            costTier: 'paid',
            costPerToken: 0.00002
        });

        // Simulate executor: Ollama fails with 503 (Out of VRAM/Service Unavailable), Gemini Free Tier succeeds
        const executor = async (channel: Channel, _key: string) => {
            if (channel.id === 'ch_ollama_local') {
                return {
                    statusCode: 503,
                    error: new Error('Local Ollama GPU out of memory: 503 Service Unavailable'),
                    payload: null
                };
            }
            if (channel.id === 'ch_gemini_free') {
                return {
                    statusCode: 200,
                    payload: { text: 'Synthesized via Gemini Free Tier' }
                };
            }
            return {
                statusCode: 400,
                error: new Error('Unexpected channel'),
                payload: null
            };
        };

        const result = await relay.executeRelay(
            {
                group: 'zero_cost',
                model: 'gpt-4o',
                zeroCostOnly: true,
                maxRetries: 3
            },
            executor
        );

        expect(result.success).toBe(true);
        expect(result.channelId).toBe('ch_gemini_free');
        expect(result.zeroCost).toBe(true);
        expect(result.retriesUsed).toBe(1);
        expect(result.failoverTrail.length).toBe(2);
        expect(result.payload).toEqual({ text: 'Synthesized via Gemini Free Tier' });

        // Verify primary Ollama channel was auto-banned
        expect(chLocal.status).toBe(ChannelStatus.AUTO_DISABLED);

        // Verify next request directly hits Gemini Free Tier without retry overhead
        const result2 = await relay.executeRelay(
            {
                group: 'zero_cost',
                model: 'gpt-4o',
                zeroCostOnly: true,
                maxRetries: 3
            },
            executor
        );

        expect(result2.success).toBe(true);
        expect(result2.channelId).toBe('ch_gemini_free');
        expect(result2.retriesUsed).toBe(0);
    });
});
