package main

import "fmt"

// Skill BEHAVIOR. The catalog itself (the Skill struct and skillRegistry) is
// generated into skills_gen.go from contracts/skills.manifest.json — adding a
// skill is one manifest edit plus, at most, one case below.

func skillByID(id string) (Skill, bool) {
	for _, s := range skillRegistry {
		if s.ID == id {
			return s, true
		}
	}
	return Skill{}, false
}

// runSkill produces the result for a non-durable skill. Effectful skills are
// ONLY reachable through the broker (tools.go), which enforces the lease
// requirement before calling this. Durable skills do not come through here —
// see runDurableSkill.
func runSkill(skill Skill, turnID string) (SkillArtifact, string) {
	switch skill.ID {
	case "ops.staging.read":
		return SkillArtifact{
				Kind:    skill.ArtifactKind,
				ID:      "staging-status-" + turnID,
				Summary: "staging: 4/4 services healthy, last deploy v9000.14, error rate 0.02%",
			},
			"Staging is green: four of four services healthy. Last deploy was v9000.14 and the error rate is holding at 0.02 percent."
	case "deployment.review.prepare":
		return SkillArtifact{
				Kind:    skill.ArtifactKind,
				ID:      "deploy-review-draft-" + turnID,
				Summary: "Draft review: voice-slice gateway + node-agent, 2 risks flagged, checklist 9 items",
			},
			"I prepared a deployment review draft. It covers the voice-slice gateway and node agent, flags two risks, and includes a nine-item checklist."
	case "change_request.create":
		return SkillArtifact{
				Kind:    skill.ArtifactKind,
				ID:      "cr-" + turnID,
				Summary: "Change request: scale api tier, window Sat 02:00 UTC, rollback plan attached",
			},
			"The change request is filed: scale the api tier during the Saturday 02:00 UTC window, rollback plan attached."
	default:
		return SkillArtifact{}, fmt.Sprintf("Skill %s has no fixture implementation.", skill.ID)
	}
}

// runDurableSkill performs a real side effect. Reached only from the broker,
// and only after the single-use lease has already been consumed — so a
// failure here is terminal for this turn by design: there is no lease left to
// retry with, and manufacturing one would let a single approval act twice.
func runDurableSkill(skill Skill, turnID, leaseID, content string, effects *EffectStore) (SkillArtifact, string, error) {
	if effects == nil {
		return SkillArtifact{}, "", fmt.Errorf("skill %s is durable but no effect store is configured", skill.ID)
	}
	switch skill.ID {
	case "notes.local.write":
		res, err := effects.WriteNote(skill.ID, leaseID, content)
		if err != nil {
			return SkillArtifact{}, "", err
		}
		return SkillArtifact{
				Kind: skill.ArtifactKind,
				ID:   "note-" + turnID,
				// The path and digest, never the body.
				Summary: fmt.Sprintf("wrote %s (%d bytes, sha256 %s)", res.RelPath, res.Bytes, res.SHA256[:12]),
			},
			fmt.Sprintf("Saved. The note is %d bytes at %s.", res.Bytes, res.RelPath),
			nil
	default:
		return SkillArtifact{}, "", fmt.Errorf("skill %s is durable but has no effect implementation", skill.ID)
	}
}
