package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

func main() {
	if len(os.Args) < 2 || os.Args[1] != "log" {
		fmt.Println("Usage: ledger log --actor <actor> --action <action> --status <status>")
		os.Exit(1)
	}

	fs := flag.NewFlagSet("log", flag.ExitOnError)
	actor := fs.String("actor", "", "Actor name")
	action := fs.String("action", "", "Action performed")
	status := fs.String("status", "", "Execution status")

	// Parse flags starting from index 2
	if err := fs.Parse(os.Args[2:]); err != nil {
		fmt.Printf("Error parsing flags: %v\n", err)
		os.Exit(1)
	}

	if *actor == "" || *action == "" || *status == "" {
		fmt.Println("Error: --actor, --action, and --status are required")
		os.Exit(1)
	}

	// Format entry: | timestamp | actor | action | status |
	timestamp := time.Now().Format(time.RFC3339)
	entry := fmt.Sprintf("| %s | %s | %s | %s |\n", timestamp, *actor, *action, *status)

	// List of ledger paths to update
	ledgers := []string{
		"PROVENANCE_LEDGER.md",
		filepath.Join("03_VAULT", "PROVENANCE_LEDGER.md"),
		filepath.Join("docs", "PROVENANCE_LEDGER.md"),
		filepath.Join("03_VAULT", "training", "configs", "PROVENANCE_LEDGER.md"),
	}

	for _, path := range ledgers {
		// Ensure directory exists
		dir := filepath.Dir(path)
		if dir != "." {
			if err := os.MkdirAll(dir, 0755); err != nil {
				fmt.Printf("Error creating directory %s: %v\n", dir, err)
				continue
			}
		}

		// Append to file
		f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			fmt.Printf("Error opening ledger %s: %v\n", path, err)
			continue
		}
		
		// If file is not empty and doesn't end with newline, write one
		info, err := f.Stat()
		if err == nil && info.Size() > 0 {
			// Read last byte if possible (simplified: just append entry)
		}

		if _, err := f.WriteString(entry); err != nil {
			fmt.Printf("Error writing to ledger %s: %v\n", path, err)
		}
		f.Close()
	}

	fmt.Println("Successfully logged to provenance ledger and mirrors.")
}
