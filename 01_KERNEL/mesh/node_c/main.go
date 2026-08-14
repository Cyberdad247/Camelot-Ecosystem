// SPDX-License-Identifier: MIT

// Package main runs a CAMELOT Empire mesh node over Tailscale tsnet (P4-T01).
//
// Node_C_Omni_Router joins the tailnet with zero open ports and serves a
// /health endpoint reachable only over the mesh. Two nodes sharing a tailnet
// (same reusable TS_AUTHKEY) can reach each other by tailnet IP — see
// mesh_test.go::TestTwoNodeMesh.
//
//	go mod tidy                          # fetch tailscale.com (needs network)
//	TS_AUTHKEY=tskey-... go run . -hostname node-c-a
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"tailscale.com/tsnet"
)

// newNode constructs an ephemeral tsnet node (auto-removed from the tailnet on
// Close) with state isolated to dir.
func newNode(hostname, authKey, dir string) *tsnet.Server {
	return &tsnet.Server{
		Hostname:  hostname,
		AuthKey:   authKey,
		Dir:       dir,
		Ephemeral: true,
	}
}

// serveHealth brings the node up on the tailnet and serves /health on :80.
// Returns the node's tailnet IPv4 address.
func serveHealth(ctx context.Context, s *tsnet.Server) (string, error) {
	ln, err := s.Listen("tcp", ":80")
	if err != nil {
		return "", err
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "CAMELOT-MESH-OK %s", s.Hostname)
	})
	go func() { _ = http.Serve(ln, mux) }()

	st, err := s.Up(ctx)
	if err != nil {
		return "", err
	}
	if len(st.TailscaleIPs) == 0 {
		return "", fmt.Errorf("node %s has no tailscale IP", s.Hostname)
	}
	return st.TailscaleIPs[0].String(), nil
}

func main() {
	host := flag.String("hostname", "node-c", "tailnet hostname")
	flag.Parse()

	authKey := os.Getenv("TS_AUTHKEY")
	if authKey == "" {
		log.Fatal("TS_AUTHKEY required (a reusable, ephemeral Tailscale auth key)")
	}
	dir, err := os.MkdirTemp("", "tsnet-"+*host+"-")
	if err != nil {
		log.Fatalf("state dir: %v", err)
	}
	s := newNode(*host, authKey, dir)
	defer s.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	ip, err := serveHealth(ctx, s)
	if err != nil {
		log.Fatalf("node up failed: %v", err)
	}
	fmt.Printf("node %s up at %s:80/health (mesh-only)\n", *host, ip)
	select {} // serve until terminated
}
