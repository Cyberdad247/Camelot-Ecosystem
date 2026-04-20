// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"sync"
	"time"
)

// HIVEMIND v1.0 - The Agentic Orchestrator
// Part of Phase 5: THE AGENTIC CRUSADE

type Task struct {
	ID      string `json:"id"`
	Command string `json:"command"`
	Type    string `json:"type"` // e.g., "FORGE", "SENTINEL", "SQUIRE"
}

type TaskResult struct {
	TaskID   string `json:"task_id"`
	Status   string `json:"status"`
	Output   string `json:"output"`
	Duration string `json:"duration"`
}

type SwarmRequest struct {
	Objective string   `json:"objective"`
	Phases    []string `json:"phases"` // e.g., ["build", "audit", "lint"]
}

func main() {
	http.HandleFunc("/dispatch", handleDispatch)
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "HIVEMIND_ONLINE")
	})

	port := "8081"
	fmt.Printf("⚔️  [HIVEMIND] Orchestrator ignited on port %s...\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func handleDispatch(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Use POST", http.StatusMethodNotAllowed)
		return
	}

	var req SwarmRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	fmt.Printf("🚀 [HIVEMIND] New Objective: %s\n", req.Objective)

	// Execute Phases in Parallel (Map-Reduce)
	var wg sync.WaitGroup
	results := make(chan TaskResult, len(req.Phases))
	start := time.Now()

	for _, phase := range req.Phases {
		wg.Add(1)
		go func(p string) {
			defer wg.Done()
			results <- executePhase(p, req.Objective)
		}(phase)
	}

	wg.Wait()
	close(results)

	var finalResults []TaskResult
	for res := range results {
		finalResults = append(finalResults, res)
	}

	duration := time.Since(start)
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"objective": req.Objective,
		"results":   finalResults,
		"total_ms":  duration.Milliseconds(),
		"status":    "RADIANT",
	})
}

func executePhase(phase, objective string) TaskResult {
	start := time.Now()
	fmt.Printf("🛡️  [SWARM] Activating Phase: %s\n", phase)

	var output string
	var status string = "SUCCESS"

	// Mapping Phases to Kinetic/Python commands
	switch phase {
	case "build":
		// Example: Call Sir Forge (Python or Go)
		output = "[FORGE] Simulated build pass. Logic verified."
	case "audit":
		// Example: Call Sir Sentinel (Trivy)
		output = "[SENTINEL] Simulated audit pass. No vulnerabilities found."
	case "lint":
		// Example: Call Squire Clean (Biome/Ruff)
		output = "[SQUIRE] Simulated lint pass. Code aesthetic is high."
	case "reason":
		// PHASE 5: Call Merlin Agent Swarm (Python Bridge)
		cmdStr := fmt.Sprintf("python 01_KERNEL/swarms/merlin_agent_swarm.py --task \"%s\"", objective)
		out, err := runCommand(cmdStr)
		if err != nil {
			status = "FAILURE"
			output = fmt.Sprintf("Merlin Error: %v", err)
		} else {
			output = out
		}
	default:
		status = "SKIPPED"
		output = "Unknown phase"
	}

	// Simulate work delay
	time.Sleep(500 * time.Millisecond)

	return TaskResult{
		TaskID:   phase,
		Status:   status,
		Output:   output,
		Duration: fmt.Sprintf("%v", time.Since(start)),
	}
}

func runCommand(cmdStr string) (string, error) {
	cmd := exec.Command("powershell", "-Command", cmdStr)
	out, err := cmd.CombinedOutput()
	return string(out), err
}