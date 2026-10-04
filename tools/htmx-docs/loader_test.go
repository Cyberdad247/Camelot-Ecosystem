package htmxdocs

import (
	"os"
	"strings"
	"testing"
)

// N100: Loader Tests - Verifying N002 Contract Compliance
func TestLoadAndRenderDoc_Valid(t *testing.T) {
	// The getting-started document was created earlier and has valid front matter
	html, err := LoadAndRenderDoc("getting-started")
	if err != nil {
		t.Fatalf("Expected valid document to load successfully, got error: %v", err)
	}
	
	if !strings.Contains(html, "DOC-001") {
		t.Errorf("Expected HTML fragment to contain ID 'DOC-001', got: %s", html)
	}
}

func TestLoadAndRenderDoc_InvalidFrontMatter(t *testing.T) {
	// Create a temporary markdown file that violates Wave 0 (No Front Matter)
	badFilePath := "docs/invalid-test.md"
	os.WriteFile(badFilePath, []byte("# I have no front matter\nAnd I should fail N002 validation."), 0644)
	defer os.Remove(badFilePath) // Cleanup

	_, err := LoadAndRenderDoc("invalid-test")
	if err == nil {
		t.Fatalf("FATAL: Loader allowed a document without Front Matter. N002 Contract Violated!")
	}
	
	if !strings.Contains(err.Error(), "N002 Contract Violation") {
		t.Errorf("Expected specific N002 violation error, got: %v", err)
	}
}
