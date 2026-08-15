package providers

import (
	"context"
	"net/http"
	"os"
	"strings"
	"time"
)

// ── Zero-cost routing via the Bifrost / CLIProxy gateway ─────────────────────
//
// The CLIProxy is a local, OpenAI-compatible endpoint (default
// http://127.0.0.1:8080/v1) that serves models for FREE via CLI OAuth — your
// existing Claude/Gemini/Codex CLI subscriptions, not pay-per-token API keys.
// Bifrost dispatches through it. Because it speaks the OpenAI Chat Completions
// protocol, every Knight routes through it with just a different model string.
//
// This is the "utilize the bifrost bridge + omnirouter zero-cost options" path:
// no paid provider keys, no per-token billing.

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

// GatewayBase returns the CLIProxy/Bifrost OpenAI-compatible chat endpoint.
func GatewayBase() string {
	base := strings.TrimRight(env("CLIPROXY_BASE", "http://127.0.0.1:8080/v1"), "/")
	return base + "/chat/completions"
}

// NewGatewayProvider builds a zero-cost provider that routes a Knight through
// the Bifrost/CLIProxy gateway with the given free model (e.g. "gpt-4o",
// "gemini-2.5-flash", "claude-sonnet-4-6"). The local proxy key (CLIPROXY_KEY,
// default "proxy-admin-key") is NOT a paid credential — it authorizes the
// loopback proxy only.
func NewGatewayProvider(label, model string) *OpenAIProvider {
	return &OpenAIProvider{
		APIKey:  env("CLIPROXY_KEY", "proxy-admin-key"),
		Model:   model,
		BaseURL: GatewayBase(),
		Client:  &http.Client{Timeout: 60 * time.Second},
		Label:   label,
	}
}

// LocalStubProvider is the offline TinyLM fallback — deterministic, no network.
// Used when the gateway is unreachable so a Knight degrades gracefully instead
// of failing the whole router.
type LocalStubProvider struct{ knight string }

// NewLocalStubProvider returns the local fallback for a Knight.
func NewLocalStubProvider(knight string) *LocalStubProvider {
	return &LocalStubProvider{knight: knight}
}

// Name satisfies orchestration.Provider.
func (s *LocalStubProvider) Name() string { return "LocalTinyLM" }

// Invoke satisfies orchestration.Provider — echoes a local, offline response.
func (s *LocalStubProvider) Invoke(_ context.Context, knight, intent, _ string) (string, error) {
	return "[LocalTinyLM/" + knight + "] (gateway offline) " + intent, nil
}

// GatewayReachable probes whether the zero-cost gateway is up (so we can pick
// live-free vs local-stub at boot without failing).
func GatewayReachable(timeout time.Duration) bool {
	base := strings.TrimRight(env("CLIPROXY_BASE", "http://127.0.0.1:8080/v1"), "/")
	c := &http.Client{Timeout: timeout}
	// /models is the OpenAI-compatible liveness probe; any non-error response
	// (even 401/404) means the proxy is answering.
	resp, err := c.Get(base + "/models")
	if err != nil {
		return false
	}
	_ = resp.Body.Close()
	return true
}

// ── Local OpenAI-compatible tier (openai-oauth / LiteRT-LM) ──────────────────
//
// Phase 1 integration (docs/architecture/integrations.md): openai-oauth
// (vendor 02_FORGE/KINETIC_ARMORY/openai-oauth) turns a ChatGPT account into an
// OpenAI-compatible dev proxy at http://127.0.0.1:10531/v1, and LiteRT-LM
// (02_FORGE/KINETIC_ARMORY/LiteRT-LM) ships an OpenAI-compatible server for
// on-device inference. Both speak the Chat Completions protocol, so ONE
// endpoint tier serves both — the SADD Inference Node adapter needs no custom
// protocol. This tier slots between the CLIProxy gateway and the offline stub:
// gateway offline + local endpoint up → route through the local endpoint.
const openAICompatDefaultBase = "http://127.0.0.1:10531/v1" // openai-oauth dev proxy

// OpenAICompatBase returns the local OpenAI-compatible chat endpoint. Override
// with OPENAI_COMPAT_BASE (e.g. a LiteRT-LM server on another port).
func OpenAICompatBase() string {
	base := strings.TrimRight(env("OPENAI_COMPAT_BASE", openAICompatDefaultBase), "/")
	return base + "/chat/completions"
}

// NewOpenAICompatProvider builds a provider bound to the local OpenAI-compatible
// endpoint. OPENAI_COMPAT_KEY is a loopback credential (default "local"), never
// a paid API key; some proxies require a non-empty bearer, most ignore it.
func NewOpenAICompatProvider(label, model string) *OpenAIProvider {
	return &OpenAIProvider{
		APIKey:  env("OPENAI_COMPAT_KEY", "local"),
		Model:   model,
		BaseURL: OpenAICompatBase(),
		Client:  &http.Client{Timeout: 60 * time.Second},
		Label:   label,
	}
}

// OpenAICompatReachable probes the local OpenAI-compatible endpoint (same
// /models liveness convention as the gateway).
func OpenAICompatReachable(timeout time.Duration) bool {
	base := strings.TrimRight(env("OPENAI_COMPAT_BASE", openAICompatDefaultBase), "/")
	c := &http.Client{Timeout: timeout}
	resp, err := c.Get(base + "/models")
	if err != nil {
		return false
	}
	_ = resp.Body.Close()
	return true
}
