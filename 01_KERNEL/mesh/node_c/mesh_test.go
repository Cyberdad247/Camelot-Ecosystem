// SPDX-License-Identifier: MIT

package main

import (
	"context"
	"fmt"
	"io"
	"os"
	"strings"
	"testing"
	"time"
)

// TestTwoNodeMesh brings up two ephemeral tsnet nodes on the same tailnet and
// verifies node B can reach node A's /health endpoint over the mesh (P4-T01).
//
// Requires TS_AUTHKEY — a reusable, ephemeral Tailscale auth key. Without it the
// test is SKIPPED so environments with no tailnet stay green:
//
//	TS_AUTHKEY=tskey-... go test -v -run TestTwoNodeMesh
func TestTwoNodeMesh(t *testing.T) {
	authKey := os.Getenv("TS_AUTHKEY")
	if authKey == "" {
		t.Skip("TS_AUTHKEY not set — skipping live tsnet 2-node mesh test")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

	dirA, _ := os.MkdirTemp("", "tsnet-a-")
	dirB, _ := os.MkdirTemp("", "tsnet-b-")
	a := newNode("node-c-a", authKey, dirA)
	defer a.Close()
	b := newNode("node-c-b", authKey, dirB)
	defer b.Close()

	ipA, err := serveHealth(ctx, a)
	if err != nil {
		t.Fatalf("node A failed to come up: %v", err)
	}
	if _, err := b.Up(ctx); err != nil {
		t.Fatalf("node B failed to come up: %v", err)
	}

	// Node B dials node A over the tailnet (mesh-only; no public route).
	client := b.HTTPClient()
	url := fmt.Sprintf("http://%s:80/health", ipA)

	var body string
	var status int
	deadline := time.Now().Add(60 * time.Second)
	for time.Now().Before(deadline) {
		resp, err := client.Get(url)
		if err == nil {
			bs, _ := io.ReadAll(resp.Body)
			resp.Body.Close()
			body, status = string(bs), resp.StatusCode
			if status == 200 {
				break
			}
		}
		time.Sleep(time.Second)
	}

	if status != 200 || !strings.Contains(body, "CAMELOT-MESH-OK") {
		t.Fatalf("node B could not reach node A over tsnet mesh; status=%d body=%q", status, body)
	}
	t.Logf("two-node tsnet mesh OK: B reached A at %s (%q)", ipA, body)
}
