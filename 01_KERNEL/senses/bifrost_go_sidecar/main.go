package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

type config struct {
	BindAddr              string
	UpstreamURL           string
	GatewayToken          string
	AllowEnvTokenFallback bool
	RequestTimeout        time.Duration
}

type healthResponse struct {
	Status         string `json:"status"`
	Node           string `json:"node"`
	UpstreamURL    string `json:"upstream_url"`
	AuthRequired   bool   `json:"auth_required"`
	RequestTimeout string `json:"request_timeout"`
}

func envOr(key string, fallback string) string {
	raw := strings.TrimSpace(os.Getenv(key))
	if raw == "" {
		return fallback
	}
	return raw
}

func loadConfig() config {
	timeoutMs := 10000
	if raw := strings.TrimSpace(os.Getenv("BIFROST_SIDECAR_TIMEOUT_MS")); raw != "" {
		var parsed int
		if _, err := fmt.Sscanf(raw, "%d", &parsed); err == nil && parsed > 0 {
			timeoutMs = parsed
		}
	}
	return config{
		BindAddr:     envOr("BIFROST_SIDECAR_BIND_ADDR", "127.0.0.1:8011"),
		UpstreamURL:  strings.TrimRight(envOr("BIFROST_SIDECAR_UPSTREAM_URL", "http://127.0.0.1:8001"), "/"),
		GatewayToken: strings.TrimSpace(os.Getenv("CAMELOT_GATEWAY_TOKEN")),
		AllowEnvTokenFallback: strings.EqualFold(strings.TrimSpace(os.Getenv("BIFROST_SIDECAR_ALLOW_ENV_TOKEN_FALLBACK")), "true") ||
			strings.TrimSpace(os.Getenv("BIFROST_SIDECAR_ALLOW_ENV_TOKEN_FALLBACK")) == "1",
		RequestTimeout: time.Duration(timeoutMs) * time.Millisecond,
	}
}

func extractBearerToken(raw string) string {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return ""
	}
	if strings.HasPrefix(strings.ToLower(raw), "bearer ") {
		return strings.TrimSpace(raw[7:])
	}
	return raw
}

func extractTokenFromHeaders(headers http.Header) string {
	if token := extractBearerToken(headers.Get("Authorization")); token != "" {
		return token
	}
	if token := strings.TrimSpace(headers.Get("x-camelot-token")); token != "" {
		return token
	}
	if token := strings.TrimSpace(headers.Get("x-bifrost-token")); token != "" {
		return token
	}
	return ""
}

func applyAuthHeaders(req *http.Request, token string) {
	if strings.TrimSpace(token) == "" {
		return
	}
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("x-camelot-token", token)
}

func ensureTraceID(inbound string) string {
	id := strings.TrimSpace(inbound)
	if id != "" {
		return id
	}
	buf := make([]byte, 8)
	if _, err := rand.Read(buf); err == nil {
		return fmt.Sprintf("bifrost-%d-%s", time.Now().UnixMilli(), hex.EncodeToString(buf))
	}
	return fmt.Sprintf("bifrost-%d", time.Now().UnixMilli())
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func proxyRequest(w http.ResponseWriter, r *http.Request, client *http.Client, cfg config, upstreamPath string) {
	traceID := ensureTraceID(r.Header.Get("x-trace-id"))
	targetURL := cfg.UpstreamURL + upstreamPath

	body, err := io.ReadAll(r.Body)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{
			"error":  "invalid request body",
			"detail": err.Error(),
		})
		return
	}

	upstreamReq, err := http.NewRequestWithContext(r.Context(), r.Method, targetURL, strings.NewReader(string(body)))
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]any{
			"error":  "upstream request build failed",
			"detail": err.Error(),
		})
		return
	}
	upstreamReq.Header.Set("Content-Type", r.Header.Get("Content-Type"))
	upstreamReq.Header.Set("x-trace-id", traceID)

	token := extractTokenFromHeaders(r.Header)
	if token == "" && cfg.AllowEnvTokenFallback {
		token = cfg.GatewayToken
	}
	if token == "" {
		writeJSON(w, http.StatusUnauthorized, map[string]any{
			"error": "missing auth token",
		})
		return
	}
	applyAuthHeaders(upstreamReq, token)

	resp, err := client.Do(upstreamReq)
	if err != nil {
		writeJSON(w, http.StatusBadGateway, map[string]any{
			"error":    "upstream request failed",
			"detail":   err.Error(),
			"trace_id": traceID,
		})
		return
	}
	defer resp.Body.Close()

	w.Header().Set("x-trace-id", traceID)
	w.Header().Set("Content-Type", resp.Header.Get("Content-Type"))
	w.WriteHeader(resp.StatusCode)
	_, _ = io.Copy(w, resp.Body)
}

func main() {
	cfg := loadConfig()
	client := &http.Client{Timeout: cfg.RequestTimeout}

	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, healthResponse{
			Status:         "healthy",
			Node:           "BIFROST_GO_SIDECAR_v0.1.0",
			UpstreamURL:    cfg.UpstreamURL,
			AuthRequired:   cfg.GatewayToken != "",
			RequestTimeout: cfg.RequestTimeout.String(),
		})
	})
	mux.HandleFunc("/v1/bifrost/status", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			writeJSON(w, http.StatusMethodNotAllowed, map[string]string{"error": "method not allowed"})
			return
		}
		proxyRequest(w, r, client, cfg, "/bifrost/status")
	})
	mux.HandleFunc("/v1/agent/dispatch", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			writeJSON(w, http.StatusMethodNotAllowed, map[string]string{"error": "method not allowed"})
			return
		}
		proxyRequest(w, r, client, cfg, "/agent/dispatch")
	})

	server := &http.Server{
		Addr:              cfg.BindAddr,
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Printf("Bifrost Go Sidecar online on %s -> %s", cfg.BindAddr, cfg.UpstreamURL)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("sidecar failed: %v", err)
	}
}
