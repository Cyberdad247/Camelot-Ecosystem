package htmxdocs
import "embed"

//go:embed docs/*.md
var DocsFS embed.FS

//go:embed templates/*
var TemplatesFS embed.FS

//go:embed static/*
var StaticFS embed.FS
