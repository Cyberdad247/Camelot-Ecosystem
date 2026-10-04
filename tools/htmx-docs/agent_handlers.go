package htmxdocs

import (
	"encoding/json"
	"net/http"
	"strings"
)

// N201: Context Consolidation (LLM Infinite Context Dump)
// Concatenates all documents into a single raw Markdown stream optimized for LLM Context Windows.
func agentDumpHandler(w http.ResponseWriter, r *http.Request) {
	indexMutex.RLock()
	defer indexMutex.RUnlock()

	w.Header().Set("Content-Type", "text/markdown")
	var sb strings.Builder
	sb.WriteString("# CAMELOT WORLD_TREE: AGENT-NATIVE CONTEXT DUMP\n\n")

	for _, meta := range SearchIndex {
		sb.WriteString("## " + meta.Title + " [" + meta.ID + "]\n")
		// Extract raw file directly from the go:embed memory filesystem
		content, err := DocsFS.ReadFile("docs/" + meta.Slug + ".md")
		if err == nil {
			sb.Write(content)
		}
		sb.WriteString("\n\n---\n\n")
	}
	w.Write([]byte(sb.String()))
}

// N202: Headless JSON Document Retrieval
// Allows autonomous agents to retrieve exact documents in structured JSON, bypassing HTMX UI fragments.
func agentDocHandler(w http.ResponseWriter, r *http.Request) {
	slug := strings.TrimPrefix(r.URL.Path, "/api/agent/doc/")
	
	// Fast memory fetch
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
		"status":  "assimilated",
		"content": string(content),
	})
}
