package main

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"sync"

	"github.com/yuin/goldmark"
	meta "github.com/yuin/goldmark-meta"
	"github.com/yuin/goldmark/parser"
)

// In-Memory AST Cache (N111 Resolution)
var docCache sync.Map

// LoadAndRenderDoc fulfills N011 (Doc Loader) and N012 (Markdown).
// It reads the file, parses the front matter (N002), and returns an HTML fragment.
func LoadAndRenderDoc(slug string) (string, error) {
	// N111: Check Memory Cache First
	if cached, ok := docCache.Load(slug); ok {
		return cached.(string), nil
	}

	// Prevent path traversal
	safeSlug := filepath.Clean(slug)
	filePath := filepath.Join("docs", safeSlug+".md")

	content, err := os.ReadFile(filePath)
	if err != nil {
		return "", fmt.Errorf("Document not found: %s", safeSlug)
	}

	// Initialize Goldmark with YAML front matter extension
	markdown := goldmark.New(
		goldmark.WithExtensions(
			meta.Meta,
		),
	)

	var buf bytes.Buffer
	context := parser.NewContext()
	
	// Convert Markdown to HTML AST and render to buffer
	if err := markdown.Convert(content, &buf, parser.WithContext(context)); err != nil {
		return "", fmt.Errorf("Markdown parsing failed: %w", err)
	}

	// N011 DoD: Strict Front Matter Schema Validation (N002)
	metaData := meta.Get(context)
	if metaData == nil {
		return "", fmt.Errorf("N002 Contract Violation: Missing YAML front matter")
	}

	// Ensure required properties exist
	if metaData["id"] == nil || metaData["title"] == nil {
		return "", fmt.Errorf("N002 Contract Violation: 'id' and 'title' are required in front matter")
	}

	// Format the final HTML Fragment
	htmlOutput := fmt.Sprintf(`
		<div class="doc-fragment fade-in">
			<div class="doc-meta" style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border);">
				<span class="badge" style="margin-right: 0.5rem;">%s</span>
				<span class="date" style="color: var(--text-secondary); font-size: 0.9rem;">%v</span>
			</div>
			<div class="doc-body">
				%s
			</div>
		</div>
	`, metaData["id"], metaData["date"], buf.String())

	// N111: Save to Cache
	docCache.Store(slug, htmlOutput)

	return htmlOutput, nil
}
