package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// Durable local effects. This is the first code in the slice that changes
// something outside the process, so it is deliberately the narrowest thing
// that can still be called a real effect.
//
// THE PATH IS NOT AN INPUT. A skill cannot ask to write "somewhere"; the
// store derives it from the skill id and the LEASE id under a fixed root,
// both server-controlled. An allow-list is a check you can forget to apply —
// an absent parameter cannot be attacked. The containment assertion below is
// belt-and-braces for a future caller that passes an untrusted id.

var (
	ErrEffectTooLarge = errors.New("note exceeds the size cap")
	ErrEffectEmpty    = errors.New("note is empty")
	ErrEffectEscape   = errors.New("derived path escaped the artifact root")
	ErrEffectExists   = errors.New("a governed artifact already exists for this lease; artifacts are write-once")
	ErrEffectUnleased = errors.New("durable effect reached the store without a lease id")
)

// maxNoteBytes caps one note. Small on purpose: the point is to prove the
// governed path end to end, not to become a document store.
const maxNoteBytes = 4096

type EffectStore struct {
	root  string
	runID string
}

func NewEffectStore(root string) *EffectStore {
	return &EffectStore{root: root, runID: newRunID()}
}

// newRunID disambiguates artifacts across gateway restarts. Lease ids restart
// at lease-0001 every process, but .run/artifacts persists — without this, the
// first governed write after a restart would collide with the previous run's
// and be refused as a duplicate.
func newRunID() string {
	var b [4]byte
	if _, err := rand.Read(b[:]); err != nil {
		return strconv.FormatInt(time.Now().UnixNano(), 16)
	}
	return hex.EncodeToString(b[:])
}

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
//
// Both inputs are server-controlled now (a manifest skill id and a minted
// lease id), so the lossy mapping cannot alias two distinct callers' names —
// it remains as a containment backstop, not as the primary defence.
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

// WriteNote writes content to <root>/<skillID>/<runID>-<leaseID>.txt
// atomically and exactly once.
//
// THE NAME COMES FROM THE LEASE, NOT THE TURN. A turn id is client-supplied:
// two browser tabs, a page reload, or a hostile caller can all reuse one, and
// with a write-once rule that means a client can pre-claim a name and
// permanently block future governed writes. A lease id is minted by the
// policy kernel, is unique per authorized action, and cannot be chosen by the
// caller — so each authorization gets exactly one artifact and no
// authorization can collide with another.
//
// Atomicity matters for a governed effect: the lease has already been
// consumed by the time we get here, so a half-written file would be an
// un-repeatable partial action. Write to a temp file, fsync, then hard-link
// into place — link is atomic AND refuses to replace an existing artifact.
func (e *EffectStore) WriteNote(skillID, leaseID, content string) (EffectResult, error) {
	if strings.TrimSpace(leaseID) == "" {
		// Durable ⇒ effectful ⇒ lease-gated. Reaching here without one means
		// the broker's ordering was bypassed.
		return EffectResult{}, ErrEffectUnleased
	}
	body := strings.TrimSpace(content)
	if body == "" {
		return EffectResult{}, ErrEffectEmpty
	}
	if len(body) > maxNoteBytes {
		return EffectResult{}, fmt.Errorf("%w: %d > %d bytes", ErrEffectTooLarge, len(body), maxNoteBytes)
	}

	dir := filepath.Join(e.root, safeSegment(skillID))
	dest := filepath.Join(dir, e.runID+"-"+safeSegment(leaseID)+".txt")

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
	// With lease-derived names this should be unreachable: one authorization
	// mints one lease id, and the single-use rule stops that lease acting
	// twice. It stays as a backstop, because the failure it prevents —
	// silently destroying the evidence of a prior approved action — is the
	// kind that leaves no trace of having happened.
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
