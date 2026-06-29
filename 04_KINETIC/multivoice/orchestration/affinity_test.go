package orchestration

import (
	"context"
	"strings"
	"testing"

	"camelot-os/vault"
	"camelot-os/zeroclaw"
)

// Mirrors the OmniRoute plan's test: structurally-identical prompts (different
// file) must yield the same affinity key.
func TestAffinityKey_Consistency(t *testing.T) {
	k1 := GenerateAffinityKey("Summarize this file: C:/path/a.py")
	k2 := GenerateAffinityKey("Summarize this file: C:/path/b.py")
	if k1 != k2 {
		t.Fatalf("expected same affinity key, got %q vs %q", k1, k2)
	}
	if len(k1) != 8 {
		t.Fatalf("key length = %d, want 8", len(k1))
	}
	// Numbers and UUIDs are abstracted too.
	if GenerateAffinityKey("retry job 17") != GenerateAffinityKey("retry job 4242") {
		t.Fatal("numbers should be abstracted to <NUM>")
	}
	// Structurally different prompts differ.
	if GenerateAffinityKey("build a wasm module") == GenerateAffinityKey("audit security posture") {
		t.Fatal("different structure must yield different keys")
	}
}

func TestAffinity_StickyCacheHit(t *testing.T) {
	a := NewAffinityRouter(2000)
	calls := 0
	fresh := func() string { calls++; return "sir_codex" }

	d1 := a.SelectKnight("build wasm from alpha.rs", fresh)
	if d1.CacheHit || d1.Escaped || d1.Knight != "sir_codex" {
		t.Fatalf("first route should be a fresh pin: %+v", d1)
	}
	// Same structural intent -> sticky cache hit, fresh() NOT called again.
	d2 := a.SelectKnight("build wasm from beta.rs", fresh)
	if !d2.CacheHit || d2.Knight != "sir_codex" {
		t.Fatalf("second route should be a cache hit: %+v", d2)
	}
	if calls != 1 {
		t.Fatalf("fresh() called %d times, want 1 (cache hit avoided it)", calls)
	}
	if a.PinCount() != 1 {
		t.Fatalf("pin count = %d, want 1", a.PinCount())
	}
}

func TestAffinity_SLOEscapeToCoolest(t *testing.T) {
	a := NewAffinityRouter(2000)
	fresh := func() string { return "sir_codex" }

	// Pin the intent to sir_codex.
	a.SelectKnight("compile the kernel", fresh)
	// sir_codex becomes a hotspot; sir_helios is cool.
	a.RecordTTFT("sir_codex", 3500) // > SLO
	a.RecordTTFT("sir_helios", 120) // cool alternate

	d := a.SelectKnight("compile the kernel", fresh)
	if !d.Escaped {
		t.Fatalf("expected SLO escape, got %+v", d)
	}
	if d.Knight != "sir_helios" {
		t.Fatalf("escape should pick coolest alternate sir_helios, got %q", d.Knight)
	}
	// The pin is rebound to the cool engine for subsequent hits.
	a.RecordTTFT("sir_helios", 100)
	d2 := a.SelectKnight("compile the kernel", fresh)
	if !d2.CacheHit || d2.Knight != "sir_helios" {
		t.Fatalf("after escape, expected sticky hit on sir_helios: %+v", d2)
	}
}

// End-to-end: the MultivoiceRouter uses the affinity layer and records TTFT.
func TestRouteIntent_WithAffinityLayer(t *testing.T) {
	led, _ := vault.MountLedger("")
	_ = zeroclaw.InitializeArena(16)
	mvr := &MultivoiceRouter{
		PolyglotEngine: NewAPEEv6Router(),
		EcosystemDB:    led,
		Affinity:       NewAffinityRouter(2000),
	}
	resp, err := mvr.RouteIntent(context.Background(), "build a wasm module from alpha.rs", "cli")
	if err != nil {
		t.Fatalf("route: %v", err)
	}
	if !strings.Contains(resp, "sir_codex") {
		t.Fatalf("expected codex route, got %q", resp)
	}
	if mvr.Affinity.PinCount() != 1 {
		t.Fatalf("expected 1 affinity pin after a route, got %d", mvr.Affinity.PinCount())
	}
	// A second equivalent intent is a cache hit (pin reused).
	if _, err := mvr.RouteIntent(context.Background(), "build a wasm module from beta.rs", "cli"); err != nil {
		t.Fatalf("route2: %v", err)
	}
	if mvr.Affinity.PinCount() != 1 {
		t.Fatalf("equivalent intent should reuse the pin, got %d pins", mvr.Affinity.PinCount())
	}
}

func TestAffinity_StatsCounters(t *testing.T) {
	a := NewAffinityRouter(2000)
	fresh := func() string { return "sir_codex" }

	a.SelectKnight("compile a.rs", fresh) // fresh pick (pin)
	a.SelectKnight("compile b.rs", fresh) // cache hit (same <FILE> key)
	a.RecordTTFT("sir_codex", 3500)       // make it a hotspot
	a.RecordTTFT("sir_helios", 100)       // cool alternate
	a.SelectKnight("compile c.rs", fresh) // escape -> sir_helios

	s := a.Stats()
	if s.FreshPicks != 1 || s.CacheHits != 1 || s.Escapes != 1 {
		t.Fatalf("counters = fresh%d hit%d esc%d, want 1/1/1", s.FreshPicks, s.CacheHits, s.Escapes)
	}
	if s.Routes != 3 {
		t.Fatalf("routes = %d, want 3", s.Routes)
	}
	if s.CacheHitPct < 33.0 || s.CacheHitPct > 34.0 {
		t.Fatalf("cache hit pct = %.1f, want ~33.3", s.CacheHitPct)
	}
	if s.AvgTTFT["sir_codex"] != 3500 {
		t.Fatalf("avg ttft codex = %v", s.AvgTTFT["sir_codex"])
	}
}
