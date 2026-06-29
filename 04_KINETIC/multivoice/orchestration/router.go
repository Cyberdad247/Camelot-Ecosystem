package orchestration

import (
	"bufio"
	"context"
	"fmt"
	"net"
	"net/http"
	"strings"

	"camelot-os/vault"
	"camelot-os/zeroclaw"
)

// MultivoiceRouter is the parallelized Go switchboard: it intercepts intents,
// queries the World Tree for skills, loads them zero-copy into ZeroClaw, and
// dispatches through the Polyglot Matrix.
type MultivoiceRouter struct {
	PolyglotEngine *APEEv6Router
	EcosystemDB    *vault.Ledger
	// Emit, if set, receives each response (e.g. forward to the Bifrost board).
	Emit func(string)
}

// RouteIntent drives one intent end-to-end and returns the engine response.
func (mvr *MultivoiceRouter) RouteIntent(ctx context.Context, intent, source string) (string, error) {
	// 1. World Tree VSS — only the skills this intent needs.
	skills := mvr.EcosystemDB.VSSSearchSkills(intent, 3)

	// 2. Pack them zero-copy into the ZeroClaw arena (Scarcity-bounded).
	fd, err := zeroclaw.LoadEcosystemCartridges(skills)
	if err != nil {
		return "", fmt.Errorf("ecosystem load failure: %w", err)
	}
	defer zeroclaw.Purge(fd) // MADV_DONTNEED on exit

	// 3. Polyglot routing — the right Knight + the right engine.
	knight := mvr.PolyglotEngine.DetermineKnight(intent, skills)

	// 4. Dispatch.
	resp, err := mvr.PolyglotEngine.InvokeKnightWithSkills(ctx, knight, intent, fd)
	if err != nil {
		return "", err
	}
	if mvr.Emit != nil {
		mvr.Emit(resp)
	}
	return resp, nil
}

// ListenUnixSocket serves CLI intents over a Unix domain socket: each line is
// one intent; the response is written back. Blocks until ctx is cancelled.
func (mvr *MultivoiceRouter) ListenUnixSocket(ctx context.Context, path string) error {
	ln, err := net.Listen("unix", path)
	if err != nil {
		return fmt.Errorf("multivoice: unix listen %s: %w", path, err)
	}
	go func() { <-ctx.Done(); _ = ln.Close() }()
	for {
		conn, err := ln.Accept()
		if err != nil {
			return nil // listener closed
		}
		go mvr.serveConn(ctx, conn)
	}
}

func (mvr *MultivoiceRouter) serveConn(ctx context.Context, conn net.Conn) {
	defer conn.Close()
	sc := bufio.NewScanner(conn)
	for sc.Scan() {
		intent := strings.TrimSpace(sc.Text())
		if intent == "" {
			continue
		}
		resp, err := mvr.RouteIntent(ctx, intent, "cli")
		if err != nil {
			fmt.Fprintf(conn, "ERR %v\n", err)
			continue
		}
		fmt.Fprintf(conn, "%s\n", resp)
	}
}

// ListenSSE serves intents over HTTP: POST /intent (body = intent) routes and
// returns the response; GET /healthz is a liveness probe. Blocks until the
// server errors or ctx is cancelled.
func (mvr *MultivoiceRouter) ListenSSE(ctx context.Context, addr string) error {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		fmt.Fprintln(w, "MULTIVOICE OK")
	})
	mux.HandleFunc("/intent", func(w http.ResponseWriter, req *http.Request) {
		buf := new(strings.Builder)
		_, _ = bufioCopy(buf, req.Body)
		resp, err := mvr.RouteIntent(req.Context(), strings.TrimSpace(buf.String()), "webmcp")
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadGateway)
			return
		}
		w.Header().Set("Content-Type", "text/event-stream")
		fmt.Fprintf(w, "event: response\ndata: %s\n\n", resp)
	})
	srv := &http.Server{Addr: addr, Handler: mux}
	go func() { <-ctx.Done(); _ = srv.Close() }()
	return srv.ListenAndServe()
}

func bufioCopy(dst *strings.Builder, r interface{ Read([]byte) (int, error) }) (int, error) {
	total := 0
	b := make([]byte, 4096)
	for {
		n, err := r.Read(b)
		if n > 0 {
			dst.Write(b[:n])
			total += n
		}
		if err != nil {
			return total, nil
		}
	}
}
