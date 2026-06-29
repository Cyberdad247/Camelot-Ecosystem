// Package providers holds live LLM Provider implementations for the Polyglot
// Matrix. Each type satisfies orchestration.Provider structurally
// (Name() string + Invoke(ctx, knight, intent, skills) (string, error)) so it
// can be passed to orchestration.NewAPEEv6RouterWith without an import cycle.
//
// Secrets come from the environment only (Sentinel Shield, Pillar 8) — never
// from source. BaseURL is overridable so the provider is testable against a
// mock server without a real key or network.
package providers

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

const (
	openAIDefaultURL   = "https://api.openai.com/v1/chat/completions"
	openAIDefaultModel = "gpt-4o"
	sirCodexSystem     = "You are SIR_CODEX, the Edge Fabricator of Camelot-OS. " +
		"Output strict, optimized code with no commentary unless asked."
)

// OpenAIProvider wires SIR_CODEX to the OpenAI Chat Completions API using a
// lean net/http client (no heavy SDK).
type OpenAIProvider struct {
	APIKey  string
	Model   string
	BaseURL string
	Client  *http.Client
	// Label overrides the engine name reported by Name() (e.g. "Bifrost:gpt-4o");
	// empty defaults to "OpenAI".
	Label string
}

// NewOpenAIProvider builds the provider, pulling the key from CAMELOT_OPENAI_KEY.
// Returns an error (not a panic) when the key is absent, so the factory can fall
// back to a stub provider gracefully.
func NewOpenAIProvider() (*OpenAIProvider, error) {
	key := os.Getenv("CAMELOT_OPENAI_KEY")
	if key == "" {
		return nil, errors.New("CAMELOT_OPENAI_KEY is not set")
	}
	model := os.Getenv("CAMELOT_OPENAI_MODEL")
	if model == "" {
		model = openAIDefaultModel
	}
	base := os.Getenv("CAMELOT_OPENAI_URL") // override for gateways (e.g. Aperture)
	if base == "" {
		base = openAIDefaultURL
	}
	return &OpenAIProvider{
		APIKey:  key,
		Model:   model,
		BaseURL: base,
		Client:  &http.Client{Timeout: 60 * time.Second},
	}, nil
}

// Name identifies the engine (satisfies orchestration.Provider).
func (p *OpenAIProvider) Name() string {
	if p.Label != "" {
		return p.Label
	}
	return "OpenAI"
}

type chatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// Invoke dispatches the intent (with any injected skills) to the model and
// returns the assistant's content. Satisfies orchestration.Provider.
func (p *OpenAIProvider) Invoke(ctx context.Context, knight, intent, skills string) (string, error) {
	user := intent
	if skills != "" {
		user = "Available skills (TOON):\n" + skills + "\n\nTask: " + intent
	}
	payload := map[string]any{
		"model": p.Model,
		"messages": []chatMessage{
			{Role: "system", Content: sirCodexSystem + " (acting Knight: " + knight + ")"},
			{Role: "user", Content: user},
		},
		"temperature": 0.2, // deterministic UAST generation
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("openai: marshal payload: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, p.BaseURL, bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("openai: build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+p.APIKey)

	resp, err := p.Client.Do(req)
	if err != nil {
		return "", fmt.Errorf("openai: request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 4096))
		return "", fmt.Errorf("openai: HTTP %d: %s", resp.StatusCode, string(b))
	}

	var result struct {
		Choices []struct {
			Message chatMessage `json:"message"`
		} `json:"choices"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("openai: decode response: %w", err)
	}
	if len(result.Choices) == 0 {
		return "", errors.New("openai: no choices returned")
	}
	return result.Choices[0].Message.Content, nil
}
