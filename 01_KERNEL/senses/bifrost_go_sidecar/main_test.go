package main

import (
	"net/http"
	"os"
	"testing"
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
