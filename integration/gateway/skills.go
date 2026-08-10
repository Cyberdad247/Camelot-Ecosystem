package main

import "fmt"

// Skill is one governed capability. The three bootstrap skills mirror
// INTENT_FIXTURES in @camelot/contracts (fixture parity is asserted in tests).
type Skill struct {
	ID                   string
	Tier                 int
	Effectful            bool
	ConfirmationRequired bool
	// Match is the lower-cased transcript keyword the Hermes adapter uses.
	Match string
}

var skillRegistry = []Skill{
	{ID: "ops.staging.read", Tier: 1, Effectful: false, ConfirmationRequired: false, Match: "staging"},
	{ID: "deployment.review.prepare", Tier: 2, Effectful: true, ConfirmationRequired: false, Match: "deployment review"},
	{ID: "change_request.create", Tier: 3, Effectful: true, ConfirmationRequired: true, Match: "change request"},
}

func skillByID(id string) (Skill, bool) {
	for _, s := range skillRegistry {
		if s.ID == id {
			return s, true
		}
	}
	return Skill{}, false
}

// runSkill produces the deterministic fixture result for a skill. Effectful
// skills are ONLY reachable through the broker (tools.go), which enforces the
// lease requirement before calling this.
func runSkill(skill Skill, turnID string) (SkillArtifact, string) {
	switch skill.ID {
	case "ops.staging.read":
		return SkillArtifact{
				Kind:    "staging_status",
				ID:      "staging-status-" + turnID,
				Summary: "staging: 4/4 services healthy, last deploy v9000.14, error rate 0.02%",
			},
			"Staging is green: four of four services healthy. Last deploy was v9000.14 and the error rate is holding at 0.02 percent."
	case "deployment.review.prepare":
		return SkillArtifact{
				Kind:    "deployment_review_draft",
				ID:      "deploy-review-draft-" + turnID,
				Summary: "Draft review: voice-slice gateway + node-agent, 2 risks flagged, checklist 9 items",
			},
			"I prepared a deployment review draft. It covers the voice-slice gateway and node agent, flags two risks, and includes a nine-item checklist."
	case "change_request.create":
		return SkillArtifact{
				Kind:    "change_request",
				ID:      "cr-" + turnID,
				Summary: "Change request: scale api tier, window Sat 02:00 UTC, rollback plan attached",
			},
			"The change request is filed: scale the api tier during the Saturday 02:00 UTC window, rollback plan attached."
	default:
		return SkillArtifact{}, fmt.Sprintf("Skill %s has no fixture implementation.", skill.ID)
	}
}
