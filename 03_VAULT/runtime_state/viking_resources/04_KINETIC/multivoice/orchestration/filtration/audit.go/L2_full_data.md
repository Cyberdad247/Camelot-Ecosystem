# [L2_FULL_DATA: audit.go]
# [PROTOCOL: OPENVIKING_DEEP_DIVE]

```
package filtration

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"path/filepath"

	_ "github.com/mattn/go-sqlite3"
)

func LogAuditTrail(modelID, policyID, validationState, backend string) {
	dbPath := "/var/camelot/world_tree.db"
	
	// Ensure directory structure exists (Expand-Migrate-Contract)
	dir := filepath.Dir(dbPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		log.Printf("[FATAL] Could not create database directory: %v", err)
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		log.Printf("[FATAL] Could not open World Tree: %v", err)
		return
	}
	defer db.Close()

	// Ensure table exists (Expand-Migrate-Contract)
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS inference_audit_trail (
			audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
			timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			model_id TEXT,
			policy_id TEXT,
			validation_state TEXT,
			backend TEXT
		);
		PRAGMA journal_mode=WAL;
	`)
	if err != nil {
		log.Printf("[FATAL] Migration failed: %v", err)
		return
	}

	_, err = db.Exec(`INSERT INTO inference_audit_trail (model_id, policy_id, validation_state, backend) VALUES (?, ?, ?, ?)`,
		modelID, policyID, validationState, backend)
	
	if err != nil {
		log.Printf("[FATAL] Audit log failed: %v", err)
	} else {
		fmt.Println("[LADY_ALEXANDRIA] Routing decision permanently engraved in World Tree.")
	}
}

```
