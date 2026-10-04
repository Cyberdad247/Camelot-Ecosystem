package main

import (
	"fmt"
	"log"
	"net/http"
	htmxdocs "htmx-docs"
)

func main() {
	htmxdocs.StartFileWatcher()
	app := htmxdocs.NewApp()

	port := ":8484"
	fmt.Printf("[N013] Bare-Metal Backend Core booting on port %s...\n", port)
	log.Fatal(http.ListenAndServe(port, app))
}
