package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// Durable local effects. This is the first code in the slice that changes
// something outside the process, so it is deliberately the narrowest thing
// that can still be called a real effect.
//
// THE PATH IS NOT AN INPUT. A skill cannot ask to write "somewhere"; the
// store derives the path from skillID + turnID under a fixed root. An
// allow-list is a check you can forget to apply — an absent parameter cannot
// be attacked. The containment assertion below is belt-and-braces for the
// case where a future caller passes an id from an untrusted source.

var (
	ErrEffectTooLarge = errors.New("note exceeds the size cap")
	ErrEffectEmpty    = errors.New("note is empty")
	ErrEffectEscape   = errors.New("derived path escaped the artifact root")
	ErrEffectExists   = errors.New("a governed artifact already exists for this turn; artifacts are write-once")
)

// maxNoteBytes caps one note. Small on purpose: the point is to prove the
// governed path end to end, not to become a document store.
const maxNoteBytes = 4096

type EffectStore struct {
	root string
}

func NewEffectStore(root string) *EffectStore { return &EffectStore{root: root} }

// EffectResult is what the audit record and the artifact summary report. The
// note body itself is never returned here — only its size and digest — so an
// effect can be proven to have happened without the content entering the log.
type EffectResult struct {
	RelPath string
	Bytes   int
	SHA256  string
}

// safeSegment reduces an identifier to a single path segment that cannot
// traverse. Everything outside [A-Za-z0-9._-] becomes '_', and a leading dot
// is neutralised so ".." can never survive.
func safeSegment(s string) string {
	var b strings.Builder
	for _, r := range s {
		switch {
		case r >= 'a' && r <= 'z', r >= 'A' && r <= 'Z', r >= '0' && r <= '9', r == '.', r == '_', r == '-':
			b.WriteRune(r)
		default:
			b.WriteByte('_')
		}
	}
	out := b.String()
	if out == "" {
		return "_"
	}
	if strings.HasPrefix(out, ".") {
		return "_" + out[1:]
	}
	return out
}

// WriteNote writes content to <root>/<skillID>/<turnID>.txt atomically and
// exactly once.
//
// Atomicity matters for a governed effect: the lease has already been
// consumed by the time we get here, so a half-written file would be an
// un-repeatable partial action. Write to a temp file, fsync, then hard-link
// into place — link is atomic AND refuses to replace an existing artifact.
func (e *EffectStore) WriteNote(skillID, turnID, content string) (EffectResult, error) {
	body := strings.TrimSpace(content)
	if body == "" {
		return EffectResult{}, ErrEffectEmpty
	}
	if len(body) > maxNoteBytes {
		return EffectResult{}, fmt.Errorf("%w: %d > %d bytes", ErrEffectTooLarge, len(body), maxNoteBytes)
	}

	dir := filepath.Join(e.root, safeSegment(skillID))
	dest := filepath.Join(dir, safeSegment(turnID)+".txt")

	// Containment assertion: the derived path must still be inside the root.
	rootAbs, err := filepath.Abs(e.root)
	if err != nil {
		return EffectResult{}, err
	}
	destAbs, err := filepath.Abs(dest)
	if err != nil {
		return EffectResult{}, err
	}
	if !strings.HasPrefix(destAbs, rootAbs+string(os.PathSeparator)) {
		return EffectResult{}, ErrEffectEscape
	}

	if err := os.MkdirAll(dir, 0o755); err != nil {
		return EffectResult{}, err
	}
	tmp, err := os.CreateTemp(dir, ".note-*")
	if err != nil {
		return EffectResult{}, err
	}
	tmpName := tmp.Name()
	defer os.Remove(tmpName) // no-op once renamed

	if _, err := tmp.WriteString(body); err != nil {
		tmp.Close()
		return EffectResult{}, err
	}
	if err := tmp.Sync(); err != nil {
		tmp.Close()
		return EffectResult{}, err
	}
	if err := tmp.Close(); err != nil {
		return EffectResult{}, err
	}

	// GOVERNED ARTIFACTS ARE WRITE-ONCE. Link fails with EEXIST rather than
	// clobbering, and unlike Rename it cannot silently replace a file.
	//
	// The single-use lease stops a LEASE from being replayed, but it cannot
	// stop a client re-submitting the same turn id and being issued a fresh
	// lease — which would overwrite the earlier artifact and destroy the
	// evidence of the first approved action. Refusing here means the second
	// attempt fails closed and is audited, and the original survives.
	if err := os.Link(tmpName, dest); err != nil {
		if errors.Is(err, os.ErrExist) {
			return EffectResult{}, fmt.Errorf("%w: %s", ErrEffectExists, filepath.Base(dest))
		}
		return EffectResult{}, err
	}

	sum := sha256.Sum256([]byte(body))
	rel, err := filepath.Rel(rootAbs, destAbs)
	if err != nil {
		rel = dest
	}
	return EffectResult{RelPath: rel, Bytes: len(body), SHA256: hex.EncodeToString(sum[:])}, nil
}
