package orchestration

import (
	"context"
	"strings"
	"testing"

	"camelot-os/vault"
	"camelot-os/zeroclaw"
)

func newRouter(t *testing.T) *MultivoiceRouter {
	t.Helper()
	led, err := vault.MountLedger("")
	if err != nil {
		t.Fatalf("mount: %v", err)
	}
	if err := zeroclaw.InitializeArena(16); err != nil {
		t.Fatalf("arena: %v", err)
	}
	return &MultivoiceRouter{PolyglotEngine: NewAPEEv6Router(), EcosystemDB: led}
}

func TestRouteIntent_CodeToCodex(t *testing.T) {
	mvr := newRouter(t)
	resp, err := mvr.RouteIntent(context.Background(), "build a wasm module in rust", "cli")
	if err != nil {
		t.Fatalf("route: %v", err)
	}
	if !strings.Contains(resp, "sir_codex") || !strings.Contains(resp, "OpenAI") {
		t.Fatalf("expected codex/OpenAI route, got: %s", resp)
	}
}

func TestRouteIntent_RagToHelios(t *testing.T) {
	mvr := newRouter(t)
	resp, err := mvr.RouteIntent(context.Background(), "architect a rag retrieval design", "cli")
	if err != nil {
		t.Fatalf("route: %v", err)
	}
	if !strings.Contains(resp, "sir_helios") || !strings.Contains(resp, "Gemini") {
		t.Fatalf("expected helios/Gemini route, got: %s", resp)
	}
}

func TestRouteIntent_SecurityToBoris(t *testing.T) {
	mvr := newRouter(t)
	resp, err := mvr.RouteIntent(context.Background(), "run a security fuzz audit", "cli")
	if err != nil {
		t.Fatalf("route: %v", err)
	}
	if !strings.Contains(resp, "sir_boris") || !strings.Contains(resp, "Claude") {
		t.Fatalf("expected boris/Claude route, got: %s", resp)
	}
}

func TestRouteIntent_SkillsInjected(t *testing.T) {
	mvr := newRouter(t)
	// "wasm" matches the wasm.compile skill -> skills should be packed + injected.
	resp, err := mvr.RouteIntent(context.Background(), "compile wasm", "cli")
	if err != nil {
		t.Fatalf("route: %v", err)
	}
	if !strings.Contains(resp, "+skills") {
		t.Fatalf("expected skills injected, got: %s", resp)
	}
}

func TestArena_ScarcityAndReclaim(t *testing.T) {
	led, _ := vault.MountLedger("")
	if err := zeroclaw.InitializeArena(16); err != nil {
		t.Fatalf("arena: %v", err)
	}
	skills := led.VSSSearchSkills("build wasm react security status", 5)
	fd, err := zeroclaw.LoadEcosystemCartridges(skills)
	if err != nil {
		t.Fatalf("load: %v", err)
	}
	if zeroclaw.Leased() == 0 {
		t.Fatal("expected non-zero arena lease after load")
	}
	zeroclaw.Purge(fd)
	if zeroclaw.Leased() != 0 {
		t.Fatalf("expected lease reclaimed, got %d", zeroclaw.Leased())
	}
}

func TestArena_NotInitialized(t *testing.T) {
	zeroclaw.PurgeAll()
	// A fresh arena with size 0 should reject loads until initialized.
	if err := zeroclaw.InitializeArena(0); err == nil {
		t.Fatal("expected error initializing zero-size arena")
	}
}
