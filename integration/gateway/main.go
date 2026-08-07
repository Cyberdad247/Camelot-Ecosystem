package main

import (
	"log"
	"net/http"
	"os"
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
	defer server.audit.Close()
	log.Printf("%s %s listening on %s (audit store: %s)", serviceName, serviceVersion, addr, dbPath)
	if err := http.ListenAndServe(addr, server.Handler()); err != nil {
		log.Fatal(err)
	}
}
