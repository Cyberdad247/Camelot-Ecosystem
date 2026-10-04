package main

import (
	"log"
	"path/filepath"
	"strings"

	"github.com/fsnotify/fsnotify"
)

// N111: StartFileWatcher monitors the docs directory for changes
func StartFileWatcher() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Printf("Failed to initialize file watcher: %v", err)
		return
	}

	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				// Rebuild index and clear cache on writes or creates
				if event.Has(fsnotify.Write) || event.Has(fsnotify.Create) {
					if strings.HasSuffix(event.Name, ".md") {
						slug := strings.TrimSuffix(filepath.Base(event.Name), ".md")
						
						// Invalidate AST Cache
						docCache.Delete(slug)
						
						// Rebuild Search & VCL Index
						if err := InitSearchIndex(); err != nil {
							log.Printf("Failed to rebuild index after file change: %v", err)
						} else {
							log.Printf("[N111 Watcher] Hot-reloaded document: %s", slug)
						}
					}
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				log.Printf("Watcher error: %v", err)
			}
		}
	}()

	err = watcher.Add("docs")
	if err != nil {
		log.Printf("Failed to watch docs directory: %v", err)
	} else {
		log.Println("[N111] Stateful Synchronization (fsnotify) active on docs/")
	}
}
