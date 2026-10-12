package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"
)

func main() {
	// LOOPBACK BY DEFAULT. ":8788" bound every interface, so on a
	// Tailscale-connected host the governed surface — including the tier-3
	// confirmation endpoint — was reachable from the whole tailnet. Widening
	// the bind is now an explicit, deliberate act.
	addr := os.Getenv("GATEWAY_ADDR")
	if addr == "" {
		addr = "127.0.0.1:8788"
	}
	// Local SQLite audit store (redacted, hash-chained). Set GATEWAY_DB to
	// relocate it, or GATEWAY_DB=:memory: for an ephemeral run.
	dbPath := os.Getenv("GATEWAY_DB")
	if dbPath == "" {
		dbPath = "camelot-voice.db"
	}
	server, err := NewPersistentServer(60*time.Millisecond, time.Now, dbPath)
	if err != nil {
		log.Fatal(err)
	}
	// Phase 4A: the node agent verifies gateway-minted node leases, so both
	// sides must share the signing key. Without this the gateway would sign
	// with a random per-process key and every node job would (correctly) be
	// rejected as forged. Set it once, out of band, for both processes.
	if key := os.Getenv("CAMELOT_NODE_LEASE_KEY"); key != "" {
		server.leases.SetSigningKey([]byte(key))
		log.Printf("lease signing key: loaded from CAMELOT_NODE_LEASE_KEY (shared with node agents)")
	} else {
		log.Printf("lease signing key: ephemeral (per-process); node-job dispatch requires CAMELOT_NODE_LEASE_KEY on both sides")
	}

	// P1: authentication. resolveAuthFromEnv cannot return an empty token —
	// an unset CAMELOT_API_TOKEN mints one rather than disabling the check, so
	// the binary is never reachable unauthenticated.
	authCfg, minted := resolveAuthFromEnv()
	server.SetAuth(authCfg)
	if minted {
		if err := writeTokenFile(authCfg.token); err != nil {
			log.Printf("api token: could not write token file: %v", err)
		}
		log.Printf("api token: MINTED for this process (set CAMELOT_API_TOKEN to pin one)")
	} else {
		log.Printf("api token: loaded from CAMELOT_API_TOKEN")
	}
	log.Printf("cors: allowed origins %v", authCfg.allowedOrigins)
	if !strings.HasPrefix(addr, "127.0.0.1:") && !strings.HasPrefix(addr, "localhost:") {
		log.Printf("WARNING: bound to %s — the governed surface is reachable beyond loopback", addr)
	}

	// Phase 3: model routing. Deterministic unless ENABLE_MODEL_PROVIDER=true
	// with an allow-listed, URL-configured provider (never auto-started).
	modelCfg := ModelConfigFromEnv()
	server.models = NewModelRouterFromConfig(60*time.Millisecond, modelCfg)
	log.Printf("model routing: provider=%s (configured enabled=%t)", server.models.Stats().Provider, modelCfg.Enabled)

	httpServer := &http.Server{Addr: addr, Handler: server.Handler()}
	errCh := make(chan error, 1)
	go func() { errCh <- httpServer.ListenAndServe() }()
	log.Printf("%s %s listening on %s (audit store: %s)", serviceName, serviceVersion, addr, dbPath)

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

	select {
	case sig := <-sigCh:
		log.Printf("received %s, shutting down", sig)
	case err := <-errCh:
		server.audit.Close()
		log.Fatal(err)
	}

	// Graceful drain: stop accepting, give in-flight requests 3s. Hijacked
	// WebSocket connections are closed by the context deadline expiring.
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	if err := httpServer.Shutdown(ctx); err != nil {
		log.Printf("shutdown: %v", err)
	}
	if err := server.audit.Close(); err != nil {
		log.Printf("audit close: %v", err)
	}
	log.Printf("graceful shutdown complete")
}

// writeTokenFile drops a minted token where local callers (smoke, the console
// static server, the node agent) can pick it up. 0600: the token is only as
// strong as the filesystem, and this at least keeps it off other users.
func writeTokenFile(token string) error {
	path := os.Getenv("CAMELOT_TOKEN_FILE")
	if path == "" {
		path = ".run/gateway.token"
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	return os.WriteFile(path, []byte(token+"\n"), 0o600)
}
