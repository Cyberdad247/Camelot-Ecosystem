/**
 * Transcript Manager: Structured Lane Replayability (Task D6)
 * Captures and persists the exact sequence of actions and results for a mission lane.
 */

export class TranscriptManager {
    constructor(laneId) {
        this.laneId = laneId;
        this.events = [];
        this.startTime = Date.now();
    }

    /**
     * Record an event in the transcript
     * @param {string} type - 'ACTION', 'SNAPSHOT', 'RESULT', 'RECOVERY'
     * @param {object} data 
     */
    async log(type, data) {
        const event = {
            laneId: this.laneId,
            timestamp: Date.now(),
            offsetMs: Date.now() - this.startTime,
            type,
            data
        };
        
        this.events.push(event);
        console.log(`[TRANSCRIPT] [${this.laneId}] Recorded ${type}`);
        
        // Persist incrementally to storage
        await this._persist();
    }

    async _persist() {
        const key = `transcript_${this.laneId}`;
        await chrome.storage.local.set({ [key]: this.events });
    }

    /**
     * Exports the transcript as a replayable JSON object
     */
    getReplayable() {
        return {
            version: "1.0",
            laneId: this.laneId,
            recordedAt: new Date(this.startTime).toISOString(),
            events: this.events
        };
    }

    static async getTranscript(laneId) {
        const key = `transcript_${laneId}`;
        const result = await chrome.storage.local.get(key);
        return result[key] || [];
    }
}
