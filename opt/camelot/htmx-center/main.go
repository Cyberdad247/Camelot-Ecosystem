package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

// ==========================================================
// Data structures for dynamic panels
// ==========================================================
type SystemStatus struct {
	Status string  `json:"status"` // "CONVERGED", "DEGRADED", "DIVERGED"
	CPU    float64 `json:"cpu"`
	Memory float64 `json:"memory"`
}

type Task struct {
	ID     string `json:"id"`
	Title  string `json:"title"`
	Status string `json:"status"` // "pending", "running", "approved"
	Risk   string `json:"risk"`
}

type Receipt struct {
	ID     string `json:"id"`
	Action string `json:"action"`
	Time   string `json:"time"`
	Hash   string `json:"hash"`
}

// ==========================================================
// Global state (simulated for demo; in production, connect to Bifrost)
// ==========================================================
var (
	status = SystemStatus{Status: "CONVERGED", CPU: 42.5, Memory: 3.2}
	tasks  = []Task{
		{ID: "task_001", Title: "Draft response to Jane", Status: "approved", Risk: "R4"},
		{ID: "task_002", Title: "Create campaign plan", Status: "running", Risk: "R2"},
		{ID: "task_003", Title: "Review invoice", Status: "pending", Risk: "R3"},
	}
	receipts = []Receipt{
		{ID: "0x9f4a", Action: "email.draft.created", Time: "10:23:11", Hash: "sha256:4f9d...e201"},
		{ID: "0x7c21", Action: "approval.granted", Time: "10:24:32", Hash: "sha256:1a8c...90b4"},
	}
	mu sync.Mutex
)

// ==========================================================
// HTML Template for main page
// ==========================================================
var indexTmpl = template.Must(template.ParseFiles("static/index.html"))

func main() {
	// Serve static files
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	// Main page
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		indexTmpl.Execute(w, nil)
	})

	// HTMX fragments (dynamic panels)
	http.HandleFunc("/fragments/status", statusFragment)
	http.HandleFunc("/fragments/tasks", tasksFragment)
	http.HandleFunc("/fragments/receipts", receiptsFragment)

	// SSE endpoint for real-time updates
	http.HandleFunc("/stream", sseHandler)

	log.Println("⚜️ Camelot HTMX Center listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

// ==========================================================
// Fragment Handlers
// ==========================================================

func statusFragment(w http.ResponseWriter, r *http.Request) {
	mu.Lock()
	defer mu.Unlock()
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, `
        <div id="status-panel" class="panel">
            <h2>Throne Room</h2>
            <p>System: <span class="status %s">%s</span></p>
            <p>CPU: %.1f%%</p>
            <p>Memory: %.1f GB</p>
        </div>
    `, status.Status, status.Status, status.CPU, status.Memory)
}

func tasksFragment(w http.ResponseWriter, r *http.Request) {
	mu.Lock()
	defer mu.Unlock()
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, `<div id="tasks-panel" class="panel">`)
	fmt.Fprintf(w, `<h2>Round Table</h2><ul>`)
	for _, t := range tasks {
		fmt.Fprintf(w, `<li data-task-id="%s">%s - <span class="risk">%s</span> [%s]</li>`, t.ID, t.Title, t.Risk, t.Status)
	}
	fmt.Fprintf(w, `</ul></div>`)
}

func receiptsFragment(w http.ResponseWriter, r *http.Request) {
	mu.Lock()
	defer mu.Unlock()
	w.Header().Set("Content-Type", "text/html")
	fmt.Fprintf(w, `<div id="receipts-panel" class="panel">`)
	fmt.Fprintf(w, `<h2>Ledger</h2><table><tr><th>ID</th><th>Action</th><th>Time</th></tr>`)
	for _, rec := range receipts {
		fmt.Fprintf(w, `<tr><td>%s</td><td>%s</td><td>%s</td></tr>`, rec.ID, rec.Action, rec.Time)
	}
	fmt.Fprintf(w, `</table></div>`)
}

// ==========================================================
// SSE Handler (simulated real-time updates)
// ==========================================================

func sseHandler(w http.ResponseWriter, r *http.Request) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	// Send initial state
	sendSSE(w, flusher, "status", status)
	sendSSE(w, flusher, "tasks", tasks)
	sendSSE(w, flusher, "receipts", receipts)

	// Simulate periodic updates (every 5 seconds)
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-r.Context().Done():
			return
		case <-ticker.C:
			mu.Lock()
			status.CPU = randomFloat(20, 90)
			status.Memory = randomFloat(2, 6)
			mu.Unlock()

			sendSSE(w, flusher, "status", status)
		}
	}
}

func sendSSE(w http.ResponseWriter, flusher http.Flusher, event string, data interface{}) {
	jsonData, _ := json.Marshal(data)
	fmt.Fprintf(w, "event: %s\n", event)
	fmt.Fprintf(w, "data: %s\n\n", jsonData)
	flusher.Flush()
}

func randomFloat(min, max float64) float64 {
	return min + (max-min)*rand.Float64()
}
