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
					{
						"name": "search_cloudbrain",
						"description": "Unified semantic search over Camelot Canonical Docs, MemCastle KNN vectors, and Knight Cloudbrains",
						"parameters": map[string]interface{}{
							"type": "object",
							"properties": map[string]interface{}{
								"query":  map[string]interface{}{"type": "string", "description": "Search query or natural language prompt"},
								"scope":  map[string]interface{}{"type": "string", "enum": []string{"all", "canonical", "cloudbrain", "memcastle"}, "description": "Search scope filter"},
								"knight": map[string]interface{}{"type": "string", "description": "Target Knight Persona (e.g., ANYA_OMEGA, SIR_BORIS)"},
							},
							"required": []string{"query"},
						},
					},
					{
						"name": "cloudbrain_status",
						"description": "Retrieve live telemetry for connected CloudBrain and MemCastle engines",
						"parameters": map[string]interface{}{
							"type": "object",
							"properties": map[string]interface{}{},
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
