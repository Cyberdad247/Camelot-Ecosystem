package providers

import (
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"
)

// TinyTTSProvider integrates the Cyberdad247/tiny-tts model into the Go omnirouter
type TinyTTSProvider struct {
	Cwd string
}

// NewTinyTTSProvider builds a new TinyTTS provider with the specified working directory
func NewTinyTTSProvider(cwd string) *TinyTTSProvider {
	return &TinyTTSProvider{Cwd: cwd}
}

// Name satisfies orchestration.Provider
func (p *TinyTTSProvider) Name() string { return "TinyTTS" }

// Invoke satisfies orchestration.Provider — runs speech synthesis using the local tiny-tts package
func (p *TinyTTSProvider) Invoke(ctx context.Context, knight, intent, _ string) (string, error) {
	text := strings.TrimSpace(intent)
	if text == "" {
		return "ERR: empty text for speech synthesis", nil
	}

	venvPython := filepath.Join(p.Cwd, ".venv", "Scripts", "python.exe")
	
	// Create outputs directory
	outputsDir := filepath.Join(p.Cwd, "infer_outputs")
	
	// Execute python snippet to trigger speech synthesis
	cmd := exec.CommandContext(ctx, venvPython, "-c", fmt.Sprintf(`
import os
os.makedirs(%q, exist_ok=True)
try:
    from tiny_tts import TinyTTS
    tts = TinyTTS()
    # Download checkpoints on demand if missing
    tts.speak(%q, output_path=%q)
    print("SUCCESS")
except Exception as e:
    print("ERROR:", str(e))
`, outputsDir, text, filepath.Join(outputsDir, "output.wav")))

	cmd.Dir = p.Cwd

	out, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Sprintf("[TinyTTS/%s] Execution failed: %v. Output: %s", knight, err, string(out)), nil
	}

	res := strings.TrimSpace(string(out))
	if strings.HasPrefix(res, "ERROR:") {
		return fmt.Sprintf("[TinyTTS/%s] Synthesis error: %s", knight, res), nil
	}

	return fmt.Sprintf("[TinyTTS/%s] Synthesized text successfully to: %s", knight, filepath.Join(outputsDir, "output.wav")), nil
}
