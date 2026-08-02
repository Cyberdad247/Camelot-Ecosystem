package orchestration

import (
	"context"
	"fmt"

	"camelot-os/api/claude"
)

// HandleAdvisorInterrupt catches the sys.advisor tool call from a Bioswarm Squire
func HandleAdvisorInterrupt(ctx context.Context, squireID string, errorContext string, attemptedFix string) string {
	fmt.Printf("⚠️ [SIR_WATCHDOG] Squire %s hit a compilation wall. Triggering Inverted Callback...\n", squireID)
	fmt.Println("⚡ [MERLIN_Ω] Waking Fable-Tier Orchestrator for Strategic Pivot...")
	
	// 1. Construct the high-density context for Fable 5
	fablePrompt := fmt.Sprintf(`
[SYSTEM_IDENTITY: MERLIN_Ω // FABLE_TIER_ADVISOR]
Your sub-agent (%s) has failed to execute the UAST Blueprint.
Error Context: %s
Attempted Fix: %s
Provide the exact, mathematically sound strategic pivot to unblock the agent. Do not write the full code. Output only the correction logic.
`, squireID, errorContext, attemptedFix)

	// 2. Invoke Fable 5 (Max Burn Tier)
	pivotStrategy, err := claude.ExecuteCompletion(ctx, "Anthropic_Fable_5", fablePrompt)
	if err != nil {
		return "[FATAL] Fable 5 unreachable. Triggering MADV_DONTNEED rollback."
	}
	fmt.Println("💤 [MERLIN_Ω] Pivot delivered. Returning to sleep state.")

	// 3. Return the strategy back to the suspended Squire
	return fmt.Sprintf("ADVISOR_PIVOT_RECEIVED:\n%s", pivotStrategy)
}
