// Package vault is the World Tree skill registry — the Camelot-Ecosystem index.
//
// The Ledger holds skill cartridges and serves Vector-Similarity-Search (VSS)
// lookups so the Multivoice-Router loads only the few skills an intent needs
// (honoring the 4GB Scarcity Protocol). The default backend is a pure-Go,
// dependency-free in-memory index seeded with a starter skill set; a SQLite
// CRIU ledger is a drop-in behind the same interface (see Open backends).
package vault

import (
	"hash/fnv"
	"sort"
	"strings"
)

// Skill is one Ecosystem cartridge.
type Skill struct {
	IDHash   uint64
	Name     string
	Keywords []string
	Payload  string
}

// Ledger is the mounted World Tree.
type Ledger struct {
	path   string
	skills []Skill
}

// MountLedger opens the World Tree at path. An empty path (or a non-existent
// file) mounts the in-memory starter registry — never fails, so the factory
// always boots. A real SQLite file backend is a future drop-in.
func MountLedger(path string) (*Ledger, error) {
	l := &Ledger{path: path, skills: starterSkills()}
	return l, nil
}

// VSSSearchSkills returns the top-k skills whose keywords best match the intent.
// Pure keyword-overlap scoring (a stand-in for embedding cosine VSS) — fast,
// deterministic, and dependency-free.
func (l *Ledger) VSSSearchSkills(intent string, topK int) []Skill {
	terms := tokenize(intent)
	type scored struct {
		skill Skill
		score int
	}
	ranked := make([]scored, 0, len(l.skills))
	for _, s := range l.skills {
		score := 0
		for _, kw := range s.Keywords {
			if terms[kw] {
				score++
			}
		}
		if score > 0 {
			ranked = append(ranked, scored{s, score})
		}
	}
	sort.SliceStable(ranked, func(i, j int) bool { return ranked[i].score > ranked[j].score })
	if topK > len(ranked) {
		topK = len(ranked)
	}
	out := make([]Skill, 0, topK)
	for i := 0; i < topK; i++ {
		out = append(out, ranked[i].skill)
	}
	return out
}

// Seal flushes and closes the ledger (no-op for the in-memory backend).
func (l *Ledger) Seal() error { return nil }

// Len reports the number of indexed skills.
func (l *Ledger) Len() int { return len(l.skills) }

func tokenize(s string) map[string]bool {
	out := map[string]bool{}
	for _, t := range strings.FieldsFunc(strings.ToLower(s), func(r rune) bool {
		return !(r == '_' || (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9'))
	}) {
		out[t] = true
	}
	return out
}

func mk(name string, payload string, keywords ...string) Skill {
	h := fnv.New64a()
	_, _ = h.Write([]byte(name))
	return Skill{IDHash: h.Sum64(), Name: name, Keywords: keywords, Payload: payload}
}

func starterSkills() []Skill {
	return []Skill{
		mk("wasm.compile", "compile rust to wasm32-wasip1", "build", "wasm", "rust", "compile", "cargo"),
		mk("react.scaffold", "scaffold a react/next component", "build", "react", "next", "ui", "component"),
		mk("rag.architect", "design a retrieval-augmented architecture", "architect", "design", "rag", "analyze", "context"),
		mk("security.audit", "run a security/fuzz audit", "security", "audit", "fuzz", "balance", "monitor"),
		mk("status.report", "report system status", "status", "report", "health", "metrics"),
	}
}
