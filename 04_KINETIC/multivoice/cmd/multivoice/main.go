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

	"camelot-os/orchestration"
	"camelot-os/vault"
	"camelot-os/zeroclaw"
)

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
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

	// 2. Initialize the ZeroClaw IPC arena.
	arenaMB, _ := strconv.Atoi(env("CAMELOT_ARENA_MB", "128"))
	if err := zeroclaw.InitializeArena(arenaMB); err != nil {
		log.Fatalf("[FATAL] ZeroClaw arena allocation failed: %v", err)
	}
	defer zeroclaw.PurgeAll()

	// 3. Boot the Polyglot Matrix (APEE v6) — swap in real providers here.
	polyglot := orchestration.NewAPEEv6Router()

	// 4. Ignite the Multivoice-Router.
	mvr := &orchestration.MultivoiceRouter{
		PolyglotEngine: polyglot,
		EcosystemDB:    ledger,
		Emit:           func(resp string) { log.Printf("[BIFROST] %s", resp) },
	}

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
