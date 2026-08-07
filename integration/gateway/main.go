package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	addr := os.Getenv("GATEWAY_ADDR")
	if addr == "" {
		addr = ":8788"
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
