package htmxdocs

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"path/filepath"
	"regexp"
	"strings"
	"sync"

	"github.com/yuin/goldmark"
	meta "github.com/yuin/goldmark-meta"
	"github.com/yuin/goldmark/parser"
)

// DocumentMeta stores the parsed front matter and N030 integrity hash.
type DocumentMeta struct {
	ID    string   `json:"id"`
	Title string   `json:"title"`
	Slug  string   `json:"slug"`
	Tags  []string `json:"tags"`
	Hash  string   `json:"hash"` // N030
}

var (
	// SearchIndex fulfills N050 (VCL Ledger)
	SearchIndex []DocumentMeta
	// InvertedIndex maps words -> slices of Slugs for O(1) Search (N111)
	InvertedIndex map[string]map[string]DocumentMeta
	indexMutex    sync.RWMutex
)

func tokenize(text string) []string {
	text = strings.ToLower(text)
	re := regexp.MustCompile(`[a-z0-9]+`)
	return re.FindAllString(text, -1)
}

// InitSearchIndex parses all markdown files on startup or fsnotify triggers
func InitSearchIndex() error {
	indexMutex.Lock()
	defer indexMutex.Unlock()

	SearchIndex = []DocumentMeta{}
	InvertedIndex = make(map[string]map[string]DocumentMeta)

	files, err := fs.Glob(DocsFS, "docs/*.md")
	if err != nil {
		return err
	}

	markdown := goldmark.New(goldmark.WithExtensions(meta.Meta))

	for _, file := range files {
		content, err := DocsFS.ReadFile(filepath.ToSlash(file))
		if err != nil {
			continue
		}

		hashBytes := sha256.Sum256(content)
		hashStr := hex.EncodeToString(hashBytes[:])

		var buf bytes.Buffer
		context := parser.NewContext()
		markdown.Convert(content, &buf, parser.WithContext(context))

		metaData := meta.Get(context)
		if metaData == nil || metaData["id"] == nil || metaData["title"] == nil {
			continue
		}

		slug := strings.TrimSuffix(filepath.Base(file), ".md")
		var tags []string
		if rawTags, ok := metaData["tags"].([]interface{}); ok {
			for _, t := range rawTags {
				tags = append(tags, fmt.Sprint(t))
			}
		}

		doc := DocumentMeta{
			ID:    fmt.Sprint(metaData["id"]),
			Title: fmt.Sprint(metaData["title"]),
			Slug:  slug,
			Tags:  tags,
			Hash:  hashStr,
		}
		SearchIndex = append(SearchIndex, doc)

		// N111: Populate Inverted Index
		tokens := append(tokenize(doc.Title), tags...)
		for _, token := range tokens {
			if InvertedIndex[token] == nil {
				InvertedIndex[token] = make(map[string]DocumentMeta)
			}
			InvertedIndex[token][slug] = doc
		}
	}
	return nil
}

// N051: Search API Endpoint
func searchHandler(w http.ResponseWriter, r *http.Request) {
	query := strings.ToLower(r.FormValue("q"))

	w.Header().Set("Content-Type", "text/html")
	if query == "" {
		w.Write([]byte(""))
		return
	}

	indexMutex.RLock()
	defer indexMutex.RUnlock()

	// Find matches in O(1) or via O(k) substring over the smaller token dictionary
	matchedDocs := make(map[string]DocumentMeta)
	
	// Quick O(k) prefix/substring search across the dictionary keys
	for token, docs := range InvertedIndex {
		if strings.Contains(token, query) {
			for slug, doc := range docs {
				matchedDocs[slug] = doc
			}
		}
	}

	// N203: Content Negotiation for Agents
	if r.Header.Get("Accept") == "application/json" {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(matchedDocs)
		return
	}

	var results []string
	for _, doc := range matchedDocs {
		res := fmt.Sprintf(`<li><a href="#" hx-get="/docs/%s" hx-target="#content" hx-push-url="true">%s <span style="font-size: 0.7em; color: var(--text-secondary);">[%s]</span></a></li>`, doc.Slug, doc.Title, doc.ID)
		results = append(results, res)
	}

	if len(results) == 0 {
		w.Write([]byte("<li style='color: var(--text-secondary);'>No matching documents found.</li>"))
		return
	}

	w.Write([]byte(strings.Join(results, "\n")))
}

// N032: VCL Endpoint
func vclHandler(w http.ResponseWriter, r *http.Request) {
	indexMutex.RLock()
	defer indexMutex.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status": "VCL Active",
		"count":  len(SearchIndex),
		"index":  SearchIndex,
	})
}
