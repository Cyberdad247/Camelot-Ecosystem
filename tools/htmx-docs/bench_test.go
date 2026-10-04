package htmxdocs

import (
	"testing"
)

// N104: Performance Benchmarks
// Tests how fast the AST parser can read, validate, and render an HTMX fragment.
func BenchmarkLoadAndRenderDoc(b *testing.B) {
	for i := 0; i < b.N; i++ {
		_, err := LoadAndRenderDoc("getting-started")
		if err != nil {
			b.Fatalf("Benchmark failed on render: %v", err)
		}
	}
}
