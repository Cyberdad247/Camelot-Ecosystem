package main

import "strings"

// Hermes is an ADAPTER ONLY (ADR-001): it may map transcripts to proposed
// intents, but it holds no reference to the lease store, tool broker, or
// audit log, and cannot execute anything. Deterministic fixtures — mirrors
// matchIntent() in @camelot/contracts.

// hermesProposal is what the adapter is allowed to say: "this transcript
// looks like that skill". Nothing more.
type hermesProposal struct {
	SkillID string
	Matched bool
}

func hermesMatchIntent(transcript string) hermesProposal {
	t := strings.ToLower(transcript)
	for _, s := range skillRegistry {
		if strings.Contains(t, s.Match) {
			return hermesProposal{SkillID: s.ID, Matched: true}
		}
	}
	return hermesProposal{}
}

// hermesSmallTalkReply is the canned reply for unmatched transcripts.
func hermesSmallTalkReply() string {
	return "I'm Anya. I can read staging status, prepare a deployment review, or create a change request. What do you need?"
}
