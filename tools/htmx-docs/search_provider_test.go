package htmxdocs

import (
	"context"
	"errors"
	"testing"
	"time"
)

// TestSearchProvider_Local verifies LocalProvider compliance with Provider interface
func TestSearchProvider_Local(t *testing.T) {
	_ = InitSearchIndex()

	local := NewLocalProvider()
	if local.Name() != "local" {
		t.Errorf("Expected Name 'local', got: %s", local.Name())
	}
	if !local.Available() {
		t.Errorf("LocalProvider must always be available")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	resp, err := local.Search(ctx, Request{Query: "getting", Limit: 5})
	if err != nil {
		t.Fatalf("Local search failed: %v", err)
	}

	if len(resp.Hits) == 0 {
		t.Errorf("Expected at least 1 hit for 'getting'")
	}
	for _, h := range resp.Hits {
		if h.ContentHash == "" {
			t.Errorf("Hit is missing required ContentHash for Gate G2 verification")
		}
		if h.Provider != "local" {
			t.Errorf("Expected provider 'local', got %s", h.Provider)
		}
	}
}

// TestSearchProvider_OfflineFirst verifies Principle 1 (CloudBrain optional)
func TestSearchProvider_OfflineFirst(t *testing.T) {
	_ = InitSearchIndex()

	// Empty endpoint = offline/disabled
	cb := NewCloudBrainProvider("")
	if cb.Available() {
		t.Errorf("CloudBrain with empty endpoint must report Available() == false")
	}

	ctx := context.Background()
	_, err := cb.Search(ctx, Request{Query: "test"})
	if !errors.Is(err, ErrUnavailable) {
		t.Errorf("Expected ErrUnavailable, got: %v", err)
	}

	// Dispatcher must gracefully proceed with LocalProvider alone
	dispatcher := NewSearchDispatcher(NewLocalProvider(), cb)
	resp, err := dispatcher.Search(ctx, Request{Query: "arch", Limit: 10})
	if err != nil {
		t.Fatalf("Dispatcher failed when CloudBrain unavailable: %v", err)
	}
	if len(resp.Hits) == 0 {
		t.Errorf("Dispatcher failed to return local hits")
	}
}
