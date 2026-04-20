/**
 * Mission Evaluator: Success Criteria Verification (Task D8)
 * Analyzes mission outcomes against high-level objectives using LLM reasoning.
 */

export class MissionEvaluator {
    /**
     * Evaluates if a mission lane successfully achieved its goal.
     * @param {string} goal - The original mission goal.
     * @param {object} transcript - The lane transcript (events).
     * @param {string} finalUrl - Current tab URL.
     * @returns {object} - { success: boolean, confidence: number, rationale: string }
     */
    static async evaluate(goal, transcript, finalUrl) {
        console.log(`[EVALUATOR] Evaluating Mission Success for: ${goal}`);

        // 1. Gather Evidence
        const lastEvents = transcript.events?.slice(-10) || []; // Look at the final actions
        const evidence = {
            goal,
            finalUrl,
            actionCount: transcript.events?.length || 0,
            lastActions: lastEvents.map(e => ({ type: e.type, data: e.data }))
        };

        // 2. Consult the Oracle (LLM)
        if (typeof process_via_offscreen !== 'undefined') {
            const evaluation = await process_via_offscreen("EVALUATE_MISSION_SUCCESS", evidence);
            
            if (evaluation && typeof evaluation.success === 'boolean') {
                console.log(`[EVALUATOR] Verdict: ${evaluation.success ? 'PASSED' : 'FAILED'} (${evaluation.confidence * 100}%)`);
                return {
                    success: evaluation.success,
                    confidence: evaluation.confidence || 0.5,
                    rationale: evaluation.rationale || "LLM Analysis Complete"
                };
            }
        }

        // Fallback: Heuristic Check
        const actionSuccessCount = lastEvents.filter(e => e.type === 'ACTION_SUCCESS').length;
        const hasNavigation = evidence.actionCount > 0;

        return {
            success: actionSuccessCount > 0,
            confidence: 0.3,
            rationale: "Heuristic fallback: Mission ended with successful actions."
        };
    }
}
