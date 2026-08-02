package orchestration

import (
	"strings"
)

// DetermineBurnTier analyzes the Sovereign Intent to set the intelligence dial
func DetermineBurnTier(intent string) string {
	intentLower := strings.ToLower(intent)
	
	// Tier 5: Fable (Macro-Architecture)
	if strings.Contains(intentLower, "architect") || strings.Contains(intentLower, "blueprint") || strings.Contains(intentLower, "design system") {
		return "Anthropic_Fable_5"
	}
	
	// Tier 4: Opus (Complex Debugging)
	if strings.Contains(intentLower, "debug memory") || strings.Contains(intentLower, "cryptography") {
		return "Anthropic_Opus_4.8"
	}
	
	// Tier 3: Sonnet (Standard Bioswarm Fabrication)
	if strings.Contains(intentLower, "build") || strings.Contains(intentLower, "compile") {
		return "Anthropic_Sonnet_3.5"
	}
	
	// Tier 2: Haiku (Volume Work)
	if strings.Contains(intentLower, "summarize") || strings.Contains(intentLower, "parse") {
		return "Anthropic_Haiku_3.5"
	}
	
	// Tier 1: Local TinyLM (Default / Zero Cost)
	return "Local_Qwen2.5_0.5B"
}
