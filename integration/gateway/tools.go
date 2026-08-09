package main

import (
	"errors"
	"fmt"
)

// ToolBroker is the ONLY code path that executes skills. Effectful skills
// require a valid approved lease; there is no bypass. Hermes and the HTTP
// layer never call runSkill directly — tests enforce the broker's refusals (T1).

var ErrLeaseRequired = errors.New("effectful action requires an approved capability lease")

type ToolBroker struct {
	leases  *LeaseStore
	effects *EffectStore
}

func NewToolBroker(leases *LeaseStore, effects *EffectStore) *ToolBroker {
	return &ToolBroker{leases: leases, effects: effects}
}

// Execute runs a skill for a turn. For effectful skills, lease must reference
// an approved, unexpired, unconsumed lease for capability "skill:<id>"
// carrying its signed token; the lease is consumed atomically before
// execution. Read-only (tier-1) skills run lease-free by design.
//
// content is the material a durable skill acts on (the note body). It is
// ignored by non-durable skills and never reaches the audit log.
//
// ORDERING IS THE IDEMPOTENCY GUARANTEE. Consume happens strictly before any
// side effect, and Consume is atomic and single-use. A replayed request —
// including the "effect succeeded but the response was lost" case — fails at
// the lease and never reaches the effect a second time.
func (b *ToolBroker) Execute(skillID, turnID, content string, lease *CapabilityLease) (SkillArtifact, string, error) {
	skill, ok := skillByID(skillID)
	if !ok {
		return SkillArtifact{}, "", fmt.Errorf("unknown skill %q", skillID)
	}

	if skill.Effectful {
		if lease == nil {
			return SkillArtifact{}, "", ErrLeaseRequired
		}
		capability := "skill:" + skill.ID
		if _, err := b.leases.Consume(lease.LeaseID, capability, lease.Token); err != nil {
			return SkillArtifact{}, "", fmt.Errorf("lease rejected: %w", err)
		}
	}

	if skill.Durable {
		return runDurableSkill(skill, turnID, content, b.effects)
	}
	artifact, reply := runSkill(skill, turnID)
	return artifact, reply, nil
}
