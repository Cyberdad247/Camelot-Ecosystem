package providers

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

// mockCLIProxy stands in for the local Bifrost/CLIProxy gateway: it answers the
// OpenAI-compatible /chat/completions and /models endpoints with no real key.
func mockCLIProxy(t *testing.T) *httptest.Server {
	t.Helper()
	mux := http.NewServeMux()
	mux.HandleFunc("/v1/models", func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte(`{"data":[{"id":"gpt-4o"},{"id":"gemini-2.5-flash"},{"id":"claude-sonnet-4-6"}]}`))
	})
	mux.HandleFunc("/v1/chat/completions", func(w http.ResponseWriter, r *http.Request) {
		if got := r.Header.Get("Authorization"); got != "Bearer proxy-admin-key" {
			t.Errorf("auth = %q, want the local proxy key", got)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"choices":[{"message":{"role":"assistant","content":"OK"}}]}`))
	})
	return httptest.NewServer(mux)
}

func TestGateway_ZeroCostRoundTrip(t *testing.T) {
	srv := mockCLIProxy(t)
	defer srv.Close()
	t.Setenv("CLIPROXY_BASE", srv.URL+"/v1")
	// CLIPROXY_KEY default is "proxy-admin-key" (a loopback key, not a paid one).

	if !GatewayReachable(2 * time.Second) {
		t.Fatal("expected gateway reachable via /models")
	}
	p := NewGatewayProvider("Bifrost:codex", "gpt-4o")
	if !strings.HasPrefix(p.BaseURL, srv.URL) {
		t.Fatalf("provider base = %q, want gateway", p.BaseURL)
	}
	if p.Name() != "Bifrost:codex" {
		t.Fatalf("label = %q", p.Name())
	}
	out, err := p.Invoke(context.Background(), "sir_codex", "build wasm", "wasm.compile")
	if err != nil {
		t.Fatalf("invoke: %v", err)
	}
	if out != "OK" {
		t.Fatalf("content = %q", out)
	}
}

func TestGateway_UnreachableDegrades(t *testing.T) {
	t.Setenv("CLIPROXY_BASE", "http://127.0.0.1:1/v1") // nothing listens here
	if GatewayReachable(300 * time.Millisecond) {
		t.Fatal("expected gateway unreachable")
	}
	// The local stub is the graceful fallback — offline, deterministic, no error.
	stub := NewLocalStubProvider("SIR_BORIS")
	out, err := stub.Invoke(context.Background(), "sir_boris", "audit security", "")
	if err != nil {
		t.Fatalf("stub invoke: %v", err)
	}
	if !strings.Contains(out, "LocalTinyLM") || !strings.Contains(out, "gateway offline") {
		t.Fatalf("unexpected stub output: %q", out)
	}
}

// mockOpenAICompat stands in for the local OpenAI-compatible tier — the same
// shape as openai-oauth's dev proxy (127.0.0.1:10531/v1) or a LiteRT-LM OpenAI
// server. It answers /models and /chat/completions with no real credential.
func mockOpenAICompat(t *testing.T) *httptest.Server {
	t.Helper()
	mux := http.NewServeMux()
	mux.HandleFunc("/v1/models", func(w http.ResponseWriter, _ *http.Request) {
		_, _ = w.Write([]byte(`{"data":[{"id":"gpt-4o"},{"id":"gemma-4-E4B"}]}`))
	})
	mux.HandleFunc("/v1/chat/completions", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"choices":[{"message":{"role":"assistant","content":"LOCAL_OK"}}]}`))
	})
	return httptest.NewServer(mux)
}

func TestOpenAICompat_RoundTrip(t *testing.T) {
	srv := mockOpenAICompat(t)
	defer srv.Close()
	t.Setenv("OPENAI_COMPAT_BASE", srv.URL+"/v1")

	if !OpenAICompatReachable(2 * time.Second) {
		t.Fatal("expected local OpenAI-compatible endpoint reachable via /models")
	}
	p := NewOpenAICompatProvider("Bifrost:codex:local", "gpt-4o")
	if !strings.HasPrefix(p.BaseURL, srv.URL) {
		t.Fatalf("provider base = %q, want local endpoint", p.BaseURL)
	}
	out, err := p.Invoke(context.Background(), "sir_codex", "run local", "")
	if err != nil {
		t.Fatalf("invoke: %v", err)
	}
	if out != "LOCAL_OK" {
		t.Fatalf("content = %q", out)
	}
}

func TestOpenAICompat_Unreachable(t *testing.T) {
	t.Setenv("OPENAI_COMPAT_BASE", "http://127.0.0.1:1/v1") // nothing listens here
	if OpenAICompatReachable(300 * time.Millisecond) {
		t.Fatal("expected local endpoint unreachable")
	}
}

// The gateway provider and the local stub both satisfy the structural Provider
// contract that orchestration.NewAPEEv6RouterWith expects.
var (
	_ interface {
		Name() string
		Invoke(ctx context.Context, knight, intent, skills string) (string, error)
	} = (*OpenAIProvider)(nil)
	_ interface {
		Name() string
		Invoke(ctx context.Context, knight, intent, skills string) (string, error)
	} = (*LocalStubProvider)(nil)
)
