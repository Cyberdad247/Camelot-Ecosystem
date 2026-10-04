package htmxdocs

import (
	"fmt"
	"net/http"
	"strings"
)

func healthzHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("200 OK - Backend Core Online (Vercel Edge Ready)"))
}

func docsHandler(w http.ResponseWriter, r *http.Request) {
	slug := strings.TrimPrefix(r.URL.Path, "/docs/")
	if slug == "" {
		slug = "getting-started"
	}

	state := GetSearchState()
	var docHash string
	if state != nil {
		if meta, ok := state.DocBySlug[slug]; ok {
			docHash = meta.Hash
		}
	}

	// Phase 1: Edge ETag Caching (304 Not Modified when hash matches)
	if docHash != "" {
		etag := fmt.Sprintf(`"%s"`, docHash)
		if match := r.Header.Get("If-None-Match"); match == etag || match == docHash {
			w.WriteHeader(http.StatusNotModified)
			return
		}
		w.Header().Set("ETag", etag)
		w.Header().Set("Cache-Control", "public, max-age=3600, stale-while-revalidate=86400")
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

func mcpHandler(w http.ResponseWriter, r *http.Request) {
	cmd := strings.ToUpper(r.FormValue("cmd"))
	w.Header().Set("Content-Type", "text/html")
	if strings.HasPrefix(cmd, "//") {
		w.Write([]byte(fmt.Sprintf(`<p style="color: #38bdf8; font-weight: bold;">[DISPATCHING]: %s</p><p>Assimilating Worldtree context... Vercel Edge active. Self-enhancing canonical documents.</p>`, cmd)))
	} else {
		w.Write([]byte(fmt.Sprintf(`<p style="color: #ef4444;">Syntax Error: '%s' is invalid. Prefix with '//' for Runic Symbolect execution.</p>`, r.FormValue("cmd"))))
	}
}
