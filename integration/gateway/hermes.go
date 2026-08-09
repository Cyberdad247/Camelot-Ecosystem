package main

import "strings"

// Hermes is an ADAPTER ONLY (ADR-001): it may map transcripts to proposed
// intents, but it holds no reference to the lease store, tool broker, or
// audit log, and cannot execute anything. Phrases come from the generated
// catalog — mirrors matchIntent() in @camelot/contracts.

// hermesProposal is what the adapter is allowed to say: "this transcript
// looks like that skill". Nothing more.
type hermesProposal struct {
	SkillID string
	Matched bool
}

// hermesMatchIntent resolves a transcript against every phrase in the
// catalog, with a total order so the winner never depends on registry
// position:
//
//  1. longest matching phrase wins — a specific phrase beats a generic one
//     that happens to be a substring of the same utterance;
//  2. then higher intent.priority — lets a skill claim an utterance it shares
//     vocabulary with, without anyone reordering the manifest;
//  3. then lower skill id, lexically — arbitrary but deterministic, so a tie
//     is never a coin toss.
//
// Rule 1 is what stops "prepare a staging deployment review" resolving to the
// tier-1 staging read. Rule 2 is what stops the next such collision needing a
// code change instead of a manifest edit.
func hermesMatchIntent(transcript string) hermesProposal {
	t := strings.ToLower(transcript)

	best := hermesProposal{}
	bestLen, bestPriority, bestID := 0, 0, ""

	for _, s := range skillRegistry {
		for _, phrase := range s.Phrases {
			if !strings.Contains(t, phrase) {
				continue
			}
			switch {
			case len(phrase) > bestLen,
				len(phrase) == bestLen && s.Priority > bestPriority,
				len(phrase) == bestLen && s.Priority == bestPriority && (bestID == "" || s.ID < bestID):
			default:
				continue
			}
			best = hermesProposal{SkillID: s.ID, Matched: true}
			bestLen, bestPriority, bestID = len(phrase), s.Priority, s.ID
		}
	}
	return best
}

// hermesSmallTalkReply is the canned reply for unmatched transcripts.
func hermesSmallTalkReply() string {
	return "I'm Anya. I can read staging status, prepare a deployment review, create a change request, or save a note. What do you need?"
}
