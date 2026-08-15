// Command multivoice ignites the Cybertronia Digital Factory: it mounts the
// World Tree skill registry, initializes the ZeroClaw arena, boots the Polyglot
// Matrix, and serves Sovereign Intent over a Unix socket (CLI) and HTTP/SSE
// (voice / WebMCP).
//
// Paths are environment-configurable (no hardcoded production paths):
//
//	CAMELOT_WORLD_TREE   world tree ledger path   (default: ./world_tree.db)
//	CAMELOT_MV_SOCK      unix socket path         (default: ./camelot_multivoice.sock)
//	CAMELOT_MV_SSE       SSE bind address         (default: :7680)
//	CAMELOT_ARENA_MB     ZeroClaw arena ceiling   (default: 128)
package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"strconv"
	"syscall"
	"time"

	"camelot-os/orchestration"
	"camelot-os/orchestration/filtration"
	"camelot-os/providers"
	"camelot-os/vault"
	"camelot-os/zeroclaw"
)

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

// buildPolyglot synchronizes the Knight Pantheon with ZERO-COST LLM engines via
// the Bifrost / CLIProxy gateway (free models over CLI OAuth — no paid keys, no
// per-token billing). Each Knight binds to a free model; if the gateway is down
// the Knight degrades gracefully to the local TinyLM stub (Kinetic Resilience).
//
//	SIR_CODEX  -> openai slot -> gpt-4o            (CAMELOT_MODEL_CODEX)
//	SIR_HELIOS -> gemini slot -> gemini-2.5-flash  (CAMELOT_MODEL_HELIOS)
//	SIR_BORIS  -> claude slot -> claude-sonnet-4-6 (CAMELOT_MODEL_BORIS)
func buildPolyglot() *orchestration.APEEv6Router {
	live := providers.GatewayReachable(800 * time.Millisecond)
	// Local OpenAI-compatible tier (Phase 1 integration): openai-oauth dev
	// proxy (127.0.0.1:10531/v1) or a LiteRT-LM OpenAI server. Gateway offline
	// + local endpoint up → route locally instead of degrading to the stub.
	local := false
	if live {
		log.Printf("[CYBERTRONIA] Bifrost/CLIProxy gateway online (%s) — zero-cost routing.", providers.GatewayBase())
	} else {
		if env("CAMELOT_REQUIRE_GATEWAY", "0") == "1" {
			log.Fatalf("[FATAL] gateway unavailable and CAMELOT_REQUIRE_GATEWAY=1")
		}
		local = providers.OpenAICompatReachable(800 * time.Millisecond)
		if local {
			log.Printf("[CYBERTRONIA] gateway offline — local OpenAI-compatible endpoint online (%s).", providers.OpenAICompatBase())
		} else {
			log.Printf("[CYBERTRONIA] gateway offline — Knights degrade to local TinyLM stubs.")
		}
	}

	bind := func(label, modelEnv, modelDefault, knight string) orchestration.Provider {
		if live {
			return providers.NewGatewayProvider(label, env(modelEnv, modelDefault))
		}
		if local {
			return providers.NewOpenAICompatProvider(label+":local", env(modelEnv, modelDefault))
		}
		return providers.NewLocalStubProvider(knight)
	}

	provs := map[string]orchestration.Provider{
		"openai": bind("Bifrost:codex", "CAMELOT_MODEL_CODEX", "gpt-4o", "SIR_CODEX"),
		"gemini": bind("Bifrost:helios", "CAMELOT_MODEL_HELIOS", "gemini-2.5-flash", "SIR_HELIOS"),
		"claude": bind("Bifrost:boris", "CAMELOT_MODEL_BORIS", "claude-sonnet-4-6", "SIR_BORIS"),
	}
	log.Printf("[CYBERTRONIA] Polyglot Matrix synchronized: SIR_CODEX, SIR_HELIOS, SIR_BORIS.")
	return orchestration.NewAPEEv6RouterWith(provs)
}

func main() {
	log.Println("[CYBERTRONIA] Initiating Factory Ignition Sequence...")

	// 1. Mount the World Tree (Camelot-Ecosystem VSS index).
	ledger, err := vault.MountLedger(env("CAMELOT_WORLD_TREE", "./world_tree.db"))
	if err != nil {
		log.Fatalf("[FATAL] Failed to mount World Tree: %v", err)
	}
	defer ledger.Seal()
	log.Printf("[CYBERTRONIA] World Tree mounted (%d skills indexed).", ledger.Len())

	// Initialize and verify Inference Filtration Layer DAG (Kinetic Grounding Mandate)
	log.Println("[CYBERTRONIA] Initializing Inference Filtration Layer...")
	plan, err := filtration.ExecuteFiltrationDAG("hf://meta-llama/Meta-Llama-3-8B-Instruct", 8192)
	if err != nil {
		log.Printf("[WARNING] Filtration DAG initial smoke check failed: %v", err)
	} else {
		log.Printf("[CYBERTRONIA] Filtration DAG active. Deployment plan generated: %+v", plan)
	}

	// 2. Initialize the ZeroClaw IPC arena.
	arenaMB, _ := strconv.Atoi(env("CAMELOT_ARENA_MB", "128"))
	if err := zeroclaw.InitializeArena(arenaMB); err != nil {
		log.Fatalf("[FATAL] ZeroClaw arena allocation failed: %v", err)
	}
	defer zeroclaw.PurgeAll()

	// 3. Boot the Polyglot Matrix (APEE v6) — live providers where keys exist.
	polyglot := buildPolyglot()

	// 4. Ignite the Multivoice-Router with the OmniRoute affinity layer
	//    (sticky KV-cache pinning + DualMap-lite SLO escape; CAMELOT_SLO_MS).
	sloMs, _ := strconv.ParseFloat(env("CAMELOT_SLO_MS", "2000"), 64)
	mvr := &orchestration.MultivoiceRouter{
		PolyglotEngine: polyglot,
		EcosystemDB:    ledger,
		Affinity:       orchestration.NewAffinityRouter(sloMs),
		Emit:           func(resp string) { log.Printf("[BIFROST] %s", resp) },
	}
	log.Printf("[CYBERTRONIA] OmniRoute affinity layer active (SLO %.0fms).", sloMs)

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	// 5. Bind ingress channels.
	sock := env("CAMELOT_MV_SOCK", "./camelot_multivoice.sock")
	_ = os.Remove(sock) // clear a stale socket
	go func() {
		if err := mvr.ListenUnixSocket(ctx, sock); err != nil {
			log.Printf("[CYBERTRONIA] unix listener: %v", err)
		}
	}()
	go func() {
		if err := mvr.ListenSSE(ctx, env("CAMELOT_MV_SSE", ":7680")); err != nil {
			log.Printf("[CYBERTRONIA] sse listener: %v", err)
		}
	}()

	log.Println("[CYBERTRONIA] Multivoice-Router Online. Ecosystem VSS Active.")
	log.Println("[CYBERTRONIA] Digital Factory awaiting Sovereign Intent.")

	<-ctx.Done()
	log.Println("[CYBERTRONIA] Shutting down. Purging ZeroClaw memory...")
}
