package htmxdocs

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// TestScalability_Phase1_ETag verifies Edge 304 Not Modified caching on documents and VCL ledger
func TestScalability_Phase1_ETag(t *testing.T) {
	if err := InitSearchIndex(); err != nil {
		t.Fatalf("InitSearchIndex failed: %v", err)
	}

	state := GetSearchState()
	if state == nil || len(state.SearchIndex) == 0 {
		t.Fatalf("SearchState is empty or nil")
	}

	firstDoc := state.SearchIndex[0]
	if firstDoc.Hash == "" {
		t.Fatalf("First document has empty hash")
	}

	// 1. Initial request without ETag -> Expect 200 OK + ETag header
	req := httptest.NewRequest("GET", "/docs/"+firstDoc.Slug, nil)
	rec := httptest.NewRecorder()
	docsHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("Expected 200 OK, got %d", rec.Code)
	}
	etag := rec.Header().Get("ETag")
	if etag == "" {
		t.Fatalf("Expected non-empty ETag header")
	}
	cacheControl := rec.Header().Get("Cache-Control")
	if !strings.Contains(cacheControl, "max-age") {
		t.Fatalf("Expected Cache-Control header, got: %s", cacheControl)
	}

	// 2. Conditional request with matching If-None-Match -> Expect 304 Not Modified
	reqCond := httptest.NewRequest("GET", "/docs/"+firstDoc.Slug, nil)
	reqCond.Header.Set("If-None-Match", etag)
	recCond := httptest.NewRecorder()
	docsHandler(recCond, reqCond)

	if recCond.Code != http.StatusNotModified {
		t.Fatalf("Expected 304 Not Modified on matching ETag, got: %d", recCond.Code)
	}
}

// TestScalability_Phase2_LockFree verifies atomic.Pointer search state operations under concurrency
func TestScalability_Phase2_LockFree(t *testing.T) {
	state := GetSearchState()
	if state == nil {
		t.Fatalf("Expected non-nil atomic SearchState")
	}

	// Concurrently query without mutex blocking
	done := make(chan bool)
	for i := 0; i < 20; i++ {
		go func() {
			for j := 0; j < 50; j++ {
				s := GetSearchState()
				if s == nil || len(s.SearchIndex) == 0 {
					t.Errorf("Concurrent read returned empty state")
				}
			}
			done <- true
		}()
	}

	for i := 0; i < 20; i++ {
		<-done
	}
}

// TestScalability_Phase3_ChunkedStreaming verifies /api/agent/dump streams properly
func TestScalability_Phase3_ChunkedStreaming(t *testing.T) {
	req := httptest.NewRequest("GET", "/api/agent/dump", nil)
	rec := httptest.NewRecorder()
	agentDumpHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("Expected 200 OK, got %d", rec.Code)
	}

	body := rec.Body.String()
	if !strings.Contains(body, "# CAMELOT WORLD_TREE: AGENT-NATIVE CONTEXT DUMP") {
		t.Fatalf("Expected agent dump header in output")
	}
}
