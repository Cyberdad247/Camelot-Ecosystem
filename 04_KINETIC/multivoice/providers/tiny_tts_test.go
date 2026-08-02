package providers

import (
	"context"
	"strings"
	"testing"
)

func TestTinyTTSProvider_Contracts(t *testing.T) {
	p := NewTinyTTSProvider(".")
	if p.Name() != "TinyTTS" {
		t.Errorf("expected provider name TinyTTS, got %s", p.Name())
	}

	// Invoke with empty string should immediately return an error message
	res, err := p.Invoke(context.Background(), "sir_sonus", "", "")
	if err != nil {
		t.Fatalf("unexpected invocation error: %v", err)
	}
	if !strings.HasPrefix(res, "ERR:") {
		t.Errorf("expected error message prefix for empty input, got %s", res)
	}
}
