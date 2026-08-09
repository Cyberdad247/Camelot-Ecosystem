package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// P1. The tier-3 confirmation endpoint was an unauthenticated HTTP call behind
// a wildcard CORS policy. These tests exist so that can never silently return.

const testToken = "test-token-0123456789abcdef"

func authedServer(t *testing.T) *Server {
	t.Helper()
	srv := NewServerWithEffectRoot(0, fixedNow, t.TempDir())
	srv.SetAuth(newAuthConfig(testToken, []string{"http://localhost:8080"}))
	return srv
}

func do(t *testing.T, srv *Server, method, path string, mutate func(*http.Request)) int {
	t.Helper()
	req := httptest.NewRequest(method, path, strings.NewReader(`{}`))
	req.Header.Set("content-type", "application/json")
	if mutate != nil {
		mutate(req)
	}
	rec := httptest.NewRecorder()
	srv.Handler().ServeHTTP(rec, req)
	return rec.Code
}

func bearer(tok string) func(*http.Request) {
	return func(r *http.Request) { r.Header.Set("Authorization", "Bearer "+tok) }
}

// The headline fix: the Iron Gate cannot be driven without a credential.
func TestConfirmationEndpointRequiresAToken(t *testing.T) {
	srv := authedServer(t)

	if code := do(t, srv, http.MethodPost, "/v1/confirmations", nil); code != http.StatusUnauthorized {
		t.Fatalf("unauthenticated confirmation: got %d, want 401", code)
	}
	if code := do(t, srv, http.MethodPost, "/v1/confirmations", bearer("wrong-token")); code != http.StatusUnauthorized {
		t.Fatalf("bad token: got %d, want 401", code)
	}
	// With the right token it gets past auth and into validation (400 for the
	// empty body) — proving the middleware passed it through, not that the
	// request succeeded.
	if code := do(t, srv, http.MethodPost, "/v1/confirmations", bearer(testToken)); code == http.StatusUnauthorized {
		t.Fatal("valid token was rejected")
	}
}

// Protecting only the tier-3 gate while leaving the tier-2 durable-write path
// open would be incoherent: the approval would be guarded and the effect not.
func TestEveryGovernedRouteRequiresAToken(t *testing.T) {
	srv := authedServer(t)

	for _, tc := range []struct{ method, path string }{
		{http.MethodPost, "/v1/voice/turns"},
		{http.MethodPost, "/v1/voice/barge-in"},
		{http.MethodPost, "/v1/confirmations"},
		{http.MethodGet, "/v1/audit/audit-0001"},
		{http.MethodGet, "/v1/models/stats"},
		{http.MethodPost, "/v1/nodes/register"},
		{http.MethodPost, "/v1/nodes/jobs"},
	} {
		if code := do(t, srv, tc.method, tc.path, nil); code != http.StatusUnauthorized {
			t.Errorf("%s %s unauthenticated: got %d, want 401", tc.method, tc.path, code)
		}
	}
}

// /healthz stays open: the startup gate polls it before a token could be
// plumbed, and it carries no data.
func TestHealthzStaysOpen(t *testing.T) {
	srv := authedServer(t)
	if code := do(t, srv, http.MethodGet, "/healthz", nil); code != http.StatusOK {
		t.Fatalf("healthz: got %d, want 200", code)
	}
}

// Browsers cannot set headers on a WebSocket handshake, so ?token= is accepted
// — but only on the events route, since query strings leak into logs.
func TestEventsAcceptsQueryTokenButOtherRoutesDoNot(t *testing.T) {
	srv := authedServer(t)

	// Wrong query token is still refused.
	if code := do(t, srv, http.MethodGet, "/v1/sessions/s1/events?token=nope", nil); code != http.StatusUnauthorized {
		t.Fatalf("events with bad query token: got %d, want 401", code)
	}
	// Correct query token passes auth; the handler then rejects it as a
	// non-WebSocket request, which is the proof it got through.
	if code := do(t, srv, http.MethodGet, "/v1/sessions/s1/events?token="+testToken, nil); code == http.StatusUnauthorized {
		t.Fatal("events rejected a valid query token")
	}
	// The escape hatch must not generalise.
	if code := do(t, srv, http.MethodPost, "/v1/voice/turns?token="+testToken, nil); code != http.StatusUnauthorized {
		t.Fatalf("query token accepted outside /events: got %d, want 401", code)
	}
}

func TestPreflightFromAnAllowedOriginIsAnswered(t *testing.T) {
	srv := authedServer(t)
	req := httptest.NewRequest(http.MethodOptions, "/v1/confirmations", nil)
	req.Header.Set("Origin", "http://localhost:8080")
	rec := httptest.NewRecorder()
	srv.Handler().ServeHTTP(rec, req)

	if rec.Code != http.StatusNoContent {
		t.Fatalf("allowed preflight: got %d, want 204", rec.Code)
	}
	if got := rec.Header().Get("Access-Control-Allow-Origin"); got != "http://localhost:8080" {
		t.Fatalf("allow-origin = %q", got)
	}
	if !strings.Contains(rec.Header().Get("Vary"), "Origin") {
		t.Fatal("missing Vary: Origin — a shared cache could cross origins")
	}
}

// The wildcard is gone. A hostile page must not be able to preflight the
// governed surface.
func TestPreflightFromAForeignOriginIsRefused(t *testing.T) {
	srv := authedServer(t)
	req := httptest.NewRequest(http.MethodOptions, "/v1/confirmations", nil)
	req.Header.Set("Origin", "https://evil.example")
	rec := httptest.NewRecorder()
	srv.Handler().ServeHTTP(rec, req)

	if rec.Code != http.StatusForbidden {
		t.Fatalf("foreign preflight: got %d, want 403", rec.Code)
	}
	if rec.Header().Get("Access-Control-Allow-Origin") != "" {
		t.Fatal("reflected a foreign origin")
	}
}

func TestNoWildcardOriginIsEverEmitted(t *testing.T) {
	srv := authedServer(t)
	for _, origin := range []string{"http://localhost:8080", "https://evil.example", ""} {
		req := httptest.NewRequest(http.MethodGet, "/healthz", nil)
		if origin != "" {
			req.Header.Set("Origin", origin)
		}
		rec := httptest.NewRecorder()
		srv.Handler().ServeHTTP(rec, req)
		if rec.Header().Get("Access-Control-Allow-Origin") == "*" {
			t.Fatalf("wildcard emitted for origin %q", origin)
		}
	}
}

// THE FAIL-CLOSED TEST. z3_verify.py returns safe=true when its solver is
// missing; a guard that vanishes with its configuration is not a guard. The
// binary's own resolution path must never yield an empty token.
func TestResolveAuthFromEnvNeverReturnsAnEmptyToken(t *testing.T) {
	t.Setenv("CAMELOT_API_TOKEN", "")
	cfg, minted := resolveAuthFromEnv()
	if cfg.token == "" {
		t.Fatal("unset CAMELOT_API_TOKEN produced an OPEN server")
	}
	if !minted {
		t.Fatal("expected the token to be reported as minted")
	}
	if len(cfg.token) < 32 {
		t.Fatalf("minted token is too short to resist guessing: %d chars", len(cfg.token))
	}

	t.Setenv("CAMELOT_API_TOKEN", "  pinned-token-value  ")
	cfg, minted = resolveAuthFromEnv()
	if cfg.token != "pinned-token-value" {
		t.Fatalf("pinned token = %q (whitespace should be trimmed)", cfg.token)
	}
	if minted {
		t.Fatal("a pinned token must not report as minted")
	}
}

func TestMintedTokensAreUnique(t *testing.T) {
	seen := map[string]bool{}
	for i := 0; i < 100; i++ {
		tok := newToken()
		if seen[tok] {
			t.Fatal("newToken repeated a value")
		}
		seen[tok] = true
	}
}

func TestAllowedOriginsAreConfigurable(t *testing.T) {
	t.Setenv("CAMELOT_API_TOKEN", "x")
	t.Setenv("CAMELOT_ALLOWED_ORIGINS", "http://a.test, http://b.test")
	cfg, _ := resolveAuthFromEnv()
	if len(cfg.allowedOrigins) != 2 || !cfg.originAllowed("http://b.test") {
		t.Fatalf("origins = %v", cfg.allowedOrigins)
	}
	if cfg.originAllowed("http://c.test") {
		t.Fatal("allowed an origin outside the list")
	}
}
