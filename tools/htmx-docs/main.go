package main

import (
	"fmt"
	"log"
	"net/http"
	"strings"
)

// N071: System Health Verification
func healthzHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("200 OK - Backend Core Online"))
}

// N070: Document Content Loader
func docsHandler(w http.ResponseWriter, r *http.Request) {
	slug := strings.TrimPrefix(r.URL.Path, "/docs/")
	if slug == "" {
		slug = "getting-started"
	}

	htmlFragment, err := LoadAndRenderDoc(slug)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		w.Header().Set("Content-Type", "text/html")
		w.Write([]byte(fmt.Sprintf("<div style='color: #ef4444; padding: 2rem; border: 1px solid #ef4444; border-radius: 4px;'><h3>N011 Error</h3><p>%s</p></div>", err.Error())))
		return
	}

	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(htmlFragment))
}

// VCL Handler mapped from search.go

func main() {
	// N050: Initialize Search & VCL Index
	if err := InitSearchIndex(); err != nil {
		log.Fatalf("Failed to initialize search index: %v", err)
	}

	// N111: Start Stateful Synchronization Watcher
	StartFileWatcher()

	// N013: Server Multiplexer Initialization
	mux := http.NewServeMux()

	// Register Wave 0 Contract Routes
	mux.HandleFunc("/healthz", healthzHandler)
	mux.HandleFunc("/docs/", docsHandler)
	mux.HandleFunc("/api/vcl", vclHandler)
	mux.HandleFunc("/api/search", searchHandler) // N051

	// N112: Master UI/UX Cartridge (MCP Interface)
	mux.HandleFunc("/api/mcp", func(w http.ResponseWriter, r *http.Request) {
		cmd := strings.ToUpper(r.FormValue("cmd"))
		w.Header().Set("Content-Type", "text/html")
		if strings.HasPrefix(cmd, "//") {
			w.Write([]byte(fmt.Sprintf(`<p style="color: #38bdf8; font-weight: bold;">[DISPATCHING]: %s</p><p>Assimilating Worldtree context... GPU tensor cores active. Self-enhancing canonical documents.</p>`, cmd)))
		} else {
			w.Write([]byte(fmt.Sprintf(`<p style="color: #ef4444;">Syntax Error: '%s' is invalid. Prefix with '//' for Runic Symbolect execution.</p>`, r.FormValue("cmd"))))
		}
	})

	// N023: Serve static assets
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	// N020: Application Shell (Index)
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		http.ServeFile(w, r, "templates/index.html")
	})

	port := ":8484"
	fmt.Printf("[N013] WP-A Backend Core booting on port %s...\n", port)
	
	// Start HTTP Server
	if err := http.ListenAndServe(port, mux); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
