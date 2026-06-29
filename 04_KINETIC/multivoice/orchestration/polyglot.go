// Package orchestration is the Polyglot Matrix + Multivoice-Router.
//
// The APEEv6Router maps an intent to the right Knight and the right LLM engine
// (OpenAI / Gemini / Claude). Providers are pluggable behind the Provider
// interface; the default build wires deterministic STUB providers (no network),
// so the router compiles and tests offline. Wire real providers by passing your
// own Provider implementations to NewAPEEv6RouterWith.
package orchestration

import (
	"context"
	"strings"

	"camelot-os/vault"
	"camelot-os/zeroclaw"
)

// Provider is one upstream LLM engine. Real OpenAI/Gemini/Claude clients
// implement this; the default is a deterministic stub (no API calls).
type Provider interface {
	Name() string
	Invoke(ctx context.Context, knight, intent, skills string) (string, error)
}

type stubProvider struct{ name string }

func (s stubProvider) Name() string { return s.name }
func (s stubProvider) Invoke(_ context.Context, knight, intent, skills string) (string, error) {
	tag := ""
	if skills != "" {
		tag = " +skills"
	}
	return "[" + s.name + "/" + knight + tag + "] " + intent, nil
}

type route struct {
	knight   string
	keywords []string
	provider string
}

// APEEv6Router routes intents across the Polyglot Matrix.
type APEEv6Router struct {
	routes    []route
	providers map[string]Provider
	fallback  route
}

// NewAPEEv6Router builds the router with the default STUB providers.
func NewAPEEv6Router() *APEEv6Router {
	return NewAPEEv6RouterWith(map[string]Provider{
		"openai": stubProvider{"OpenAI"},
		"gemini": stubProvider{"Gemini"},
		"claude": stubProvider{"Claude"},
	})
}

// NewAPEEv6RouterWith builds the router with caller-supplied providers
// (keyed "openai"/"gemini"/"claude").
func NewAPEEv6RouterWith(providers map[string]Provider) *APEEv6Router {
	return &APEEv6Router{
		providers: providers,
		routes: []route{
			{"sir_codex", []string{"build", "compile", "rust", "wasm", "react", "code"}, "openai"},
			{"sir_helios", []string{"architect", "design", "analyze", "rag", "context"}, "gemini"},
			{"sir_boris", []string{"balance", "fuzz", "security", "monitor", "audit"}, "claude"},
		},
		fallback: route{"sir_boris", nil, "claude"},
	}
}

// DetermineKnight selects the best Knight for the intent (skill keywords break
// ties / reinforce the match).
func (r *APEEv6Router) DetermineKnight(intent string, skills []vault.Skill) string {
	return r.matchRoute(intent, skills).knight
}

func (r *APEEv6Router) matchRoute(intent string, skills []vault.Skill) route {
	hay := strings.ToLower(intent)
	for _, s := range skills {
		hay += " " + strings.ToLower(strings.Join(s.Keywords, " "))
	}
	best := r.fallback
	bestScore := 0
	for _, rt := range r.routes {
		score := 0
		for _, kw := range rt.keywords {
			if strings.Contains(hay, kw) {
				score++
			}
		}
		if score > bestScore {
			bestScore, best = score, rt
		}
	}
	return best
}

// InvokeKnightWithSkills dispatches the intent to the Knight's bound provider,
// injecting the zero-copy skill region.
func (r *APEEv6Router) InvokeKnightWithSkills(ctx context.Context, knight, intent string, fd *zeroclaw.SkillFD) (string, error) {
	provName := r.fallback.provider
	for _, rt := range r.routes {
		if rt.knight == knight {
			provName = rt.provider
			break
		}
	}
	prov := r.providers[provName]
	if prov == nil {
		prov = stubProvider{provName}
	}
	skillStr := ""
	if fd != nil {
		skillStr = string(fd.Bytes())
	}
	return prov.Invoke(ctx, knight, intent, skillStr)
}
