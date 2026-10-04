package api

import (
	"net/http"
	htmxdocs "htmx-docs"
)

var app = htmxdocs.NewApp()

func Handler(w http.ResponseWriter, r *http.Request) {
	app.ServeHTTP(w, r)
}
