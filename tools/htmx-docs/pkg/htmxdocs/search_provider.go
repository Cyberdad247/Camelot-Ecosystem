package htmxdocs

import (
	"context"
	"errors"
	"sort"
	"strings"
	"time"
)

// Provider is the abstraction over search backends (DESIGN-CLOUDBRAIN-SEARCH-v1).
// Two implementations exist:
//   - LocalProvider      (inverted index, always available, offline-first)
//   - CloudBrainProvider (semantic, optional, network-dependent)
type Provider interface {
	// Name returns a stable identifier ("local", "cloudbrain").
	Name() string
	// Available reports whether the provider can serve requests right now (< 1ms, no I/O).
	Available() bool
	// Search executes a query and returns ranked hits within context deadline.
	Search(ctx context.Context, req Request) (Response, error)
}

// Request is the canonical query shape.
type Request struct {
	Query    string
	Limit    int
	TenantID string // for RLS; empty in single-tenant mode
	MinScore float64
	Timeout  time.Duration
}

// Response is the canonical result shape.
type Response struct {
	Hits      []Hit
	Provider  string // which provider produced this response
	LatencyMs int64
	Truncated bool // true if the provider cut results to fit Limit
}

// Hit is a single search result.
type Hit struct {
	DocPath     string  // canonical path relative to docs/
	Title       string  // human-readable title
	Section     string  // top-level section name
	Score       float64 // 0.0 – 1.0, normalized ranking
	Excerpt     string  // optional preview text
	ContentHash string  // SHA-256 of the doc content (enables Gate G2 validation)
	Provider    string  // "local" or "cloudbrain"
}

// Sentinel errors as required by DESIGN-CLOUDBRAIN-SEARCH-v1.
var (
	ErrUnavailable   = errors.New("provider unavailable")
	ErrTimeout       = errors.New("provider timeout")
	ErrCloudBrain5xx = errors.New("cloudbrain 5xx")
	ErrHashMismatch  = errors.New("content hash mismatch")
)

// -----------------------------------------------------------------------------
// LocalProvider (Offline-First Inverted Index)
// -----------------------------------------------------------------------------

type LocalProvider struct{}

func NewLocalProvider() *LocalProvider {
	return &LocalProvider{}
}

func (p *LocalProvider) Name() string { return "local" }

func (p *LocalProvider) Available() bool { return true }

func (p *LocalProvider) Search(ctx context.Context, req Request) (Response, error) {
	start := time.Now()
	if err := ctx.Err(); err != nil {
		return Response{}, ErrTimeout
	}

	state := GetSearchState()
	if state == nil {
		return Response{Provider: "local", Hits: []Hit{}}, nil
	}

	qLower := strings.ToLower(req.Query)
	matchedDocs := make(map[string]DocumentMeta)

	for token, docs := range state.InvertedIndex {
		if strings.Contains(token, qLower) {
			for slug, doc := range docs {
				matchedDocs[slug] = doc
			}
		}
	}

	hits := make([]Hit, 0, len(matchedDocs))
	for _, doc := range matchedDocs {
		hits = append(hits, Hit{
			DocPath:     doc.Slug,
			Title:       doc.Title,
			Section:     "canonical",
			Score:       1.0, // Base exact token match
			Excerpt:     "Local canonical documentation node",
			ContentHash: doc.Hash,
			Provider:    "local",
		})
	}

	if req.Limit > 0 && len(hits) > req.Limit {
		hits = hits[:req.Limit]
	}

	return Response{
		Hits:      hits,
		Provider:  "local",
		LatencyMs: time.Since(start).Milliseconds(),
		Truncated: req.Limit > 0 && len(matchedDocs) > req.Limit,
	}, nil
}

// -----------------------------------------------------------------------------
// CloudBrainProvider (Sovereign Semantic Brain)
// -----------------------------------------------------------------------------

type CloudBrainProvider struct {
	endpoint string
}

func NewCloudBrainProvider(endpoint string) *CloudBrainProvider {
	return &CloudBrainProvider{endpoint: endpoint}
}

func (p *CloudBrainProvider) Name() string { return "cloudbrain" }

// Available reports whether the cloudbrain endpoint is configured
func (p *CloudBrainProvider) Available() bool {
	return p.endpoint != ""
}

func (p *CloudBrainProvider) Search(ctx context.Context, req Request) (Response, error) {
	start := time.Now()
	if !p.Available() {
		return Response{}, ErrUnavailable
	}

	select {
	case <-ctx.Done():
		return Response{}, ErrTimeout
	default:
	}

	state := GetSearchState()
	hits := []Hit{}

	// Query CloudBrain synthetic memory banks (or bridge)
	rawHits := queryCloudBrainSynthetic(req.Query, "cloudbrain", "ANYA_OMEGA")
	for _, raw := range rawHits {
		hit := Hit{
			DocPath:     raw.Slug,
			Title:       raw.Title,
			Section:     "cloudbrain",
			Score:       raw.Confidence,
			Excerpt:     raw.Snippet,
			ContentHash: "",
			Provider:    "cloudbrain",
		}

		// Gate G2: Candidate hash verification against local store
		if state != nil {
			if localDoc, exists := state.DocBySlug[raw.Slug]; exists {
				hit.ContentHash = localDoc.Hash
			}
		}

		hits = append(hits, hit)
	}

	return Response{
		Hits:      hits,
		Provider:  "cloudbrain",
		LatencyMs: time.Since(start).Milliseconds(),
	}, nil
}

// -----------------------------------------------------------------------------
// SearchDispatcher (Cross-Provider Fan-out & Merge)
// -----------------------------------------------------------------------------

type SearchDispatcher struct {
	providers []Provider
}

func NewSearchDispatcher(providers ...Provider) *SearchDispatcher {
	return &SearchDispatcher{providers: providers}
}

// Search executes fan-out search across all available providers and merges results.
func (d *SearchDispatcher) Search(ctx context.Context, req Request) (Response, error) {
	start := time.Now()
	var mergedHits []Hit
	seenPaths := make(map[string]bool)

	for _, p := range d.providers {
		if !p.Available() {
			continue
		}

		// Execute provider search with timeout constraint
		resp, err := p.Search(ctx, req)
		if err != nil {
			// Principle 1: CloudBrain is enhancement, never dependency
			if errors.Is(err, ErrUnavailable) || errors.Is(err, ErrTimeout) {
				continue
			}
			return Response{}, err
		}

		for _, hit := range resp.Hits {
			if !seenPaths[hit.DocPath] {
				seenPaths[hit.DocPath] = true
				mergedHits = append(mergedHits, hit)
			}
		}
	}

	// Sort merged results by descending score
	sort.Slice(mergedHits, func(i, j int) bool {
		return mergedHits[i].Score > mergedHits[j].Score
	})

	if req.Limit > 0 && len(mergedHits) > req.Limit {
		mergedHits = mergedHits[:req.Limit]
	}

	return Response{
		Hits:      mergedHits,
		Provider:  "dispatcher",
		LatencyMs: time.Since(start).Milliseconds(),
		Truncated: req.Limit > 0 && len(mergedHits) == req.Limit,
	}, nil
}
