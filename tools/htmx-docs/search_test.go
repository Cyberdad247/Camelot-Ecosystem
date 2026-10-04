package main

import (
	"testing"
)

// N101: Search and VCL Integrity Tests
func TestSearchIndexIntegrity(t *testing.T) {
	err := InitSearchIndex()
	if err != nil {
		t.Fatalf("Failed to initialize search index: %v", err)
	}

	if len(SearchIndex) == 0 {
		t.Fatalf("Expected search index to contain documents, found 0")
	}

	// N030 Verification: Ensure cryptographic hashes are computed
	for _, doc := range SearchIndex {
		if doc.Hash == "" {
			t.Errorf("Document %s (%s) is missing its N030 SHA-256 integrity hash", doc.Title, doc.ID)
		}
		if len(doc.Hash) != 64 { // SHA-256 hex string is 64 characters
			t.Errorf("Document %s has an invalid hash length: %s", doc.ID, doc.Hash)
		}
	}
}
