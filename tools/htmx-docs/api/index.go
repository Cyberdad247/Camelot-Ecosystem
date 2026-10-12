package handler

import (
	"net/http"
	htmxdocs "htmx-docs/pkg/htmxdocs"
)

var app = htmxdocs.NewApp()

func Handler(w http.ResponseWriter, r *http.Request) {
	app.ServeHTTP(w, r)
}
