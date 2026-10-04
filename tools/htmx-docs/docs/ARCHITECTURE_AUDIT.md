# System Architecture Audit: EVD-HTMX-SITE-001

## 1. Overview and Baseline Strengths
The current architecture (Go + HTMX + Bare Metal) provides a phenomenally lightweight and performant baseline. 
* **Zero JS Payload:** By leveraging HTMX, the client downloads ~14KB of JavaScript instead of a multi-megabyte SPA bundle.
* **CPU Efficiency:** The Go AST parser renders markdown to HTML in ~0.36ms, allowing a single core to process over 2,700 requests per second.
* **Security & Integrity:** The VCL (Verification Control List) enforces strict cryptographic hashing (SHA-256) of all loaded documents, ensuring supply chain and runtime integrity.

However, as the documentation site scales from hundreds to tens of thousands of documents, several architectural bottlenecks will emerge.

---

## 2. Architectural Recommendations (The N111 Arthur Resolution)

### A. The Disk I/O Bottleneck (Caching Strategy)
> [!WARNING] High Risk at Scale
> Currently, every time a user clicks a link, the `LoadAndRenderDoc` function reads the `.md` file directly from the SSD and re-parses the AST. 

**The Problem:** While SSDs are fast, Disk I/O is still orders of magnitude slower than RAM. Under high concurrent load, reading from disk on every HTTP request will cause thread blocking and CPU thrashing.
**The Fix:** Implement an **In-Memory LRU (Least Recently Used) Cache** or a `sync.Map`. Since documents are mostly static, rendering the HTML fragment once and storing it in RAM will drop response times from 0.36ms down to nanoseconds.

### B. Search Algorithm Complexity (O(N) vs Inverted Index)
> [!TIP] Performance Optimization
> The current search implementation loops through an array of all documents and runs a substring match (`strings.Contains`). This is an `O(N)` linear time operation.

**The Problem:** If we have 10,000 documents, searching for "deployment" requires checking 10,000 titles and tags on every single keystroke.
**The Fix:** Build an **Inverted Index** on startup (similar to how Elasticsearch or Lucene works). Map individual words to document IDs (e.g., `"deploy" -> [DOC-001, DOC-042]`). This turns search into an `O(1)` hash map lookup, keeping the API lightning fast regardless of document volume.

### C. Stateful Synchronization (File Watching)
> [!NOTE] Developer Experience / Ops
> The `SearchIndex` and VCL hashes are only computed when the Go binary boots. 

**The Problem:** If a technical writer updates `getting-started.md` on the server, the new content will render (since it reads from disk), but the Search Index and VCL hashes will be out of sync until the server is restarted.
**The Fix:** Integrate the `fsnotify` Go library to actively watch the `docs/` directory for filesystem events. When a file is modified, dynamically rebuild that document's AST, update the cache, and recalculate its VCL hash without dropping the server.

### D. Network Resilience & Rate Limiting
> [!CAUTION] Security Vulnerability
> HTMX relies heavily on network requests to mutate the DOM. We added a `delay:500ms` debounce to the search input, but a malicious script could bypass this and hammer the `/api/search` endpoint.

**The Problem:** Without a database, our backend is fast, but it is entirely unprotected against application-layer DDoS attacks that exhaust the HTTP multiplexer pool.
**The Fix:** Implement a **Token Bucket Rate Limiter** middleware in Go, or configure Caddy to limit requests to 50 req/sec per IP address.

### E. Accessibility (A11Y) for DOM Swapping
> [!IMPORTANT] UX Requirement
> When HTMX swaps the `#content` div, visually able users see the change instantly. Screen readers, however, do not know the DOM was mutated.

**The Problem:** Blind or visually impaired users will click a sidebar link and hear nothing, assuming the site is broken.
**The Fix:** Add `aria-live="polite"` to the `<main id="content">` and `<ul id="search-results">` containers. This instructs the browser's accessibility tree to announce the new text whenever HTMX injects new HTML.
