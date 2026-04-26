// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
package soul

import (
	"strings"
)

// EngineWeight represents immutable weight locks per Titanium Law.
type EngineWeight float64

const (
	WOrchestration EngineWeight = 0.85 // Sir Boris  — Claude Code
	WContext       EngineWeight = 0.90 // Sir Helio  — Gemini CLI
	WVelocity      EngineWeight = 0.75 // Sir Codex  — OpenAI Codex
	WPrivacy       EngineWeight = 1.00 // Sir Ghost  — Local Qwen 3.5
	WSovereignty   EngineWeight = 0.80 // Sir Liberte — Open Source
	WKinetic       EngineWeight = 0.70 // Sir Forge  — Open Coder (local)
)

// KnightEngine represents a Foundry Council Knight engine definition.
type KnightEngine struct {
	KnightID     string       `json:"knight_id"`
	Engine       string       `json:"engine"`
	Weight       EngineWeight `json:"weight"`
	Function     string       `json:"function"`
	PrivacyLevel float64      `json:"privacy_level"`
}

// FoundryCouncil represents the frozen registry of engines.
var FoundryCouncil = []KnightEngine{
	{"sir_boris", "claude_code", WOrchestration, "Architecture, Colony Command, 13-Agent Critique", 0.3},
	{"sir_helio", "gemini_cli", WContext, "1M+ token context mapping", 0.2},
	{"sir_codex", "openai_codex", WVelocity, "High-velocity code generation", 0.2},
	{"sir_forge", "open_coder", WKinetic, "L2 Kinetic Code Generation — local open-weight", 0.7},
	{"sir_ghost", "local_qwen", WPrivacy, "Zero-Trust, air-gapped execution", 1.0},
	{"sir_liberte", "open_source", WSovereignty, "Anti-vendor lock-in, sovereign execution", 0.5},
}

// PrivacyKeywords triggers immediate reroute to air-gapped engine.
var PrivacyKeywords = []string{"secret", "local", "private", "credential", "key", "password"}

// IntentTensor represents multi-dimensional intent scoring vector.
type IntentTensor struct {
	Velocity    float64 `json:"velocity"`
	Magnitude   float64 `json:"magnitude"`
	Privacy     float64 `json:"privacy"`
	Environment float64 `json:"environment"`
}

const (
	Alpha = 0.20 // velocity weight
	Beta  = 0.35 // magnitude weight
	Gamma = 0.30 // privacy weight
	Delta = 0.15 // environment weight
)

// SoulEquation calculates the routing score: S_omega = alpha*V + beta*M + gamma*P + delta*E
func SoulEquation(t IntentTensor) float64 {
	return Alpha*t.Velocity + Beta*t.Magnitude + Gamma*t.Privacy + Delta*t.Environment
}

// RouteDecision represents the result of a routing decision.
type RouteDecision struct {
	KnightID        string       `json:"knight_id"`
	Engine          string       `json:"engine"`
	Weight          float64      `json:"weight"`
	Score           float64      `json:"score"`
	Tensor          IntentTensor `json:"tensor"`
	Reason          string       `json:"reason"`
	PrivacyOverride bool         `json:"privacy_override"`
}

// SoulRouter implements the MFOE Routing Matrix logic in Go.
type SoulRouter struct {
	Engines map[string]KnightEngine
	Routes  map[string]string
}

func NewSoulRouter() *SoulRouter {
	engines := make(map[string]KnightEngine)
	for _, e := range FoundryCouncil {
		engines[e.KnightID] = e
	}

	routes := map[string]string{
		"orchestration":   "sir_boris",
		"architecture":    "sir_boris",
		"colony":          "sir_boris",
		"critique":        "sir_boris",
		"vocal":           "sir_boris",
		"technical":       "sir_forge",
		"scaffold":        "sir_forge",
		"code_gen":        "sir_forge",
		"security_review": "sir_sentinel",
		"audit":           "sir_sentinel",
		"financial":       "sir_valerian",
		"roi":             "sir_valerian",
	}

	return &SoulRouter{
		Engines: engines,
		Routes:  routes,
	}
}

func (sr *SoulRouter) Route(intent string, velocity, magnitude, privacy float64) RouteDecision {
	intentLower := strings.ToLower(intent)

	// --- Privacy Override (Titanium Law) ---
	hasPrivacyKeyword := false
	for _, kw := range PrivacyKeywords {
		if strings.Contains(intentLower, kw) {
			hasPrivacyKeyword = true
			break
		}
	}

	if privacy >= 0.8 || hasPrivacyKeyword {
		effectivePrivacy := privacy
		if hasPrivacyKeyword && effectivePrivacy < 0.9 {
			effectivePrivacy = 0.9
		}
		ghost := sr.Engines["sir_ghost"]
		tensor := IntentTensor{velocity, magnitude, effectivePrivacy, float64(ghost.Weight)}
		return RouteDecision{
			KnightID:        "sir_ghost",
			Engine:          ghost.Engine,
			Weight:          float64(ghost.Weight),
			Score:           SoulEquation(tensor),
			Tensor:          tensor,
			Reason:          "PRIVACY_OVERRIDE: Sir Ghost (air-gapped) selected",
			PrivacyOverride: true,
		}
	}

	// --- Keyword matching ---
	matchedKnightID := ""
	for kw, kid := range sr.Routes {
		if strings.Contains(intentLower, kw) {
			matchedKnightID = kid
			break
		}
	}

	// --- Tensor scoring ---
	var bestEngine KnightEngine
	var bestTensor IntentTensor
	var bestScore float64 = -1.0
	var reason string

	if matchedKnightID != "" {
		if e, ok := sr.Engines[matchedKnightID]; ok {
			bestEngine = e
			bestTensor = IntentTensor{velocity, magnitude, privacy, float64(e.Weight)}
			bestScore = SoulEquation(bestTensor)
			reason = "KEYWORD_MATCH: " + matchedKnightID
		}
	}

	if bestScore == -1.0 {
		for _, e := range sr.Engines {
			// Skip air-gapped for low privacy
			if e.PrivacyLevel >= 0.8 && privacy < 0.3 {
				continue
			}
			t := IntentTensor{velocity, magnitude, privacy, float64(e.Weight)}
			s := SoulEquation(t)
			if s > bestScore {
				bestScore = s
				bestEngine = e
				bestTensor = t
			}
		}
		reason = "TENSOR_SCORED"
	}

	if bestScore == -1.0 {
		// Fallback to Boris
		bestEngine = sr.Engines["sir_boris"]
		bestTensor = IntentTensor{velocity, magnitude, privacy, float64(bestEngine.Weight)}
		bestScore = SoulEquation(bestTensor)
		reason = "FALLBACK: sir_boris"
	}

	if magnitude >= 0.8 {
		reason += " | COMPLEXITY_SPIKE"
	}

	return RouteDecision{
		KnightID: bestEngine.KnightID,
		Engine:   bestEngine.Engine,
		Weight:   float64(bestEngine.Weight),
		Score:    bestScore,
		Tensor:   bestTensor,
		Reason:   reason,
	}
}
