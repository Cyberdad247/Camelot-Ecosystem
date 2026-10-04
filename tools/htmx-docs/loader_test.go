package htmxdocs

import (
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
	// Mock the file reader to return bad markdown
	originalReader := fileReader
	fileReader = func(name string) ([]byte, error) {
		if name == "docs/invalid-test.md" {
			return []byte("# I have no front matter\nAnd I should fail N002 validation."), nil
		}
		return originalReader(name)
	}
	defer func() { fileReader = originalReader }()

	_, err := LoadAndRenderDoc("invalid-test")
	if err == nil {
		t.Fatalf("FATAL: Loader allowed a document without Front Matter. N002 Contract Violated!")
	}
	
	if !strings.Contains(err.Error(), "N002 Contract Violation") {
		t.Errorf("Expected specific N002 violation error, got: %v", err)
	}
}
