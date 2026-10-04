package htmxdocs

import (
	"encoding/json"
	"net/http"
)

// N210: WebMCP Manifest
// Exposes the documentation site's capabilities as a native Model Context Protocol (MCP) server.
func mcpManifestHandler(w http.ResponseWriter, r *http.Request) {
	manifest := map[string]interface{}{
		"mcpServers": map[string]interface{}{
			"camelot-worldtree-docs": map[string]interface{}{
				"version": "1.0.0",
				"description": "Living Canonical Documents & Agent-Native Surface",
				"tools": []map[string]interface{}{
					{
						"name": "search_docs", // N212
						"description": "Semantic and keyword search over the Camelot ecosystem documents",
						"parameters": map[string]interface{}{
							"type": "object",
							"properties": map[string]interface{}{
								"query": map[string]interface{}{"type": "string", "description": "The search query"},
							},
							"required": []string{"query"},
						},
					},
					{
						"name": "get_doc", // N213
						"description": "Retrieve the full structured JSON/Markdown content of a specific document node",
						"parameters": map[string]interface{}{
							"type": "object",
							"properties": map[string]interface{}{
								"slug": map[string]interface{}{"type": "string", "description": "The document slug to retrieve"},
							},
							"required": []string{"slug"},
						},
					},
					{
						"name": "verify_doc_hash", // N216
						"description": "Verify a document's VCL signature against the ledger",
						"parameters": map[string]interface{}{
							"type": "object",
							"properties": map[string]interface{}{
								"slug": map[string]interface{}{"type": "string", "description": "The document slug to verify"},
							},
							"required": []string{"slug"},
						},
					},
				},
			},
		},
	}
	
	w.Header().Set("Content-Type", "application/json")
	// CORS headers to allow browser extensions (like Claude) to read the manifest
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
	json.NewEncoder(w).Encode(manifest)
}
