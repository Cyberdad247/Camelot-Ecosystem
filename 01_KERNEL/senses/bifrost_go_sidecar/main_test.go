package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestExtractTokenFromHeadersPriority(t *testing.T) {
	headers := http.Header{}
	headers.Set("x-bifrost-token", "legacy")
	headers.Set("x-camelot-token", "camelot")
	headers.Set("Authorization", "Bearer authz")

	got := extractTokenFromHeaders(headers)
	if got != "authz" {
		t.Fatalf("expected authz token, got %q", got)
	}
}

func TestApplyAuthHeadersSetsCanonicalHeaders(t *testing.T) {
	req, err := http.NewRequest(http.MethodGet, "http://localhost", nil)
	if err != nil {
		t.Fatalf("request build failed: %v", err)
	}
	applyAuthHeaders(req, "abc123")

	if got := req.Header.Get("Authorization"); got != "Bearer abc123" {
		t.Fatalf("unexpected authorization header %q", got)
	}
	if got := req.Header.Get("x-camelot-token"); got != "abc123" {
		t.Fatalf("unexpected x-camelot-token header %q", got)
	}
}

func TestLoadConfigFallbackFlagDefaultsFalse(t *testing.T) {
	key := "BIFROST_SIDECAR_ALLOW_ENV_TOKEN_FALLBACK"
	_ = os.Unsetenv(key)
	cfg := loadConfig()
	if cfg.AllowEnvTokenFallback {
		t.Fatalf("expected env token fallback to default false")
	}

	if err := os.Setenv(key, "true"); err != nil {
		t.Fatalf("setenv failed: %v", err)
	}
	defer os.Unsetenv(key)
	cfg = loadConfig()
	if !cfg.AllowEnvTokenFallback {
		t.Fatalf("expected env token fallback true when configured")
	}
}

func TestLoadToonEvidence(t *testing.T) {
	path := writeTempToonEvidence(t)

	evidence, err := loadToonEvidence(path)
	if err != nil {
		t.Fatalf("loadToonEvidence failed: %v", err)
	}
	if evidence == nil {
		t.Fatalf("expected evidence")
	}
	if evidence.SHA256 != "abc123" {
		t.Fatalf("unexpected sha %q", evidence.SHA256)
	}
}

func TestProxyRequestForwardsToonEnvelopeHeaders(t *testing.T) {
	evidencePath := writeTempToonEvidence(t)
	var captured http.Header
	upstream := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		captured = r.Header.Clone()
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"ok":true}`))
	}))
	defer upstream.Close()

	cfg := config{
		UpstreamURL:      upstream.URL,
		RequestTimeout:   time.Second,
		ToonEvidencePath: evidencePath,
	}
	client := &http.Client{Timeout: cfg.RequestTimeout}
	req := httptest.NewRequest(http.MethodPost, "/v1/agent/dispatch", strings.NewReader(`{"intent":"status"}`))
	req.Header.Set("Authorization", "Bearer inbound")
	rec := httptest.NewRecorder()

	proxyRequest(rec, req, client, cfg, "/agent/dispatch")

	if rec.Code != http.StatusOK {
		t.Fatalf("unexpected status %d: %s", rec.Code, rec.Body.String())
	}
	if got := captured.Get("x-camelot-toon-sha256"); got != "abc123" {
		t.Fatalf("unexpected toon sha header %q", got)
	}
	if got := captured.Get("x-camelot-toon-reduction-pct"); got != "58.25" {
		t.Fatalf("unexpected toon reduction header %q", got)
	}
	if got := captured.Get("x-camelot-toon-evidence"); got != "confirmed" {
		t.Fatalf("unexpected toon evidence header %q", got)
	}
}

func writeTempToonEvidence(t *testing.T) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "camelot.toon.evidence.json")
	payload := toonEvidence{
		Status:        "COMPILED",
		Spec:          "v3.2",
		EvidenceClass: "confirmed",
		BytesToon:     1121,
		ReductionPct:  58.25,
		SHA256:        "abc123",
	}
	data, err := json.Marshal(payload)
	if err != nil {
		t.Fatalf("marshal evidence failed: %v", err)
	}
	if err := os.WriteFile(path, data, 0o600); err != nil {
		t.Fatalf("write evidence failed: %v", err)
	}
	return path
}
