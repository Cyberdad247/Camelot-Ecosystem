package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

// ── fake OpenAI-compatible SSE provider for tests ───────────────────────

type fakeProviderSpec struct {
	deltas     []string
	perDelta   time.Duration
	preDelay   time.Duration
	malformed  bool
	statusCode int
}

func fakeProviderServer(t *testing.T, spec fakeProviderSpec) *httptest.Server {
	t.Helper()
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if spec.statusCode != 0 {
			w.WriteHeader(spec.statusCode)
			return
		}
		w.Header().Set("Content-Type", "text/event-stream")
		flusher := w.(http.Flusher)
		if spec.preDelay > 0 {
			select {
			case <-time.After(spec.preDelay):
			case <-r.Context().Done():
				return
			}
		}
		if spec.malformed {
			fmt.Fprint(w, "this is not SSE at all\n")
			flusher.Flush()
			return
		}
		for _, d := range spec.deltas {
			select {
			case <-time.After(spec.perDelta):
			case <-r.Context().Done():
				return
			}
			payload, _ := json.Marshal(map[string]any{
				"choices": []map[string]any{{"delta": map[string]string{"content": d}}},
			})
			fmt.Fprintf(w, "data: %s\n\n", payload)
			flusher.Flush()
		}
		fmt.Fprint(w, "data: [DONE]\n\n")
		flusher.Flush()
	}))
	t.Cleanup(ts.Close)
	return ts
}

func routerWith(url string, timeout time.Duration) *ModelRouter {
	return NewModelRouterFromConfig(time.Millisecond, ModelConfig{
		Enabled: true,
		Allow:   []string{"deterministic", "testprov"},
		Name:    "testprov",
		URL:     url,
		Model:   "test-model",
		APIKey:  "sk-secret-shhh",
		Timeout: timeout,
	})
}

// drain collects session events until reply.done, turn.cancelled, or timeout.
func drain(t *testing.T, events chan SessionEvent, wait time.Duration) []SessionEvent {
	t.Helper()
	var collected []SessionEvent
	deadline := time.After(wait)
	for {
		select {
		case e := <-events:
			collected = append(collected, e)
			if e.Type == "reply.done" || e.Type == "turn.cancelled" {
				return collected
			}
		case <-deadline:
			return collected
		}
	}
}

func replyText(events []SessionEvent) string {
	var b strings.Builder
	for _, e := range events {
		if e.Type == "reply.chunk" {
			b.WriteString(e.Text)
		}
	}
	return b.String()
}

// 1. Default deterministic provider works without any external configuration.
func TestDeterministicProviderIsDefault(t *testing.T) {
	server, ts := newTestServer(t)
	events, unsub := server.sessions.Subscribe("sess-anya-demo-001")
	defer unsub()

	_, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m1", "read staging status"))
	if res.Reply.Text == "" {
		t.Fatal("deterministic primary must return sync reply text")
	}
	collected := drain(t, events, 3*time.Second)
	if !strings.Contains(replyText(collected), "Staging is green") {
		t.Fatalf("deterministic narration missing: %q", replyText(collected))
	}
	stats := server.models.Stats()
	if stats.Provider != "deterministic" || stats.Requests != 1 || stats.Fallbacks != 0 {
		t.Fatalf("stats %+v", stats)
	}
}

// 2. A configured provider that is NOT enabled is never selected.
func TestDisabledConfiguredProviderNotSelected(t *testing.T) {
	router := NewModelRouterFromConfig(time.Millisecond, ModelConfig{
		Enabled: false, // flag off
		Allow:   []string{"deterministic", "testprov"},
		Name:    "testprov",
		URL:     "http://localhost:1", // would fail if ever used
	})
	if !router.PrimaryIsDeterministic() {
		t.Fatal("disabled provider was selected")
	}
	// Allow-list also gates selection even when enabled.
	router = NewModelRouterFromConfig(time.Millisecond, ModelConfig{
		Enabled: true,
		Allow:   []string{"deterministic"}, // testprov absent
		Name:    "testprov",
		URL:     "http://localhost:1",
	})
	if !router.PrimaryIsDeterministic() {
		t.Fatal("non-allow-listed provider was selected")
	}
}

// 3. Provider timeout falls back to the deterministic reply, typed + audited.
func TestProviderTimeoutFallsBack(t *testing.T) {
	slow := fakeProviderServer(t, fakeProviderSpec{preDelay: 5 * time.Second})
	server, ts := newTestServer(t)
	server.models = routerWith(slow.URL, 150*time.Millisecond)

	events, unsub := server.sessions.Subscribe("sess-anya-demo-001")
	defer unsub()
	_, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m3", "read staging status"))
	if res.Reply.Text != "" {
		t.Fatal("configured primary must not fake a sync reply")
	}

	collected := drain(t, events, 5*time.Second)
	if !strings.Contains(replyText(collected), "Staging is green") {
		t.Fatalf("fallback text missing: %q", replyText(collected))
	}
	var sawFallbackRoute bool
	for _, e := range collected {
		if e.Type == "model.route" && e.Fallback && e.Provider == "deterministic" {
			sawFallbackRoute = true
		}
	}
	if !sawFallbackRoute {
		t.Fatal("no fallback model.route event")
	}
	if server.models.Stats().Fallbacks != 1 {
		t.Fatalf("fallback count %d", server.models.Stats().Fallbacks)
	}
}

// 4. A malformed stream fails safely into the deterministic fallback.
func TestMalformedStreamFallsBack(t *testing.T) {
	bad := fakeProviderServer(t, fakeProviderSpec{malformed: true})
	server, ts := newTestServer(t)
	server.models = routerWith(bad.URL, 2*time.Second)

	events, unsub := server.sessions.Subscribe("sess-anya-demo-001")
	defer unsub()
	postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m4", "read staging status"))

	collected := drain(t, events, 5*time.Second)
	if !strings.Contains(replyText(collected), "Staging is green") {
		t.Fatalf("fallback text missing after malformed stream: %q", replyText(collected))
	}

	// The audit chain records the typed failure, without secrets.
	found := false
	for i := 1; i <= server.audit.Len(); i++ {
		event, _ := server.audit.Get(fmt.Sprintf("audit-%04d", i))
		if event.Kind == "model.route" && strings.Contains(event.RedactedSummary, "malformed_stream") {
			found = true
		}
	}
	if !found {
		t.Fatal("malformed_stream failure not audited")
	}
}

// 5. Barge-in cancels active generation: no reply.done, turn.cancelled emitted.
func TestBargeInCancelsActiveGeneration(t *testing.T) {
	slow := fakeProviderServer(t, fakeProviderSpec{
		deltas:   []string{"Thinking ", "about ", "the ", "deployment ", "review ", "carefully ", "and ", "slowly."},
		perDelta: 120 * time.Millisecond,
	})
	server, ts := newTestServer(t)
	server.models = routerWith(slow.URL, 30*time.Second)

	events, unsub := server.sessions.Subscribe("sess-anya-demo-001")
	defer unsub()
	postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m5", "read staging status"))

	// Wait for generation to start streaming.
	deadline := time.After(5 * time.Second)
	for started := false; !started; {
		select {
		case e := <-events:
			if e.Type == "reply.chunk" {
				started = true
			}
		case <-deadline:
			t.Fatal("generation never started")
		}
	}

	status, barge := postJSON[BargeInResponse](t, ts.URL+"/v1/voice/barge-in", VoiceBargeIn{
		SessionID: "sess-anya-demo-001", TurnID: "turn-m5", AtMs: 1, Reason: "mock",
	})
	if status != 200 || barge.CancelledTurnID != "turn-m5" {
		t.Fatalf("barge-in failed: %d %+v", status, barge)
	}

	collected := drain(t, events, 3*time.Second)
	for _, e := range collected {
		if e.Type == "reply.done" {
			t.Fatal("generation completed despite barge-in")
		}
	}
	sawCancelled := false
	for _, e := range collected {
		if e.Type == "turn.cancelled" && e.TurnID == "turn-m5" {
			sawCancelled = true
		}
	}
	if !sawCancelled {
		t.Fatal("turn.cancelled missing after barge-in during generation")
	}
}

// 6. A model-proposed unknown skill is denied and audited; a known one is
// recorded as a proposal and NEVER executed.
func TestModelPlanProposals(t *testing.T) {
	prov := fakeProviderServer(t, fakeProviderSpec{
		deltas:   []string{"Here is my answer.\n", `PLAN {"skillId":"filesystem.rm_rf"}`},
		perDelta: time.Millisecond,
	})
	server, ts := newTestServer(t)
	server.models = routerWith(prov.URL, 5*time.Second)

	events, unsub := server.sessions.Subscribe("sess-anya-demo-001")
	defer unsub()
	postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m6", "read staging status"))
	collected := drain(t, events, 5*time.Second)

	// The PLAN directive is never rendered/spoken.
	if strings.Contains(replyText(collected), "PLAN") {
		t.Fatalf("plan directive leaked into reply: %q", replyText(collected))
	}
	denied := false
	for i := 1; i <= server.audit.Len(); i++ {
		event, _ := server.audit.Get(fmt.Sprintf("audit-%04d", i))
		if event.Kind == "model.plan.denied" && strings.Contains(event.RedactedSummary, "filesystem.rm_rf") {
			denied = true
		}
	}
	if !denied {
		t.Fatal("unknown skill proposal was not denied+audited")
	}
	if got := server.models.Stats(); got.PlanDenials != 1 {
		t.Fatalf("denial not counted: %+v", got)
	}

	// Known-skill proposal: recorded, not executed (no lease was consumed).
	// (Fresh router below — stats are per-router.)
	prov2 := fakeProviderServer(t, fakeProviderSpec{
		deltas:   []string{"Consider preparing a review.\n", `PLAN {"skillId":"deployment.review.prepare"}`},
		perDelta: time.Millisecond,
	})
	server.models = routerWith(prov2.URL, 5*time.Second)
	events2, unsub2 := server.sessions.Subscribe("sess-anya-demo-001")
	defer unsub2()
	postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m7", "read staging status"))
	drain(t, events2, 5*time.Second)

	proposed := false
	for i := 1; i <= server.audit.Len(); i++ {
		event, _ := server.audit.Get(fmt.Sprintf("audit-%04d", i))
		if event.Kind == "model.plan.proposed" && strings.Contains(event.RedactedSummary, "deployment.review.prepare") {
			proposed = true
			if !strings.Contains(event.RedactedSummary, "recorded only") {
				t.Fatal("proposal audit must state it was not executed")
			}
		}
	}
	if !proposed {
		t.Fatal("valid proposal not recorded")
	}
	if got := server.models.Stats(); got.PlanProposals != 1 {
		t.Fatalf("proposal not counted: %+v", got)
	}
}

// 7. Tier-3 actions still require user confirmation with a model enabled.
func TestTier3StillRequiresConfirmationWithModel(t *testing.T) {
	prov := fakeProviderServer(t, fakeProviderSpec{deltas: []string{"ok"}, perDelta: time.Millisecond})
	server, ts := newTestServer(t)
	server.models = routerWith(prov.URL, 5*time.Second)

	_, res := postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m8", "create a change request to scale the api tier"))
	if res.Decision.Effect != "requires_confirmation" || res.UIState != "blocked" {
		t.Fatalf("model routing must not bypass tier-3 confirmation: %+v", res.Decision)
	}
	if res.Artifact != nil {
		t.Fatal("nothing may execute before confirmation, model or not")
	}
	_ = server
}

// 8. Audit records route and fallback WITHOUT provider secrets.
func TestAuditRecordsRouteWithoutSecrets(t *testing.T) {
	bad := fakeProviderServer(t, fakeProviderSpec{statusCode: 500})
	server, ts := newTestServer(t)
	server.models = routerWith(bad.URL, 2*time.Second)

	events, unsub := server.sessions.Subscribe("sess-anya-demo-001")
	defer unsub()
	postJSON[CamelotTurnResponse](t, ts.URL+"/v1/voice/turns", turnBody("turn-m9", "read staging status"))
	drain(t, events, 5*time.Second)

	for i := 1; i <= server.audit.Len(); i++ {
		event, _ := server.audit.Get(fmt.Sprintf("audit-%04d", i))
		payload, _ := json.Marshal(event)
		if strings.Contains(string(payload), "sk-secret-shhh") {
			t.Fatalf("provider API key leaked into audit: %s", payload)
		}
	}
	if server.audit.VerifyChain() != -1 {
		t.Fatal("audit chain broken")
	}
	if server.models.Stats().Fallbacks != 1 {
		t.Fatalf("fallback not counted: %+v", server.models.Stats())
	}
}
