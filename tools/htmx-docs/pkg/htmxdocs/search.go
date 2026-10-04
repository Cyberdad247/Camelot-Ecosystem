package htmxdocs

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"path/filepath"
	"regexp"
	"strings"
	"sync/atomic"

	"github.com/yuin/goldmark"
	meta "github.com/yuin/goldmark-meta"
	"github.com/yuin/goldmark/parser"
)

// DocumentMeta stores the parsed front matter and N030 integrity hash.
type DocumentMeta struct {
	ID    string   `json:"id"`
	Title string   `json:"title"`
	Slug  string   `json:"slug"`
	Tags  []string `json:"tags"`
	Hash  string   `json:"hash"` // N030
}

// SearchState holds an immutable snapshot of search and VCL structures for lock-free reads.
type SearchState struct {
	SearchIndex   []DocumentMeta
	InvertedIndex map[string]map[string]DocumentMeta
	DocBySlug     map[string]DocumentMeta
	AggregateHash string
}

var (
	// Backward-compatible exports
	SearchIndex   []DocumentMeta
	InvertedIndex map[string]map[string]DocumentMeta

	// Phase 2: Lock-free atomic state snapshot (Copy-On-Write)
	searchState atomic.Pointer[SearchState]
)

// GetSearchState returns the current immutable snapshot without locks.
func GetSearchState() *SearchState {
	s := searchState.Load()
	if s == nil {
		_ = InitSearchIndex()
		s = searchState.Load()
	}
	return s
}

func tokenize(text string) []string {
	text = strings.ToLower(text)
	re := regexp.MustCompile(`[a-z0-9]+`)
	return re.FindAllString(text, -1)
}

// InitSearchIndex parses all markdown files on startup or fsnotify triggers
func InitSearchIndex() error {
	newSearchIndex := []DocumentMeta{}
	newInvertedIndex := make(map[string]map[string]DocumentMeta)
	newDocBySlug := make(map[string]DocumentMeta)

	files, err := fs.Glob(DocsFS, "docs/*.md")
	if err != nil {
		return err
	}

	markdown := goldmark.New(goldmark.WithExtensions(meta.Meta))
	aggregateHasher := sha256.New()

	for _, file := range files {
		content, err := DocsFS.ReadFile(filepath.ToSlash(file))
		if err != nil {
			continue
		}

		hashBytes := sha256.Sum256(content)
		hashStr := hex.EncodeToString(hashBytes[:])
		aggregateHasher.Write(hashBytes[:])

		var buf bytes.Buffer
		context := parser.NewContext()
		markdown.Convert(content, &buf, parser.WithContext(context))

		metaData := meta.Get(context)
		if metaData == nil || metaData["id"] == nil || metaData["title"] == nil {
			continue
		}

		slug := strings.TrimSuffix(filepath.Base(file), ".md")
		var tags []string
		if rawTags, ok := metaData["tags"].([]interface{}); ok {
			for _, t := range rawTags {
				tags = append(tags, fmt.Sprint(t))
			}
		}

		doc := DocumentMeta{
			ID:    fmt.Sprint(metaData["id"]),
			Title: fmt.Sprint(metaData["title"]),
			Slug:  slug,
			Tags:  tags,
			Hash:  hashStr,
		}
		newSearchIndex = append(newSearchIndex, doc)
		newDocBySlug[slug] = doc

		// N111: Populate Inverted Index
		tokens := append(tokenize(doc.Title), tags...)
		for _, token := range tokens {
			if newInvertedIndex[token] == nil {
				newInvertedIndex[token] = make(map[string]DocumentMeta)
			}
			newInvertedIndex[token][slug] = doc
		}
	}

	aggHashStr := hex.EncodeToString(aggregateHasher.Sum(nil))

	newState := &SearchState{
		SearchIndex:   newSearchIndex,
		InvertedIndex: newInvertedIndex,
		DocBySlug:     newDocBySlug,
		AggregateHash: aggHashStr,
	}

	// Phase 2: Atomic pointer swap (0-contention read snapshot)
	searchState.Store(newState)

	// Keep backward-compatible globals in sync
	SearchIndex = newSearchIndex
	InvertedIndex = newInvertedIndex

	return nil
}

// N051: Search API Endpoint (Lock-Free)
func searchHandler(w http.ResponseWriter, r *http.Request) {
	query := strings.ToLower(r.FormValue("q"))

	w.Header().Set("Content-Type", "text/html")
	if query == "" {
		w.Write([]byte(""))
		return
	}

	state := GetSearchState()
	if state == nil {
		w.Write([]byte("<li style='color: var(--text-secondary);'>Index unavailable.</li>"))
		return
	}

	// Find matches in O(1) or via O(k) substring over the smaller token dictionary
	matchedDocs := make(map[string]DocumentMeta)
	
	// Quick O(k) prefix/substring search across the dictionary keys without locks
	for token, docs := range state.InvertedIndex {
		if strings.Contains(token, query) {
			for slug, doc := range docs {
				matchedDocs[slug] = doc
			}
		}
	}

	// N203: Content Negotiation for Agents
	if r.Header.Get("Accept") == "application/json" {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(matchedDocs)
		return
	}

	var results []string
	for _, doc := range matchedDocs {
		res := fmt.Sprintf(`<li><a href="#" hx-get="/docs/%s" hx-target="#content" hx-push-url="true">%s <span style="font-size: 0.7em; color: var(--text-secondary);">[%s]</span></a></li>`, doc.Slug, doc.Title, doc.ID)
		results = append(results, res)
	}

	if len(results) == 0 {
		w.Write([]byte("<li style='color: var(--text-secondary);'>No matching documents found.</li>"))
		return
	}

	w.Write([]byte(strings.Join(results, "\n")))
}

// N032: VCL Endpoint with Phase 1 Edge ETag Caching
func vclHandler(w http.ResponseWriter, r *http.Request) {
	state := GetSearchState()
	if state == nil {
		http.Error(w, `{"error":"index uninitialized"}`, http.StatusInternalServerError)
		return
	}

	// Phase 1: Edge ETag Caching on VCL Ledger
	if state.AggregateHash != "" {
		etag := fmt.Sprintf(`"%s"`, state.AggregateHash)
		if match := r.Header.Get("If-None-Match"); match == etag || match == state.AggregateHash {
			w.WriteHeader(http.StatusNotModified)
			return
		}
		w.Header().Set("ETag", etag)
		w.Header().Set("Cache-Control", "public, max-age=60, stale-while-revalidate=600")
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":         "VCL Active",
		"aggregate_hash": state.AggregateHash,
		"count":          len(state.SearchIndex),
		"index":          state.SearchIndex,
	})
}
