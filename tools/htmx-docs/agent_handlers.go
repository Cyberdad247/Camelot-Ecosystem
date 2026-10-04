package htmxdocs

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

// N201: Context Consolidation (LLM Infinite Context Dump)
// Phase 2 & Phase 3: Lock-free chunked streaming with ETag caching.
// Flushes node-by-node directly to the client socket without buffering in heap.
func agentDumpHandler(w http.ResponseWriter, r *http.Request) {
	state := GetSearchState()
	if state == nil {
		http.Error(w, "Search state uninitialized", http.StatusInternalServerError)
		return
	}

	// Phase 1: Edge ETag check on entire corpus
	if state.AggregateHash != "" {
		etag := fmt.Sprintf(`"%s"`, state.AggregateHash)
		if match := r.Header.Get("If-None-Match"); match == etag || match == state.AggregateHash {
			w.WriteHeader(http.StatusNotModified)
			return
		}
		w.Header().Set("ETag", etag)
	}

	w.Header().Set("Content-Type", "text/markdown; charset=utf-8")
	w.Header().Set("Transfer-Encoding", "chunked")
	w.Header().Set("Cache-Control", "public, max-age=300, stale-while-revalidate=1200")
	w.Header().Set("X-Content-Type-Options", "nosniff")

	flusher, canFlush := w.(http.Flusher)

	// Stream header
	w.Write([]byte("# CAMELOT WORLD_TREE: AGENT-NATIVE CONTEXT DUMP\n\n"))
	if canFlush {
		flusher.Flush()
	}

	// Phase 3: Stream each document chunk directly into network buffer
	for _, meta := range state.SearchIndex {
		w.Write([]byte(fmt.Sprintf("## %s [%s]\n", meta.Title, meta.ID)))
		content, err := DocsFS.ReadFile("docs/" + meta.Slug + ".md")
		if err == nil {
			w.Write(content)
		}
		w.Write([]byte("\n\n---\n\n"))
		if canFlush {
			flusher.Flush()
		}
	}
}

// N202: Headless JSON Document Retrieval
// Phase 1 & Phase 2: Lock-free retrieval with 304 ETag caching.
func agentDocHandler(w http.ResponseWriter, r *http.Request) {
	slug := strings.TrimPrefix(r.URL.Path, "/api/agent/doc/")
	state := GetSearchState()

	var docHash string
	if state != nil {
		if meta, ok := state.DocBySlug[slug]; ok {
			docHash = meta.Hash
		}
	}

	// Phase 1: Edge ETag Caching
	if docHash != "" {
		etag := fmt.Sprintf(`"%s"`, docHash)
		if match := r.Header.Get("If-None-Match"); match == etag || match == docHash {
			w.WriteHeader(http.StatusNotModified)
			return
		}
		w.Header().Set("ETag", etag)
		w.Header().Set("Cache-Control", "public, max-age=3600, stale-while-revalidate=86400")
	}

	// Fast memory fetch from embedded FS
	content, err := DocsFS.ReadFile("docs/" + slug + ".md")
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		w.Write([]byte(`{"error": "Agent Document Request Failed: Target Node Not Found"}`))
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"node":    slug,
		"hash":    docHash,
		"status":  "assimilated",
		"content": string(content),
	})
}
