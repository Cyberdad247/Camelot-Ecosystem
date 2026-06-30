package main

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

// harnessHTML is the bundled SSE test client, served at "/" so it is
// same-origin with /events (no CORS handling required).
//
//go:embed harness.html
var harnessHTML []byte

// RuneResult is the canonical output of a rune evaluation. Kept identical to
// the original CLI contract so existing callers (and go_router.exe consumers)
// keep working unchanged.
type RuneResult struct {
	Rune      string                 `json:"rune"`
	Knight    string                 `json:"knight"`
	Directive string                 `json:"directive"`
	Mode      string                 `json:"mode"`
	Status    string                 `json:"status"`
	Metadata  map[string]interface{} `json:"metadata"`
}

// knightRoster maps the active knight reported in active_knight SSE events.
// These names line up with the avatar slots the 3D hub expects.
var knightRoster = []string{
	"anya", "merlin", "codex", "hashimoto", "boris", "helios",
}

// evaluateRune holds the original CLI logic in one place so both the CLI path
// and the HTTP path produce identical results.
func evaluateRune(runeName, taskName string) RuneResult {
	// SAT-gate validation simulation (Z3-gate)
	status := "SATISFIED"
	if runeName == "//MALICIOUS" {
		status = "UNSATISFIED"
	}

	return RuneResult{
		Rune:      runeName,
		Knight:    "sir_boris",
		Directive: runeName + " " + taskName,
		Mode:      "SWARM",
		Status:    status,
		Metadata: map[string]interface{}{
			"engine":             "v1000_go_router",
			"z3_verification_ms": 12,
		},
	}
}

// detectNode resolves which node this daemon is running on. CAMELOT_NODE wins;
// otherwise we fall back to the OS hostname.
func detectNode() string {
	if n := os.Getenv("CAMELOT_NODE"); n != "" {
		return n
	}
	h, err := os.Hostname()
	if err != nil {
		return "unknown"
	}
	return h
}

// sseEvent is one server-sent event: an event name plus a JSON payload.
type sseEvent struct {
	name string
	data []byte
}

// hub is a minimal SSE fan-out. Subscribers register a channel; Broadcast
// pushes an event to every live subscriber without blocking on slow ones.
type hub struct {
	mu   sync.Mutex
	subs map[chan sseEvent]struct{}
}

func newHub() *hub {
	return &hub{subs: make(map[chan sseEvent]struct{})}
}

func (h *hub) subscribe() chan sseEvent {
	ch := make(chan sseEvent, 16)
	h.mu.Lock()
	h.subs[ch] = struct{}{}
	h.mu.Unlock()
	return ch
}

func (h *hub) unsubscribe(ch chan sseEvent) {
	h.mu.Lock()
	delete(h.subs, ch)
	close(ch)
	h.mu.Unlock()
}

func (h *hub) broadcast(ev sseEvent) {
	h.mu.Lock()
	defer h.mu.Unlock()
	for ch := range h.subs {
		select {
		case ch <- ev:
		default:
			// Drop for a subscriber that can't keep up rather than stall the hub.
		}
	}
}

// activeKnightFor picks a deterministic knight for a rune so the 3D hub lights
// up a stable avatar per rune instead of flickering.
func activeKnightFor(runeName string) string {
	if runeName == "" {
		return knightRoster[0]
	}
	var sum int
	for _, r := range runeName {
		sum += int(r)
	}
	return knightRoster[sum%len(knightRoster)]
}

func mustJSON(v interface{}) []byte {
	b, err := json.Marshal(v)
	if err != nil {
		return []byte(`{"error":"marshal_failed"}`)
	}
	return b
}

func runServer(addr string) error {
	node := detectNode()
	h := newHub()

	mux := http.NewServeMux()

	// GET / — the bundled SSE harness. Exact-match only so it does not
	// swallow other routes.
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(harnessHTML)
	})

	// GET /healthz — node identity + liveness for the cluster.
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.Write(mustJSON(map[string]interface{}{
			"status": "ok",
			"node":   node,
			"engine": "v1000_go_router",
		}))
	})

	// POST /rune?rune=//FOO&task=bar — evaluate a rune, broadcast active_knight,
	// return the RuneResult. GET works too for easy testing.
	mux.HandleFunc("/rune", func(w http.ResponseWriter, r *http.Request) {
		runeName := r.URL.Query().Get("rune")
		taskName := r.URL.Query().Get("task")
		if runeName == "" {
			http.Error(w, `{"error":"missing rune"}`, http.StatusBadRequest)
			return
		}
		result := evaluateRune(runeName, taskName)
		knight := activeKnightFor(runeName)
		h.broadcast(sseEvent{
			name: "active_knight",
			data: mustJSON(map[string]interface{}{
				"knight": knight,
				"rune":   runeName,
				"status": result.Status,
				"node":   node,
				"ts":     time.Now().UTC().Format(time.RFC3339),
			}),
		})
		w.Header().Set("Content-Type", "application/json")
		w.Write(mustJSON(result))
	})

	// GET /events — SSE stream the 3D avatars subscribe to.
	mux.HandleFunc("/events", func(w http.ResponseWriter, r *http.Request) {
		flusher, ok := w.(http.Flusher)
		if !ok {
			http.Error(w, "streaming unsupported", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")

		ch := h.subscribe()
		defer h.unsubscribe(ch)

		// Greet the client with the node it's attached to.
		fmt.Fprintf(w, "event: node\ndata: %s\n\n",
			mustJSON(map[string]string{"node": node}))
		flusher.Flush()

		heartbeat := time.NewTicker(15 * time.Second)
		defer heartbeat.Stop()

		for {
			select {
			case <-r.Context().Done():
				return
			case ev := <-ch:
				fmt.Fprintf(w, "event: %s\ndata: %s\n\n", ev.name, ev.data)
				flusher.Flush()
			case <-heartbeat.C:
				fmt.Fprint(w, ": keep-alive\n\n")
				flusher.Flush()
			}
		}
	})

	log.Printf("[go_router] node=%s serving on %s (SSE: /events, rune: /rune)", node, addr)
	return http.ListenAndServe(addr, mux)
}

func main() {
	// Daemon mode: `go_router serve [addr]`. Preserves the original one-shot CLI
	// for every other invocation so existing callers are unaffected.
	if len(os.Args) >= 2 && os.Args[1] == "serve" {
		addr := ":8077"
		if len(os.Args) > 2 {
			addr = os.Args[2]
		}
		if err := runServer(addr); err != nil {
			log.Fatalf("[go_router] server error: %v", err)
		}
		return
	}

	if len(os.Args) < 2 {
		fmt.Println("Usage:")
		fmt.Println("  go_router <rune> <task>      one-shot rune evaluation")
		fmt.Println("  go_router serve [addr]       run SSE daemon (default :8077)")
		os.Exit(1)
	}

	runeName := os.Args[1]
	taskName := ""
	if len(os.Args) > 2 {
		taskName = os.Args[2]
	}

	result := evaluateRune(runeName, taskName)
	resBytes, _ := json.MarshalIndent(result, "", "  ")
	fmt.Println(string(resBytes))
}
