import { TranscriptManager } from './transcript_manager.js';
import { MissionEvaluator } from './mission_evaluator.js';

/**
 * GOAL ORCHESTRATOR (Phase 53)
 * Manages the recursive execution of the Mission DAG.
 */

export class GoalOrchestrator {
    constructor(qfocus) {
        this.qfocus = qfocus;
        this.dag = [];
        this.status = "INIT";
        this.results = {};
        this.transcripts = {}; // laneId -> TranscriptManager
    }

    /**
     * Decomposes the high-level intent into a DAG.
     */
    async compile() {
        console.log(`[ORCHESTRATOR] Compiling DAG for: ${this.qfocus}`);
        const decomposition = await process_via_offscreen("DECOMPOSE_MISSION", {
            qfocus: this.qfocus
        });

        if (Array.isArray(decomposition)) {
            this.dag = decomposition.map(g => ({
                ...g,
                status: "PENDING",
                result: null,
                evaluation: null
            }));
            this.status = "COMPILED";
            console.log(`[ORCHESTRATOR] DAG Compiled with ${this.dag.length} goals.`);
            return true;
        }
        return false;
    }

    /**
     * Executes the DAG step-by-step.
     */
    async execute(executorFunc) {
        if (this.status !== "COMPILED") await this.compile();

        while (!this.isFinished()) {
            const readyGoals = this.getReadyGoals();
            if (readyGoals.length === 0 && !this.isFinished()) {
                console.error("[ORCHESTRATOR] Deadlock detected or all goals blocked.");
                break;
            }

            for (const goal of readyGoals) {
                console.log(`[ORCHESTRATOR] Executing Sub-Goal: ${goal.id} - ${goal.description}`);
                goal.status = "RUNNING";
                
                const laneId = `lane_${goal.id}_${Date.now()}`;
                const transcript = new TranscriptManager(laneId);
                this.transcripts[goal.id] = transcript;

                try {
                    // Inject context from previous results if needed
                    const context = this.getDependencyContext(goal);
                    
                    // Task D6: Capture execution in transcript
                    await transcript.log('GOAL_START', { description: goal.description, context });
                    
                    // The executorFunc should ideally take laneId to pass to ActionExecutor
                    const result = await executorFunc(goal.description, context, laneId);

                    // Task D8: Evaluate Mission Success
                    let finalUrl = "unknown";
                    try {
                        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
                        finalUrl = tabs[0]?.url || "unknown";
                    } catch (e) {}

                    const evaluation = await MissionEvaluator.evaluate(goal.description, transcript, finalUrl);
                    
                    goal.status = evaluation.success ? "COMPLETED" : "FAILED";
                    goal.result = result;
                    goal.evaluation = evaluation;
                    this.results[goal.id] = { result, evaluation, transcript: transcript.getReplayable() };

                    await transcript.log('GOAL_END', { status: goal.status, evaluation });

                    // Phase 54: Predictive Execution Loop
                    if (goal.status === "COMPLETED") {
                        console.log(`[ORCHESTRATOR] Goal ${goal.id} finished. Pondering future requirements...`);
                        const predictions = await process_via_offscreen("PREDICT_NEXT_MOVE", {
                            dag_state: this.dag.map(g => ({ id: g.id, status: g.status, desc: g.description })),
                            recent_results: this.results
                        });

                        if (predictions && Array.isArray(predictions)) {
                            predictions.forEach(p => {
                                if (p.confidence > 0.7) {
                                    console.log(`[ORCHESTRATOR] (PREDICT) High-confidence move detected: "${p.prediction}" (${p.rationale})`);
                                }
                            });
                        }
                    }
                } catch (e) {
                    console.error(`[ORCHESTRATOR] Goal ${goal.id} FAILED:`, e);
                    goal.status = "FAILED";
                    await transcript.log('GOAL_ERROR', { error: e.message });
                }
            }
        }

        console.log("[ORCHESTRATOR] Mission DAG Execution Finished.");
        return this.results;
    }

    getReadyGoals() {
        return this.dag.filter(g =>
            g.status === "PENDING" &&
            g.dependencies.every(depId => this.results[depId] !== undefined)
        );
    }

    getDependencyContext(goal) {
        const context = {};
        goal.dependencies.forEach(depId => {
            context[depId] = this.results[depId];
        });
        return context;
    }

    isFinished() {
        return this.dag.every(g => g.status === "COMPLETED" || g.status === "FAILED");
    }
}
