package providers

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

// A mock OpenAI server lets us exercise the real HTTP round-trip (request shape,
// auth header, model, response parsing) with no real key and no network.
func mockOpenAI(t *testing.T, wantAuth string) *httptest.Server {
	t.Helper()
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if got := r.Header.Get("Authorization"); got != wantAuth {
			t.Errorf("auth header = %q, want %q", got, wantAuth)
		}
		var body struct {
			Model    string `json:"model"`
			Messages []struct {
				Role    string `json:"role"`
				Content string `json:"content"`
			} `json:"messages"`
		}
		b, _ := io.ReadAll(r.Body)
		_ = json.Unmarshal(b, &body)
		if body.Model != "gpt-4o" {
			t.Errorf("model = %q, want gpt-4o", body.Model)
		}
		if len(body.Messages) < 2 || !strings.Contains(body.Messages[0].Content, "SIR_CODEX") {
			t.Errorf("system message missing SIR_CODEX: %+v", body.Messages)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"choices":[{"message":{"role":"assistant","content":"fn main() {}"}}]}`))
	}))
}

func newTestProvider(url string) *OpenAIProvider {
	return &OpenAIProvider{
		APIKey:  "test-key",
		Model:   "gpt-4o",
		BaseURL: url,
		Client:  &http.Client{Timeout: 5 * time.Second},
	}
}

func TestOpenAIProvider_InvokeRoundTrip(t *testing.T) {
	srv := mockOpenAI(t, "Bearer test-key")
	defer srv.Close()

	p := newTestProvider(srv.URL)
	out, err := p.Invoke(context.Background(), "sir_codex", "build a wasm module", "wasm.compile|cargo")
	if err != nil {
		t.Fatalf("invoke: %v", err)
	}
	if out != "fn main() {}" {
		t.Fatalf("content = %q, want the mocked completion", out)
	}
	if p.Name() != "OpenAI" {
		t.Fatalf("name = %q", p.Name())
	}
}

func TestOpenAIProvider_HTTPError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		http.Error(w, `{"error":"rate_limited"}`, http.StatusTooManyRequests)
	}))
	defer srv.Close()

	_, err := newTestProvider(srv.URL).Invoke(context.Background(), "sir_codex", "x", "")
	if err == nil || !strings.Contains(err.Error(), "HTTP 429") {
		t.Fatalf("expected HTTP 429 error, got: %v", err)
	}
}

func TestNewOpenAIProvider_RequiresKey(t *testing.T) {
	t.Setenv("CAMELOT_OPENAI_KEY", "")
	if _, err := NewOpenAIProvider(); err == nil {
		t.Fatal("expected error when CAMELOT_OPENAI_KEY is unset (Sentinel Shield)")
	}
	t.Setenv("CAMELOT_OPENAI_KEY", "sk-live-xxxx")
	p, err := NewOpenAIProvider()
	if err != nil {
		t.Fatalf("construct with key: %v", err)
	}
	if p.Model != "gpt-4o" || p.BaseURL == "" {
		t.Fatalf("defaults not applied: %+v", p)
	}
}

// Compile-time proof the provider satisfies the structural Provider contract
// (Name + Invoke) that orchestration.NewAPEEv6RouterWith expects.
var _ interface {
	Name() string
	Invoke(ctx context.Context, knight, intent, skills string) (string, error)
} = (*OpenAIProvider)(nil)
