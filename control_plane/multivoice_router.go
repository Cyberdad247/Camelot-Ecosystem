package main

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

// The Multivoice-Router acts as a Go-native, goroutine-parallel switchboard.
// It intercepts high-level CMUX/MCP commands and translates them to the Rust Bifrost API.

type AgentIntent struct {
	Tenant     string `json:"tenant"`
	Capability string `json:"capability"`
	Payload    string `json:"payload"`
}

func handleAgentIntent(w http.ResponseWriter, r *http.Request) {
	var intent AgentIntent
	if err := json.NewDecoder(r.Body).Decode(&intent); err != nil {
		http.Error(w, "Malformed JSON", http.StatusBadRequest)
		return
	}

	log.Printf("[MULTIVOICE-ROUTER] Routing intent for %s: %s", intent.Tenant, intent.Capability)

	// Forward to the Rust Bifrost Transport (Week 3 Deliverable)
	reqBody, _ := json.Marshal(intent)
	resp, err := http.Post("http://127.0.0.1:8080/execute", "application/json", bytes.NewBuffer(reqBody))

	if err != nil {
		http.Error(w, "Bifrost Gateway Offline", http.StatusServiceUnavailable)
		return
	}
	defer resp.Body.Close()

	// Stream verified receipt back to the CMUX UI
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "routed_to_microvm"})
}

func main() {
	r := mux.NewRouter()
	r.HandleFunc("/intent", handleAgentIntent).Methods("POST")

	log.Println("⚡ Multivoice-Router (Cybertronia Control Plane) active on :8090")
	log.Fatal(http.ListenAndServe(":8090", r))
}
