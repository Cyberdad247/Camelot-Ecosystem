package htmxdocs

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// TestCloudBrainSearch_HTML verifies HTMX hypermedia responses with origin badges
func TestCloudBrainSearch_HTML(t *testing.T) {
	_ = InitSearchIndex()

	req := httptest.NewRequest("POST", "/api/cloudbrain/search?q=getting", nil)
	rec := httptest.NewRecorder()
	cloudbrainSearchHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("Expected 200 OK, got: %d", rec.Code)
	}

	html := rec.Body.String()
	if !strings.Contains(html, "CANONICAL") {
		t.Fatalf("Expected HTML response to contain CANONICAL origin badge, got: %s", html)
	}
}

// TestCloudBrainSearch_JSON verifies agent content negotiation
func TestCloudBrainSearch_JSON(t *testing.T) {
	_ = InitSearchIndex()

	req := httptest.NewRequest("POST", "/api/cloudbrain/search?q=arch", nil)
	req.Header.Set("Accept", "application/json")
	rec := httptest.NewRecorder()
	cloudbrainSearchHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("Expected 200 OK, got: %d", rec.Code)
	}

	var resp UnifiedSearchResponse
	if err := json.Unmarshal(rec.Body.Bytes(), &resp); err != nil {
		t.Fatalf("Failed to parse JSON response: %v", err)
	}

	if resp.TotalHits == 0 {
		t.Fatalf("Expected at least 1 hit for 'arch', got 0")
	}

	foundCanonical := false
	for _, item := range resp.Results {
		if item.Source == "canonical" {
			foundCanonical = true
		}
	}

	if !foundCanonical {
		t.Errorf("Expected canonical match in unified search results")
	}
}

// TestCloudBrainSearch_ScopeFilter verifies filtering by scope
func TestCloudBrainSearch_ScopeFilter(t *testing.T) {
	_ = InitSearchIndex()

	// 1. Canonical only
	req := httptest.NewRequest("POST", "/api/cloudbrain/search?q=gpu&scope=canonical", nil)
	req.Header.Set("Accept", "application/json")
	rec := httptest.NewRecorder()
	cloudbrainSearchHandler(rec, req)

	var respCanonical UnifiedSearchResponse
	_ = json.Unmarshal(rec.Body.Bytes(), &respCanonical)
	for _, item := range respCanonical.Results {
		if item.Source != "canonical" {
			t.Errorf("Expected only canonical results, got: %s", item.Source)
		}
	}

	// 2. CloudBrain only
	reqCB := httptest.NewRequest("POST", "/api/cloudbrain/search?q=anya&scope=cloudbrain", nil)
	reqCB.Header.Set("Accept", "application/json")
	recCB := httptest.NewRecorder()
	cloudbrainSearchHandler(recCB, reqCB)

	var respCB UnifiedSearchResponse
	_ = json.Unmarshal(recCB.Body.Bytes(), &respCB)
	if respCB.TotalHits == 0 {
		t.Fatalf("Expected CloudBrain matches for 'anya'")
	}
	for _, item := range respCB.Results {
		if item.Source != "cloudbrain" {
			t.Errorf("Expected only cloudbrain results, got: %s", item.Source)
		}
	}
}

// TestCloudBrainStatus verifies health telemetry endpoint
func TestCloudBrainStatus(t *testing.T) {
	req := httptest.NewRequest("GET", "/api/cloudbrain/status", nil)
	rec := httptest.NewRecorder()
	cloudbrainStatusHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("Expected 200 OK, got: %d", rec.Code)
	}

	var status map[string]interface{}
	if err := json.Unmarshal(rec.Body.Bytes(), &status); err != nil {
		t.Fatalf("Failed to parse status JSON: %v", err)
	}

	if status["status"] != "ONLINE" {
		t.Errorf("Expected status ONLINE, got: %v", status["status"])
	}
}
