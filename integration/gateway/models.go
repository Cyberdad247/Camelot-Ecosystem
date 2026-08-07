package main

// Phase 3: model routing behind the gateway. The gateway REMAINS the policy
// boundary — a model narrates replies and may PROPOSE a bounded skill plan,
// but proposals are only validated and audited, never executed; only the
// policy kernel issues leases. Narration always runs AFTER any skill
// execution, so a generation retry or fallback can never re-run a tool
// (the no-retry-for-effectful rule holds structurally).

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

// ── shared contracts (mirrored in @camelot/contracts model.ts) ──────────

type ModelRequest struct {
	RequestID string   `json:"requestId"`
	SessionID string   `json:"sessionId"`
	TurnID    string   `json:"turnId"`
	Prompt    string   `json:"prompt"`
	Context   []string `json:"context,omitempty"`
	MaxChars  int      `json:"maxChars"`
}

type ModelDelta struct {
	RequestID string `json:"requestId"`
	Seq       int    `json:"seq"`
	Text      string `json:"text"`
}

type ModelFailure struct {
	Code   string `json:"code"` // timeout|disabled|not_allowed|oversized|malformed_stream|provider_error
	Detail string `json:"detail"`
}

type ModelRouteDecision struct {
	RequestID string        `json:"requestId"`
	Provider  string        `json:"provider"`
	Reason    string        `json:"reason"`
	Fallback  bool          `json:"fallback"`
	Failure   *ModelFailure `json:"failure,omitempty"`
}

type ModelResponse struct {
	RequestID    string `json:"requestId"`
	Provider     string `json:"provider"`
	Text         string `json:"text"`
	FinishReason string `json:"finishReason"` // complete|cancelled|fallback|error
	FirstTokenMs int64  `json:"firstTokenMs"`
	CompletionMs int64  `json:"completionMs"`
	DeltaCount   int    `json:"deltaCount"`
}

type ModelProviderHealth struct {
	Provider string `json:"provider"`
	OK       bool   `json:"ok"`
	Detail   string `json:"detail,omitempty"`
}

// ── interfaces ──────────────────────────────────────────────────────────

type StreamSink interface {
	Delta(seq int, text string) error
}

type ModelProvider interface {
	Name() string
	Health(ctx context.Context) ModelProviderHealth
	// Stream emits deltas to the sink until done, error, or ctx cancellation.
	Stream(ctx context.Context, req ModelRequest, sink StreamSink) error
}

// ── deterministic provider (default; byte-identical to Phase 1 replies) ─

type DeterministicProvider struct {
	chunkDelay time.Duration
}

func (d *DeterministicProvider) Name() string { return "deterministic" }

func (d *DeterministicProvider) Health(context.Context) ModelProviderHealth {
	return ModelProviderHealth{Provider: "deterministic", OK: true}
}

func (d *DeterministicProvider) Stream(ctx context.Context, req ModelRequest, sink StreamSink) error {
	words := strings.Split(req.Prompt, " ")
	for i, w := range words {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(d.chunkDelay):
		}
		text := w
		if i < len(words)-1 {
			text += " "
		}
		if err := sink.Delta(i, text); err != nil {
			return err
		}
	}
	return nil
}

// ── configured provider (OpenAI-compatible SSE; off unless enabled) ─────

type ConfiguredProvider struct {
	ProviderName string
	URL          string // e.g. http://localhost:11434/v1/chat/completions
	Model        string
	APIKey       string // from env/keystore only; never persisted or audited
	Client       *http.Client
}

func (p *ConfiguredProvider) Name() string { return p.ProviderName }

func (p *ConfiguredProvider) Health(ctx context.Context) ModelProviderHealth {
	return ModelProviderHealth{Provider: p.ProviderName, OK: p.URL != "", Detail: p.Model}
}

func (p *ConfiguredProvider) Stream(ctx context.Context, req ModelRequest, sink StreamSink) error {
	prompt := req.Prompt
	if len(req.Context) > 0 {
		prompt = strings.Join(req.Context, "\n") + "\n" + prompt
	}
	if req.MaxChars > 0 && len(prompt) > req.MaxChars {
		prompt = prompt[len(prompt)-req.MaxChars:]
	}
	body, _ := json.Marshal(map[string]any{
		"model":  p.Model,
		"stream": true,
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
	})
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, p.URL, bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("provider_error: %w", err)
	}
	httpReq.Header.Set("Content-Type", "application/json")
	if p.APIKey != "" {
		httpReq.Header.Set("Authorization", "Bearer "+p.APIKey)
	}
	client := p.Client
	if client == nil {
		client = http.DefaultClient
	}
	res, err := client.Do(httpReq)
	if err != nil {
		return fmt.Errorf("provider_error: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return fmt.Errorf("provider_error: HTTP %d", res.StatusCode)
	}

	scanner := bufio.NewScanner(res.Body)
	scanner.Buffer(make([]byte, 64*1024), 1<<20)
	seq := 0
	sawData := false
	emitted := 0
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, ":") {
			continue
		}
		payload, ok := strings.CutPrefix(line, "data:")
		if !ok {
			return errors.New("malformed_stream: non-SSE line in response body")
		}
		payload = strings.TrimSpace(payload)
		if payload == "[DONE]" {
			return nil
		}
		var chunk struct {
			Choices []struct {
				Delta struct {
					Content string `json:"content"`
				} `json:"delta"`
			} `json:"choices"`
		}
		if err := json.Unmarshal([]byte(payload), &chunk); err != nil {
			return fmt.Errorf("malformed_stream: %w", err)
		}
		sawData = true
		if len(chunk.Choices) == 0 {
			continue
		}
		text := chunk.Choices[0].Delta.Content
		if text == "" {
			continue
		}
		emitted += len(text)
		if req.MaxChars > 0 && emitted > req.MaxChars {
			return nil // response cap reached: stop cleanly
		}
		if err := sink.Delta(seq, text); err != nil {
			return err
		}
		seq++
	}
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("provider_error: %w", err)
	}
	if !sawData {
		return errors.New("malformed_stream: empty stream")
	}
	return nil
}

// ── router ──────────────────────────────────────────────────────────────

type ModelStats struct {
	Provider        string  `json:"provider"`
	Requests        int64   `json:"requests"`
	Fallbacks       int64   `json:"fallbacks"`
	PlanProposals   int64   `json:"planProposals"`
	PlanDenials     int64   `json:"planDenials"`
	AvgFirstTokenMs float64 `json:"avgFirstTokenMs"`
	AvgCompletionMs float64 `json:"avgCompletionMs"`
}

type ModelConfig struct {
	Enabled      bool
	Allow        []string // provider allow-list; deterministic is always allowed
	Name         string
	URL          string
	Model        string
	APIKey       string
	Timeout      time.Duration
	MaxResponse  int
	ContextMax   int
	ContextTurns int
}

func ModelConfigFromEnv() ModelConfig {
	timeout, _ := time.ParseDuration(getenvDefault("MODEL_TIMEOUT", "10s"))
	return ModelConfig{
		Enabled:      os.Getenv("ENABLE_MODEL_PROVIDER") == "true",
		Allow:        strings.Split(getenvDefault("MODEL_PROVIDER_ALLOW", "deterministic"), ","),
		Name:         getenvDefault("MODEL_PROVIDER_NAME", "configured"),
		URL:          os.Getenv("MODEL_PROVIDER_URL"),
		Model:        getenvDefault("MODEL_PROVIDER_MODEL", "default"),
		APIKey:       os.Getenv("MODEL_PROVIDER_API_KEY"),
		Timeout:      timeout,
		MaxResponse:  2000,
		ContextMax:   4000,
		ContextTurns: 8,
	}
}

func getenvDefault(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

type ModelRouter struct {
	deterministic *DeterministicProvider
	configured    ModelProvider // nil unless enabled + allow-listed
	timeout       time.Duration
	maxResponse   int
	contextMax    int
	contextTurns  int

	mu          sync.Mutex
	contexts    map[string][]string // sessionID -> recent transcripts (memory only)
	requests    int64
	fallbacks   int64
	planProps   int64
	planDenials int64
	sumFirstMs  int64
	sumTotalMs  int64
	reqSeq      int64
}

func NewModelRouter(chunkDelay time.Duration) *ModelRouter {
	return &ModelRouter{
		deterministic: &DeterministicProvider{chunkDelay: chunkDelay},
		timeout:       10 * time.Second,
		maxResponse:   2000,
		contextMax:    4000,
		contextTurns:  8,
		contexts:      map[string][]string{},
	}
}

func NewModelRouterFromConfig(chunkDelay time.Duration, cfg ModelConfig) *ModelRouter {
	r := NewModelRouter(chunkDelay)
	if cfg.Timeout > 0 {
		r.timeout = cfg.Timeout
	}
	if cfg.MaxResponse > 0 {
		r.maxResponse = cfg.MaxResponse
	}
	if cfg.ContextMax > 0 {
		r.contextMax = cfg.ContextMax
	}
	if cfg.ContextTurns > 0 {
		r.contextTurns = cfg.ContextTurns
	}
	allowed := false
	for _, name := range cfg.Allow {
		if strings.TrimSpace(name) == cfg.Name {
			allowed = true
		}
	}
	// Configured provider exists ONLY when explicitly enabled, allow-listed,
	// and pointed at a URL. Nothing is ever auto-started or downloaded.
	if cfg.Enabled && allowed && cfg.URL != "" {
		r.configured = &ConfiguredProvider{
			ProviderName: cfg.Name,
			URL:          cfg.URL,
			Model:        cfg.Model,
			APIKey:       cfg.APIKey,
		}
	}
	return r
}

// PrimaryIsDeterministic tells handlers whether the sync reply text is known
// upfront (deterministic) or arrives only via streaming (configured).
func (r *ModelRouter) PrimaryIsDeterministic() bool {
	return r.configured == nil
}

// RememberTranscript keeps a capped, session-local, MEMORY-ONLY context
// window (never persisted; dies with the process).
func (r *ModelRouter) RememberTranscript(sessionID, transcript string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	window := append(r.contexts[sessionID], transcript)
	if len(window) > r.contextTurns {
		window = window[len(window)-r.contextTurns:]
	}
	r.contexts[sessionID] = window
}

func (r *ModelRouter) contextWindow(sessionID string) []string {
	r.mu.Lock()
	defer r.mu.Unlock()
	window := r.contexts[sessionID]
	out := make([]string, len(window))
	copy(out, window)
	total := 0
	for i := len(out) - 1; i >= 0; i-- {
		total += len(out[i])
		if total > r.contextMax {
			return out[i+1:]
		}
	}
	return out
}

func (r *ModelRouter) Stats() ModelStats {
	r.mu.Lock()
	defer r.mu.Unlock()
	name := "deterministic"
	if r.configured != nil {
		name = r.configured.Name()
	}
	stats := ModelStats{
		Provider:      name,
		Requests:      r.requests,
		Fallbacks:     r.fallbacks,
		PlanProposals: r.planProps,
		PlanDenials:   r.planDenials,
	}
	if r.requests > 0 {
		stats.AvgFirstTokenMs = float64(r.sumFirstMs) / float64(r.requests)
		stats.AvgCompletionMs = float64(r.sumTotalMs) / float64(r.requests)
	}
	return stats
}

// hubSink forwards deltas as the existing reply.chunk session events, while
// holding back any trailing "PLAN {...}" directive line (model tool-plan
// proposals are extracted for validation, never spoken or rendered).
type hubSink struct {
	hub       *SessionHub
	sessionID string
	turnID    string
	seq       int
	firstAt   time.Time
	started   time.Time
	text      strings.Builder
	lineBuf   strings.Builder
	planLine  string
}

func (s *hubSink) Delta(_ int, text string) error {
	if s.firstAt.IsZero() {
		s.firstAt = time.Now()
	}
	for _, r := range text {
		if r == '\n' {
			s.flushLine("\n")
			continue
		}
		s.lineBuf.WriteRune(r)
		// Emit eagerly unless the line could be a PLAN directive prefix.
		if !couldBePlan(s.lineBuf.String()) {
			s.emit(s.lineBuf.String())
			s.lineBuf.Reset()
		}
	}
	return nil
}

func (s *hubSink) flushLine(suffix string) {
	line := s.lineBuf.String()
	s.lineBuf.Reset()
	if strings.HasPrefix(strings.TrimSpace(line), "PLAN ") {
		s.planLine = strings.TrimSpace(line)
		return
	}
	if line != "" || suffix != "" {
		s.emit(line + suffix)
	}
}

func (s *hubSink) emit(text string) {
	if text == "" {
		return
	}
	s.text.WriteString(text)
	s.hub.Publish(s.sessionID, SessionEvent{Type: "reply.chunk", TurnID: s.turnID, Seq: s.seq, Text: text})
	s.seq++
}

func (s *hubSink) finish() {
	s.flushLine("")
}

func couldBePlan(partial string) bool {
	const directive = "PLAN "
	trimmed := strings.TrimLeft(partial, " ")
	if len(trimmed) >= len(directive) {
		return strings.HasPrefix(trimmed, directive)
	}
	return strings.HasPrefix(directive, trimmed)
}

// Narrate streams the reply for an allowed turn. deterministicReply is the
// fixture text used when routing deterministically or on any provider
// failure (never a silent failure). Runs async; barge-in cancels it through
// the same registry as Phase 1 streaming.
func (r *ModelRouter) Narrate(hub *SessionHub, audit *AuditLog, sessionID, turnID, transcript, deterministicReply string) {
	go r.narrate(hub, audit, sessionID, turnID, transcript, deterministicReply)
}

func (r *ModelRouter) narrate(hub *SessionHub, audit *AuditLog, sessionID, turnID, transcript, deterministicReply string) {
	ctx, cleanup := hub.RegisterStream(turnID)
	defer cleanup()

	r.mu.Lock()
	r.reqSeq++
	requestID := fmt.Sprintf("mreq-%04d", r.reqSeq)
	provider := ModelProvider(r.deterministic)
	if r.configured != nil {
		provider = r.configured
	}
	r.mu.Unlock()

	sink := &hubSink{hub: hub, sessionID: sessionID, turnID: turnID, started: time.Now()}
	decision := ModelRouteDecision{RequestID: requestID, Provider: provider.Name(), Reason: "primary route"}
	hub.Publish(sessionID, SessionEvent{
		Type: "model.route", TurnID: turnID, Provider: provider.Name(), Reason: decision.Reason,
	})

	request := ModelRequest{
		RequestID: requestID,
		SessionID: sessionID,
		TurnID:    turnID,
		Prompt:    deterministicReply,
		MaxChars:  r.maxResponse,
	}
	runCtx := ctx
	var cancelTimeout context.CancelFunc
	if provider.Name() != "deterministic" {
		// Real generation: transcript + capped session context; bounded time.
		request.Prompt = transcript
		request.Context = r.contextWindow(sessionID)
		runCtx, cancelTimeout = context.WithTimeout(ctx, r.timeout)
		defer cancelTimeout()
	}

	err := provider.Stream(runCtx, request, sink)
	sink.finish()

	userCancelled := ctx.Err() != nil // barge-in, not timeout
	if err != nil && !userCancelled {
		// Typed failure -> deterministic fallback, loudly recorded.
		failure := classifyModelFailure(err, runCtx)
		decision.Fallback = true
		decision.Failure = &failure
		decision.Reason = "provider failed: " + failure.Code
		r.mu.Lock()
		r.fallbacks++
		r.mu.Unlock()

		hub.Publish(sessionID, SessionEvent{
			Type: "model.route", TurnID: turnID, Provider: "deterministic",
			Fallback: true, Reason: decision.Reason,
		})
		auditEvent := audit.Append(auditEntry{
			SessionID:       sessionID,
			TurnID:          turnID,
			Kind:            "model.route",
			RedactedSummary: fmt.Sprintf("model %s failed (%s); deterministic fallback served", provider.Name(), failure.Code),
		})
		hub.Publish(sessionID, SessionEvent{Type: "audit.appended", AuditID: auditEvent.AuditID, Kind: auditEvent.Kind})

		fallbackSink := &hubSink{hub: hub, sessionID: sessionID, turnID: turnID, started: sink.started, seq: sink.seq}
		fbErr := r.deterministic.Stream(ctx, ModelRequest{RequestID: requestID, Prompt: deterministicReply}, fallbackSink)
		fallbackSink.finish()
		userCancelled = fbErr != nil && ctx.Err() != nil
		sink = fallbackSink
	} else if err == nil {
		auditEvent := audit.Append(auditEntry{
			SessionID:       sessionID,
			TurnID:          turnID,
			Kind:            "model.route",
			RedactedSummary: fmt.Sprintf("reply narrated by %s (%d deltas)", provider.Name(), sink.seq),
		})
		hub.Publish(sessionID, SessionEvent{Type: "audit.appended", AuditID: auditEvent.AuditID, Kind: auditEvent.Kind})
	}

	if userCancelled {
		hub.Publish(sessionID, SessionEvent{Type: "turn.cancelled", TurnID: turnID, Reason: "barge-in"})
		return
	}

	if sink.planLine != "" {
		r.recordPlanProposal(hub, audit, sessionID, turnID, provider.Name(), sink.planLine)
	}

	r.mu.Lock()
	r.requests++
	if !sink.firstAt.IsZero() {
		r.sumFirstMs += sink.firstAt.Sub(sink.started).Milliseconds()
	}
	r.sumTotalMs += time.Since(sink.started).Milliseconds()
	r.mu.Unlock()

	hub.Publish(sessionID, SessionEvent{Type: "reply.done", TurnID: turnID})
}

// recordPlanProposal validates a model-proposed skill plan against the skill
// registry and policy tiers. Proposals are NEVER executed in Phase 3 —
// validated ones are audited as proposals, unknown ones are denied loudly.
func (r *ModelRouter) recordPlanProposal(hub *SessionHub, audit *AuditLog, sessionID, turnID, providerName, planLine string) {
	var plan struct {
		SkillID string `json:"skillId"`
	}
	payload := strings.TrimPrefix(planLine, "PLAN ")
	parseErr := json.Unmarshal([]byte(payload), &plan)

	var event AuditEvent
	if parseErr != nil || plan.SkillID == "" {
		r.mu.Lock()
		r.planDenials++
		r.mu.Unlock()
		event = audit.Append(auditEntry{
			SessionID: sessionID, TurnID: turnID, Kind: "model.plan.denied",
			RedactedSummary: fmt.Sprintf("model %s proposed a malformed tool plan; denied", providerName),
		})
	} else if skill, ok := skillByID(plan.SkillID); ok {
		r.mu.Lock()
		r.planProps++
		r.mu.Unlock()
		event = audit.Append(auditEntry{
			SessionID: sessionID, TurnID: turnID, Kind: "model.plan.proposed",
			RedactedSummary: fmt.Sprintf("model %s proposed skill %s (tier %d); recorded only — execution requires the standard turn/confirmation flow", providerName, skill.ID, skill.Tier),
		})
	} else {
		r.mu.Lock()
		r.planDenials++
		r.mu.Unlock()
		event = audit.Append(auditEntry{
			SessionID: sessionID, TurnID: turnID, Kind: "model.plan.denied",
			RedactedSummary: fmt.Sprintf("model %s proposed unknown skill %q; denied", providerName, plan.SkillID),
		})
	}
	hub.Publish(sessionID, SessionEvent{Type: "audit.appended", AuditID: event.AuditID, Kind: event.Kind})
}

func classifyModelFailure(err error, runCtx context.Context) ModelFailure {
	message := err.Error()
	switch {
	case errors.Is(runCtx.Err(), context.DeadlineExceeded):
		return ModelFailure{Code: "timeout", Detail: "provider exceeded MODEL_TIMEOUT"}
	case strings.HasPrefix(message, "malformed_stream"):
		return ModelFailure{Code: "malformed_stream", Detail: message}
	default:
		return ModelFailure{Code: "provider_error", Detail: message}
	}
}
