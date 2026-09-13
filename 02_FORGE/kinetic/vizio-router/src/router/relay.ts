// src/router/relay.ts
// Channel Relay & Load Balancing Adapter for vizio-router
// Assimilated from new-api channel pooling, health probe, and zero-cost failover algorithms.

export enum ChannelStatus {
    ENABLED = 1,
    MANUALLY_DISABLED = 2,
    AUTO_DISABLED = 3
}

export type CostTier = "zero_cost" | "free" | "paid" | "premium";

export interface ChannelConfig {
    id: string;
    name: string;
    type: string; // "openai" | "claude" | "gemini" | "ollama" | "custom"
    baseUrl?: string;
    keys: string[];
    group?: string; // "default" | "vip" | "zero_cost" | "local"
    models: string[];
    priority?: number; // Higher priority attempted first
    weight?: number;   // Load balancing weight within same priority bucket
    status?: ChannelStatus;
    costTier?: CostTier;
    costPerToken?: number;
    autoBan?: boolean;
    autoEnable?: boolean;
    latencyMs?: number;
    healthScore?: number;
}

export class Channel {
    public id: string;
    public name: string;
    public type: string;
    public baseUrl?: string;
    public keys: string[];
    public keyIndex: number = 0;
    public group: string;
    public models: string[];
    public priority: number;
    public weight: number;
    public status: ChannelStatus;
    public costTier: CostTier;
    public costPerToken: number;
    public autoBan: boolean;
    public autoEnable: boolean;
    public latencyMs: number = 0;
    public healthScore: number = 1.0;
    public consecutiveFailures: number = 0;
    public consecutiveSuccesses: number = 0;
    public totalRequests: number = 0;
    public totalSuccesses: number = 0;
    public totalFailures: number = 0;
    public lastFailureReason?: string;

    constructor(config: ChannelConfig) {
        this.id = config.id;
        this.name = config.name;
        this.type = config.type;
        this.baseUrl = config.baseUrl;
        this.keys = [...config.keys];
        this.group = config.group || "default";
        this.models = [...config.models];
        this.priority = config.priority !== undefined ? config.priority : 10;
        this.weight = config.weight !== undefined ? config.weight : 100;
        this.status = config.status !== undefined ? config.status : ChannelStatus.ENABLED;
        this.costTier = config.costTier || "paid";
        this.costPerToken = config.costPerToken !== undefined ? config.costPerToken : 0.00002;
        this.autoBan = config.autoBan !== undefined ? config.autoBan : true;
        this.autoEnable = config.autoEnable !== undefined ? config.autoEnable : false;
        this.latencyMs = config.latencyMs || 0;
        this.healthScore = config.healthScore !== undefined ? config.healthScore : 1.0;
    }

    public getNextKey(): string {
        if (!this.keys || this.keys.length === 0) return "";
        if (this.keys.length === 1) return this.keys[0];
        const key = this.keys[this.keyIndex % this.keys.length];
        this.keyIndex = (this.keyIndex + 1) % Number.MAX_SAFE_INTEGER;
        return key;
    }

    public isAvailable(): boolean {
        return this.status === ChannelStatus.ENABLED;
    }

    public isZeroCost(): boolean {
        return (
            this.costTier === "zero_cost" ||
            this.costTier === "free" ||
            this.costPerToken === 0 ||
            this.group.toLowerCase().includes("zero_cost") ||
            this.group.toLowerCase().includes("local")
        );
    }

    public recordSuccess(latencyMs: number): void {
        this.totalRequests++;
        this.totalSuccesses++;
        this.consecutiveSuccesses++;
        this.consecutiveFailures = 0;
        this.latencyMs = latencyMs;
        this.healthScore = 0.85 * this.healthScore + 0.15 * 1.0;
    }

    public recordFailure(reason: string): boolean {
        this.totalRequests++;
        this.totalFailures++;
        this.consecutiveFailures++;
        this.consecutiveSuccesses = 0;
        this.lastFailureReason = reason;
        this.healthScore = 0.85 * this.healthScore;

        if (this.autoBan) {
            this.status = ChannelStatus.AUTO_DISABLED;
            return true;
        }
        return false;
    }
}

export class ChannelPool {
    private channels: Map<string, Channel> = new Map();
    private groupModels: Map<string, Map<string, string[]>> = new Map();

    public registerChannel(channelOrConfig: Channel | ChannelConfig): Channel {
        const channel = channelOrConfig instanceof Channel ? channelOrConfig : new Channel(channelOrConfig);
        this.channels.set(channel.id, channel);
        this.rebuildIndex();
        return channel;
    }

    public removeChannel(id: string): void {
        this.channels.delete(id);
        this.rebuildIndex();
    }

    public updateChannelStatus(id: string, status: ChannelStatus): void {
        const ch = this.channels.get(id);
        if (ch) {
            ch.status = status;
            this.rebuildIndex();
        }
    }

    public getChannel(id: string): Channel | undefined {
        return this.channels.get(id);
    }

    public getAllChannels(): Channel[] {
        return Array.from(this.channels.values());
    }

    private rebuildIndex(): void {
        const newIndex = new Map<string, Map<string, string[]>>();

        for (const [id, ch] of this.channels.entries()) {
            if (ch.status !== ChannelStatus.ENABLED) continue;

            const groups = ch.group.split(",").map(g => g.trim()).filter(Boolean);
            if (groups.length === 0) groups.push("default");

            for (const g of groups) {
                if (!newIndex.has(g)) {
                    newIndex.set(g, new Map<string, string[]>());
                }
                const modelMap = newIndex.get(g)!;
                for (const m of ch.models) {
                    const model = m.trim();
                    if (!model) continue;
                    if (!modelMap.has(model)) {
                        modelMap.set(model, []);
                    }
                    modelMap.get(model)!.push(id);
                }
            }
        }
        this.groupModels = newIndex;
    }

    public selectChannel(group: string, model: string, retry: number = 0, _requestPath?: string): Channel | null {
        if (this.channels.size === 0) return null;

        const candidateIDs: string[] = [];

        // 1. Direct group & model match
        const modelMap = this.groupModels.get(group);
        if (modelMap) {
            if (modelMap.has(model)) {
                candidateIDs.push(...modelMap.get(model)!);
            }
            if (modelMap.has("*")) {
                candidateIDs.push(...modelMap.get("*")!);
            }
        }

        // 2. Default or auto group fallback
        if (candidateIDs.length === 0 && group !== "default" && group !== "auto") {
            const defMap = this.groupModels.get("default");
            if (defMap && defMap.has(model)) {
                candidateIDs.push(...defMap.get(model)!);
            }
        }

        if (candidateIDs.length === 0 && group === "auto") {
            for (const map of this.groupModels.values()) {
                if (map.has(model)) {
                    candidateIDs.push(...map.get(model)!);
                }
            }
        }

        // Deduplicate
        const uniqueIDs = Array.from(new Set(candidateIDs));
        const candidates = uniqueIDs
            .map(id => this.channels.get(id))
            .filter((ch): ch is Channel => ch !== undefined && ch.isAvailable());

        if (candidates.length === 0) return null;

        // Extract unique descending priorities
        const prioritySet = new Set<number>();
        for (const ch of candidates) {
            prioritySet.add(ch.priority);
        }
        const sortedPriorities = Array.from(prioritySet).sort((a, b) => b - a);

        let targetPriorityIdx = retry;
        if (targetPriorityIdx >= sortedPriorities.length) {
            targetPriorityIdx = sortedPriorities.length - 1;
        }
        const targetPriority = sortedPriorities[targetPriorityIdx];

        const targetBucket = candidates.filter(ch => ch.priority === targetPriority);
        if (targetBucket.length === 0) return null;
        if (targetBucket.length === 1) return targetBucket[0];

        // Smoothed Weighted Random Selection
        let sumWeight = 0;
        for (const ch of targetBucket) {
            sumWeight += Math.max(0, ch.weight);
        }

        let smoothingFactor = 1;
        let smoothingAdjustment = 0;

        if (sumWeight === 0) {
            sumWeight = targetBucket.length * 100;
            smoothingAdjustment = 100;
        } else if (sumWeight / targetBucket.length < 10) {
            smoothingFactor = 100;
        }

        const totalWeight = sumWeight * smoothingFactor;
        let randomWeight = Math.floor(Math.random() * totalWeight);

        for (const ch of targetBucket) {
            const w = Math.max(0, ch.weight);
            randomWeight -= (w * smoothingFactor + smoothingAdjustment);
            if (randomWeight < 0) {
                return ch;
            }
        }

        return targetBucket[0];
    }

    public selectZeroCostChannel(group: string, model: string, retry: number = 0): Channel | null {
        const zeroCostCandidates = Array.from(this.channels.values()).filter(ch => {
            if (!ch.isAvailable() || !ch.isZeroCost()) return false;
            return ch.models.includes(model) || ch.models.includes("*");
        });

        if (zeroCostCandidates.length === 0) return null;

        zeroCostCandidates.sort((a, b) => b.priority - a.priority);

        const idx = retry >= zeroCostCandidates.length ? retry % zeroCostCandidates.length : retry;
        return zeroCostCandidates[idx];
    }
}

export class HealthProbeEngine {
    constructor(private pool: ChannelPool) {}

    public shouldDisableChannel(statusCode?: number, error?: Error | string): boolean {
        if (statusCode === 401 || statusCode === 403 || statusCode === 429) return true;
        if (statusCode !== undefined && statusCode >= 500 && statusCode <= 504) return true;

        if (error) {
            const msg = (typeof error === "string" ? error : error.message).toLowerCase();
            if (
                msg.includes("insufficient_quota") ||
                msg.includes("quota_exceeded") ||
                msg.includes("invalid_api_key") ||
                msg.includes("connection refused") ||
                msg.includes("timeout") ||
                msg.includes("service unavailable")
            ) {
                return true;
            }
        }
        return false;
    }

    public shouldRetry(statusCode?: number, _error?: Error | string, remainingRetries: number = 0): boolean {
        if (remainingRetries <= 0) return false;
        if (statusCode === 400 || statusCode === 422) return false;
        if (statusCode !== undefined && statusCode >= 200 && statusCode < 300) return false;
        return true;
    }

    public autoBan(channel: Channel, reason: string): void {
        const banned = channel.recordFailure(reason);
        if (banned) {
            this.pool.updateChannelStatus(channel.id, ChannelStatus.AUTO_DISABLED);
        }
    }

    public autoEnable(channel: Channel): void {
        if (channel.status === ChannelStatus.AUTO_DISABLED && channel.autoEnable) {
            channel.status = ChannelStatus.ENABLED;
            channel.consecutiveFailures = 0;
            channel.consecutiveSuccesses = 0;
            channel.healthScore = 0.5;
            this.pool.updateChannelStatus(channel.id, ChannelStatus.ENABLED);
        }
    }
}

export interface RelayExecutionRequest {
    group?: string;
    model: string;
    prompt?: string;
    contextSize?: number;
    zeroCostOnly?: boolean;
    spendCap?: number;
    maxRetries?: number;
    requestPath?: string;
    metadata?: Record<string, any>;
}

export interface RelayExecutionResult<T = any> {
    success: boolean;
    channelId?: string;
    channelName?: string;
    usedKey?: string;
    costTier?: CostTier;
    zeroCost: boolean;
    retriesUsed: number;
    failoverTrail: string[];
    latencyMs?: number;
    payload?: T;
    error?: string;
}

export class ChannelRelay {
    private pool: ChannelPool;
    private probe: HealthProbeEngine;
    private maxRetries: number = 3;

    constructor(pool?: ChannelPool, probe?: HealthProbeEngine) {
        this.pool = pool || new ChannelPool();
        this.probe = probe || new HealthProbeEngine(this.pool);
    }

    public getPool(): ChannelPool {
        return this.pool;
    }

    public getProbe(): HealthProbeEngine {
        return this.probe;
    }

    public async executeRelay<T = any>(
        req: RelayExecutionRequest,
        executor: (channel: Channel, key: string) => Promise<{ payload: T; statusCode: number; error?: Error }>
    ): Promise<RelayExecutionResult<T>> {
        const group = req.group || "default";
        const maxTries = req.maxRetries !== undefined ? req.maxRetries : this.maxRetries;
        const trail: string[] = [];
        let lastError: Error | string = "Unknown error";

        for (let retry = 0; retry <= maxTries; retry++) {
            let channel: Channel | null = null;

            if (req.zeroCostOnly || (req.spendCap === 0 && group === "zero_cost")) {
                channel = this.pool.selectZeroCostChannel(group, req.model, retry);
            } else {
                channel = this.pool.selectChannel(group, req.model, retry, req.requestPath);
            }

            if (!channel) {
                if (req.zeroCostOnly) {
                    return {
                        success: false,
                        zeroCost: true,
                        retriesUsed: retry,
                        failoverTrail: trail,
                        error: `Zero-cost channel pool exhausted for model ${req.model}`
                    };
                }
                channel = this.pool.selectChannel(group, req.model, retry, req.requestPath);
                if (!channel) {
                    lastError = `No available channel found for group=${group} model=${req.model}`;
                    break;
                }
            }

            const key = channel.getNextKey();
            trail.push(`${channel.name}(#${channel.id},p=${channel.priority},w=${channel.weight})`);

            const start = Date.now();
            try {
                const res = await executor(channel, key);
                const latency = Date.now() - start;

                if (!res.error && res.statusCode >= 200 && res.statusCode < 300) {
                    channel.recordSuccess(latency);
                    return {
                        success: true,
                        channelId: channel.id,
                        channelName: channel.name,
                        usedKey: key,
                        costTier: channel.costTier,
                        zeroCost: channel.isZeroCost(),
                        retriesUsed: retry,
                        failoverTrail: trail,
                        latencyMs: latency,
                        payload: res.payload
                    };
                }

                const errMsg = res.error ? res.error.message : `HTTP status ${res.statusCode}`;
                lastError = new Error(`Channel ${channel.name} failed: ${errMsg}`);

                if (this.probe.shouldDisableChannel(res.statusCode, res.error)) {
                    this.probe.autoBan(channel, errMsg);
                } else {
                    channel.recordFailure(errMsg);
                }

                const remaining = maxTries - retry;
                if (!this.probe.shouldRetry(res.statusCode, res.error, remaining)) {
                    break;
                }
            } catch (err: any) {
                const latency = Date.now() - start;
                lastError = err;
                const errMsg = err.message || String(err);

                if (this.probe.shouldDisableChannel(undefined, err)) {
                    this.probe.autoBan(channel, errMsg);
                } else {
                    channel.recordFailure(errMsg);
                }

                const remaining = maxTries - retry;
                if (!this.probe.shouldRetry(undefined, err, remaining)) {
                    break;
                }
            }
        }

        return {
            success: false,
            zeroCost: req.zeroCostOnly || false,
            retriesUsed: Math.max(0, trail.length - 1),
            failoverTrail: trail,
            error: typeof lastError === "string" ? lastError : lastError.message
        };
    }
}
