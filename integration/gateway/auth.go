package main

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/hex"
	"log"
	"net/http"
	"os"
	"strings"
)

// P1 — authentication for the governed surface.
//
// WHAT THIS FIXES. Every route was previously unauthenticated behind
// `Access-Control-Allow-Origin: *`. POST /v1/confirmations is the tier-3 human
// gate the whole governance story rests on, and it could be driven by any page
// or process that could reach the port — which, with the old `:8788` bind
// default, included every host on the tailnet.
//
// WHAT THIS HONESTLY DOES NOT FIX. The console is served by a plain static
// file server rooted at integration/, so a browser can read .run/ over HTTP.
// A local process that can read the filesystem can therefore read the token —
// but such a process could already read it from disk, so auth was never the
// control there. What the token DOES stop is anything that can reach the port
// without local filesystem access, and the origin allow-list stops a hostile
// page in the user's browser from driving the gate cross-origin. Those are the
// two threats that were actually open.

type authConfig struct {
	token          string
	allowedOrigins []string
}

// openRoutes need no credential. /healthz is a liveness probe carrying no data
// and is polled by the startup gate before any token could be plumbed.
var openRoutes = map[string]bool{"/healthz": true}

func newAuthConfig(token string, origins []string) *authConfig {
	return &authConfig{token: token, allowedOrigins: origins}
}

// resolveAuthFromEnv builds the config the BINARY runs with. It can never
// return an empty token: an unset CAMELOT_API_TOKEN mints one rather than
// disabling the check.
//
// This is deliberate, and it is the lesson from z3_verify.py, which returns
// safe=true when its solver is missing — a guard that disappears when its
// dependency does is not a guard. Absence of configuration must not mean
// absence of enforcement.
func resolveAuthFromEnv() (*authConfig, bool) {
	minted := false
	token := strings.TrimSpace(os.Getenv("CAMELOT_API_TOKEN"))
	if token == "" {
		token = newToken()
		minted = true
	}

	origins := defaultAllowedOrigins()
	if raw := strings.TrimSpace(os.Getenv("CAMELOT_ALLOWED_ORIGINS")); raw != "" {
		origins = nil
		for _, o := range strings.Split(raw, ",") {
			if o = strings.TrimSpace(o); o != "" {
				origins = append(origins, o)
			}
		}
	}
	return newAuthConfig(token, origins), minted
}

func defaultAllowedOrigins() []string {
	port := os.Getenv("CONSOLE_PORT")
	if port == "" {
		port = "8080"
	}
	return []string{"http://localhost:" + port, "http://127.0.0.1:" + port}
}

func newToken() string {
	var b [32]byte
	if _, err := rand.Read(b[:]); err != nil {
		log.Fatalf("cannot mint an API token: %v", err) // fail closed, loudly
	}
	return hex.EncodeToString(b[:])
}

func (a *authConfig) originAllowed(origin string) bool {
	for _, o := range a.allowedOrigins {
		if o == origin {
			return true
		}
	}
	return false
}

// presented extracts the credential. Browsers cannot set headers on a
// WebSocket handshake, so the events endpoint also accepts ?token= — scoped to
// that one route rather than allowed everywhere, because query strings land in
// logs and referrers.
func presented(r *http.Request) string {
	if h := r.Header.Get("Authorization"); h != "" {
		if after, ok := strings.CutPrefix(h, "Bearer "); ok {
			return strings.TrimSpace(after)
		}
		return ""
	}
	if strings.HasSuffix(r.URL.Path, "/events") {
		return r.URL.Query().Get("token")
	}
	return ""
}

// withAuth gates every route except the open ones. Applied by Handler() only
// when a config is present; the binary always presents one.
func withAuth(cfg *authConfig, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Preflight carries no credential by definition; withCORS answers it
		// and has already enforced the origin allow-list.
		if r.Method == http.MethodOptions || openRoutes[r.URL.Path] {
			next.ServeHTTP(w, r)
			return
		}
		got := presented(r)
		// Constant-time: a length-leaking compare on a 32-byte token is a
		// small win for an attacker, but it is free to avoid.
		if got == "" || subtle.ConstantTimeCompare([]byte(got), []byte(cfg.token)) != 1 {
			httpError(w, http.StatusUnauthorized, "missing or invalid bearer token")
			return
		}
		next.ServeHTTP(w, r)
	})
}

// withCORS reflects only allow-listed origins. The previous wildcard let any
// page in the user's browser preflight and then drive the governed surface.
func withCORS(cfg *authConfig, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		origin := r.Header.Get("Origin")
		// Vary matters even when we refuse: a shared cache must not serve one
		// origin's allowed response to another origin.
		w.Header().Add("Vary", "Origin")

		if origin != "" {
			if cfg == nil || cfg.originAllowed(origin) {
				w.Header().Set("Access-Control-Allow-Origin", origin)
				w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
				w.Header().Set("Access-Control-Allow-Headers", "content-type, authorization")
			} else if r.Method == http.MethodOptions {
				// Refuse the preflight outright rather than letting the browser
				// infer denial from a missing header.
				httpError(w, http.StatusForbidden, "origin not allowed")
				return
			}
		}
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}
