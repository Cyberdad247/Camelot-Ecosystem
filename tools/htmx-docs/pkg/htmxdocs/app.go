package htmxdocs

import (
	"log"
	"net/http"
)

func NewApp() http.Handler {
	if err := InitSearchIndex(); err != nil {
		log.Printf("Failed to initialize search index: %v", err)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", healthzHandler)
	mux.HandleFunc("/docs/", docsHandler)
	mux.HandleFunc("/api/vcl", vclHandler)
	mux.HandleFunc("/api/search", searchHandler)
	mux.HandleFunc("/api/mcp", mcpHandler)

	// WP-G: WebMCP Surface
	mux.HandleFunc("/.well-known/mcp.json", mcpManifestHandler)
	mux.HandleFunc("/api/mcp/manifest", mcpManifestHandler)

	// N200: Agent-Native Surface Routes
	mux.HandleFunc("/api/agent/dump", agentDumpHandler)
	mux.HandleFunc("/api/agent/doc/", agentDocHandler)

	// CloudBrain Search & Telemetry Endpoints
	mux.HandleFunc("/api/cloudbrain/search", cloudbrainSearchHandler)
	mux.HandleFunc("/api/cloudbrain/status", cloudbrainStatusHandler)

	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.FS(StaticFS))))
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		content, _ := TemplatesFS.ReadFile("templates/index.html")
		w.Header().Set("Content-Type", "text/html")
		w.Write(content)
	})

	return mux
}
