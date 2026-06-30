package orchestration

import (
	"crypto/md5"
	"encoding/hex"
	"math"
	"regexp"
	"sync"
)

// ── OmniRoute Affinity Layer ─────────────────────────────────────────────────
//
// Sits on top of the Polyglot Matrix. Two behaviours, ported from the OmniRoute
// affinity plan (docs/plans/2026-05-23-omniroute-affinity-v1000.md):
//
//   1. Stateful affinity pinning — structurally-identical prompts share an
//      affinity key and stick to the same engine, maximizing KV-cache prefix
//      hits (mirrors control_plane/cli_intercept.generate_affinity_key).
//   2. DualMap-lite SLO escape — per-engine TTFT is tracked; when a pinned
//      engine becomes a hotspot (avg TTFT breaches the SLO) the layer escapes
//      to the coolest alternate engine instead of honoring the sticky pin.

var (
	reFile = regexp.MustCompile(`[a-zA-Z0-9_\-./]+\.[a-z]{2,4}`)
	reUUID = regexp.MustCompile(`\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b`)
	reNum  = regexp.MustCompile(`\b\d+\b`)
)

// GenerateAffinityKey abstracts dynamic values (file paths, UUIDs, numbers) so
// "Audit file X" and "Audit file Y" yield the same key. Mirrors the Python
// generate_affinity_key (md5 of the structural template, first 8 hex chars).
func GenerateAffinityKey(intent string) string {
	s := reFile.ReplaceAllString(intent, "<FILE>")
	s = reUUID.ReplaceAllString(s, "<UUID>")
	s = reNum.ReplaceAllString(s, "<NUM>")
	sum := md5.Sum([]byte(s))
	return hex.EncodeToString(sum[:])[:8]
}

// AffinityDecision reports how an intent was routed.
type AffinityDecision struct {
	Knight   string
	Key      string
	CacheHit bool // honored an existing healthy pin
	Escaped  bool // pinned engine breached SLO -> rerouted to a cooler engine
}

// AffinityRouter is the OmniRoute routing layer.
type AffinityRouter struct {
	mu     sync.Mutex
	pins   map[string]string    // affinity_key -> knight
	ttft   map[string][]float64 // knight -> recent TTFT samples (ms)
	SLOms  float64
	window int
}

// NewAffinityRouter builds the layer with a TTFT SLO (ms); <=0 defaults to 2000.
func NewAffinityRouter(sloMs float64) *AffinityRouter {
	if sloMs <= 0 {
		sloMs = 2000.0
	}
	return &AffinityRouter{
		pins:   map[string]string{},
		ttft:   map[string][]float64{},
		SLOms:  sloMs,
		window: 10,
	}
}

// SelectKnight decides the engine for an intent. A healthy pin -> cache hit; a
// hot pin -> escape to the coolest alternate; no pin -> the fresh polyglot pick.
// fresh() supplies the keyword/Polyglot decision (called only when needed).
func (a *AffinityRouter) SelectKnight(intent string, fresh func() string) AffinityDecision {
	key := GenerateAffinityKey(intent)
	a.mu.Lock()
	defer a.mu.Unlock()

	if pinned, ok := a.pins[key]; ok {
		if a.healthyLocked(pinned) {
			return AffinityDecision{Knight: pinned, Key: key, CacheHit: true}
		}
		// Hotspot — DualMap-lite escape to the coolest alternate engine.
		alt := a.coolestExceptLocked(pinned)
		if alt == "" {
			alt = fresh()
		}
		a.pins[key] = alt
		return AffinityDecision{Knight: alt, Key: key, Escaped: true}
	}

	k := fresh()
	a.pins[key] = k
	return AffinityDecision{Knight: k, Key: key}
}

// RecordTTFT records a Time-To-First-Token sample (ms) for an engine.
func (a *AffinityRouter) RecordTTFT(knight string, ms float64) {
	a.mu.Lock()
	defer a.mu.Unlock()
	h := append(a.ttft[knight], ms)
	if len(h) > a.window {
		h = h[len(h)-a.window:]
	}
	a.ttft[knight] = h
}

// AvgTTFT returns the rolling-average TTFT (ms) for an engine (0 if unseen).
func (a *AffinityRouter) AvgTTFT(knight string) float64 {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.avgLocked(knight)
}

// PinCount reports the number of active affinity pins.
func (a *AffinityRouter) PinCount() int {
	a.mu.Lock()
	defer a.mu.Unlock()
	return len(a.pins)
}

func (a *AffinityRouter) healthyLocked(knight string) bool {
	h := a.ttft[knight]
	if len(h) == 0 {
		return true // no evidence of a hotspot yet
	}
	return a.avgLocked(knight) < a.SLOms
}

func (a *AffinityRouter) avgLocked(knight string) float64 {
	h := a.ttft[knight]
	if len(h) == 0 {
		return 0
	}
	sum := 0.0
	for _, v := range h {
		sum += v
	}
	return sum / float64(len(h))
}

// coolestExceptLocked returns the known engine (excluding `hot`) with the lowest
// avg TTFT that is itself under SLO, or "" if there is no cooler alternate.
func (a *AffinityRouter) coolestExceptLocked(hot string) string {
	best := ""
	bestAvg := math.MaxFloat64
	for knight := range a.ttft {
		if knight == hot {
			continue
		}
		avg := a.avgLocked(knight)
		if avg < a.SLOms && avg < bestAvg {
			best, bestAvg = knight, avg
		}
	}
	return best
}
