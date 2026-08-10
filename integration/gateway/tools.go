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
	leases *LeaseStore
}

func NewToolBroker(leases *LeaseStore) *ToolBroker {
	return &ToolBroker{leases: leases}
}

// Execute runs a skill for a turn. For effectful skills, lease must reference
// an approved, unexpired, unconsumed lease for capability "skill:<id>"
// carrying its signed token; the lease is consumed atomically before
// execution. Read-only (tier-1) skills run lease-free by design.
func (b *ToolBroker) Execute(skillID, turnID string, lease *CapabilityLease) (SkillArtifact, string, error) {
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

	artifact, reply := runSkill(skill, turnID)
	return artifact, reply, nil
}
