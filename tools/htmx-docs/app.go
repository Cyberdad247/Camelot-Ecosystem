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

	// N200: Agent-Native Surface Routes
	mux.HandleFunc("/api/agent/dump", agentDumpHandler)
	mux.HandleFunc("/api/agent/doc/", agentDocHandler)

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
