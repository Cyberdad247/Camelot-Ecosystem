package main

import (
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// The first REAL side effect in the slice. These tests exist to prove the
// governance path holds when something actually happens — every prior
// effectful test guarded a hardcoded string.

func noteTurn(t *testing.T, srv *Server, turnID, transcript string) CamelotTurnResponse {
	t.Helper()
	body, _ := json.Marshal(VoiceTurn{
		SessionID: "sess-effect", TurnID: turnID, Modality: "text", Transcript: transcript,
	})
	req := httptest.NewRequest(http.MethodPost, "/v1/voice/turns", strings.NewReader(string(body)))
	rec := httptest.NewRecorder()
	srv.Handler().ServeHTTP(rec, req)

	var resp CamelotTurnResponse
	if err := json.Unmarshal(rec.Body.Bytes(), &resp); err != nil {
		t.Fatalf("decode turn response (status %d): %v — %s", rec.Code, err, rec.Body.String())
	}
	return resp
}

func notePath(root, turnID string) string {
	return filepath.Join(root, "notes.local.write", turnID+".txt")
}

// AC1: a valid lease produces the file AND an audit event carrying the result.
func TestGovernedWriteProducesFileAndAudit(t *testing.T) {
	root := t.TempDir()
	srv := NewServerWithEffectRoot(0, fixedNow, root)

	resp := noteTurn(t, srv, "turn-0001", "save a note about the staging rollout")

	if resp.Decision.Effect != "allow" || resp.Decision.SkillID != "notes.local.write" {
		t.Fatalf("unexpected decision: %+v", resp.Decision)
	}
	data, err := os.ReadFile(notePath(root, "turn-0001"))
	if err != nil {
		t.Fatalf("note was not written: %v", err)
	}
	if string(data) != "save a note about the staging rollout" {
		t.Fatalf("note content = %q", data)
	}

	event, ok := srv.audit.Get(resp.AuditID)
	if !ok {
		t.Fatal("no audit event for the write")
	}
	// The audit proves the effect happened, by size and digest...
	if !strings.Contains(event.RedactedSummary, "bytes") {
		t.Fatalf("audit does not record the effect result: %q", event.RedactedSummary)
	}
	// ...without reproducing the note body (tier 2 -> redactTranscript).
	if strings.Contains(event.RedactedSummary, "staging rollout") {
		t.Fatalf("audit leaked the note body: %q", event.RedactedSummary)
	}
	if event.TranscriptSHA256 == "" {
		t.Fatal("audit should carry the transcript hash")
	}
}

// AC2: a bad lease produces NO file and an auditable denial.
func TestRefusedLeaveNoFileAndAreAudited(t *testing.T) {
	root := t.TempDir()
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases, NewEffectStore(root))

	// Wrong capability: a lease for another skill must not write this note.
	lease := leases.Issue("sess", "turn-0002", "skill:deployment.review.prepare", true)
	_, _, err := broker.Execute("notes.local.write", "turn-0002", "secret", &lease)
	if !errors.Is(err, ErrLeaseCapMatch) {
		t.Fatalf("want ErrLeaseCapMatch, got %v", err)
	}
	if _, statErr := os.Stat(notePath(root, "turn-0002")); !os.IsNotExist(statErr) {
		t.Fatal("a refused write still created a file")
	}

	// No lease at all.
	_, _, err = broker.Execute("notes.local.write", "turn-0003", "secret", nil)
	if !errors.Is(err, ErrLeaseRequired) {
		t.Fatalf("want ErrLeaseRequired, got %v", err)
	}
	if _, statErr := os.Stat(notePath(root, "turn-0003")); !os.IsNotExist(statErr) {
		t.Fatal("an unleased write still created a file")
	}
}

// AC2 (server half): the denial reaches the audit log, not just the caller.
// Previously a refused execution returned 403 and left no record at all.
func TestRefusedExecutionIsAudited(t *testing.T) {
	srv := NewServerWithEffectRoot(0, fixedNow, t.TempDir())
	before := srv.audit.Len()

	// Over the size cap: the lease is issued and CONSUMED, then the effect
	// itself refuses. This is the interesting half — the failure happens
	// after the authorization, which is exactly when a silent 403 would have
	// left no trace.
	resp := noteTurn(t, srv, "turn-0004", "save a note "+strings.Repeat("x", maxNoteBytes))

	if srv.audit.Len() <= before {
		t.Fatal("a refused execution produced no audit event")
	}
	last := srv.audit.events[srv.audit.Len()-1]
	if last.Kind != "tool.refused" {
		t.Fatalf("last audit kind = %q, want tool.refused (resp: %+v)", last.Kind, resp.Decision)
	}
	if last.Decision == nil || last.Decision.Effect != "deny" {
		t.Fatalf("refusal was not recorded as a denial: %+v", last.Decision)
	}
}

// AC3: the single-use lease IS the idempotency key. This is the
// "effect succeeded but the response was lost" case: a replay must not write
// a second time, and must fail at the lease rather than at the effect.
func TestReplayedEffectfulRequestCannotWriteTwice(t *testing.T) {
	root := t.TempDir()
	leases := NewLeaseStore(fixedNow)
	broker := NewToolBroker(leases, NewEffectStore(root))
	lease := leases.Issue("sess", "turn-0005", "skill:notes.local.write", true)

	if _, _, err := broker.Execute("notes.local.write", "turn-0005", "first write", &lease); err != nil {
		t.Fatalf("first write failed: %v", err)
	}
	info, err := os.Stat(notePath(root, "turn-0005"))
	if err != nil {
		t.Fatalf("first write produced no file: %v", err)
	}
	firstModTime := info.ModTime()

	// Replay with the very same lease material.
	_, _, err = broker.Execute("notes.local.write", "turn-0005", "SECOND write", &lease)
	if !errors.Is(err, ErrLeaseConsumed) {
		t.Fatalf("replay: want ErrLeaseConsumed, got %v", err)
	}
	data, _ := os.ReadFile(notePath(root, "turn-0005"))
	if string(data) != "first write" {
		t.Fatalf("replay overwrote the note: %q", data)
	}
	if after, _ := os.Stat(notePath(root, "turn-0005")); !after.ModTime().Equal(firstModTime) {
		t.Fatal("replay touched the file")
	}
}

// AC4: the broker is the only way in. The effect store is reachable from the
// broker; nothing in the HTTP surface exposes it.
func TestEffectRequiresTheBroker(t *testing.T) {
	root := t.TempDir()
	srv := NewServerWithEffectRoot(0, fixedNow, root)

	// There is no route that names the effect store, a path, or a skill id.
	for _, path := range []string{
		"/v1/effects", "/v1/notes", "/v1/skills/notes.local.write",
		"/v1/artifacts", "/v1/effects/write",
	} {
		rec := httptest.NewRecorder()
		srv.Handler().ServeHTTP(rec, httptest.NewRequest(http.MethodPost, path, nil))
		if rec.Code != http.StatusNotFound && rec.Code != http.StatusMethodNotAllowed {
			t.Fatalf("%s is reachable (status %d) — effects must only be brokered", path, rec.Code)
		}
	}
}

// AC5: the chain still detects tampering once an effect record is in it.
func TestAuditChainCoversTheEffectRecord(t *testing.T) {
	srv := NewServerWithEffectRoot(0, fixedNow, t.TempDir())
	noteTurn(t, srv, "turn-0006", "read staging status")          // tier 1
	noteTurn(t, srv, "turn-0007", "save a note about the window") // durable

	if srv.audit.Len() < 2 {
		t.Fatalf("expected a chain, got %d events", srv.audit.Len())
	}
	if bad := srv.audit.VerifyChain(); bad != -1 {
		t.Fatalf("clean chain rejected at index %d", bad)
	}

	// Rewrite the effect record's summary, as an attacker hiding a write.
	last := srv.audit.Len() - 1
	srv.audit.events[last].RedactedSummary = "nothing happened here"
	if bad := srv.audit.VerifyChain(); bad != last {
		t.Fatalf("tampered effect record passed chain verification (first bad index %d, want %d)", bad, last)
	}
}

// The path is derived, never supplied. A hostile turn id cannot traverse.
func TestDerivedPathCannotEscapeTheRoot(t *testing.T) {
	root := t.TempDir()
	store := NewEffectStore(root)

	for _, turnID := range []string{"../escape", "../../etc/passwd", "..", "/abs/path", "a/b/c"} {
		res, err := store.WriteNote("notes.local.write", turnID, "content")
		if err != nil {
			continue // refusing outright is also acceptable
		}
		full := filepath.Join(root, res.RelPath)
		abs, _ := filepath.Abs(full)
		rootAbs, _ := filepath.Abs(root)
		if !strings.HasPrefix(abs, rootAbs+string(os.PathSeparator)) {
			t.Fatalf("turn id %q escaped the root: %s", turnID, abs)
		}
	}
}

func TestNoteSizeCapIsEnforced(t *testing.T) {
	root := t.TempDir()
	store := NewEffectStore(root)

	_, err := store.WriteNote("notes.local.write", "turn-big", strings.Repeat("x", maxNoteBytes+1))
	if !errors.Is(err, ErrEffectTooLarge) {
		t.Fatalf("want ErrEffectTooLarge, got %v", err)
	}
	if entries, _ := os.ReadDir(filepath.Join(root, "notes.local.write")); len(entries) != 0 {
		t.Fatalf("over-cap write left %d files behind", len(entries))
	}
}

// A governed artifact is write-once. The single-use lease stops a lease being
// replayed; it cannot stop a client re-submitting the same turn id and being
// issued a FRESH lease. Without this, the second write would silently destroy
// the first approved action's evidence.
func TestGovernedArtifactsAreWriteOnce(t *testing.T) {
	root := t.TempDir()
	store := NewEffectStore(root)

	if _, err := store.WriteNote("notes.local.write", "turn-once", "original"); err != nil {
		t.Fatalf("first write failed: %v", err)
	}
	_, err := store.WriteNote("notes.local.write", "turn-once", "replacement")
	if !errors.Is(err, ErrEffectExists) {
		t.Fatalf("second write: want ErrEffectExists, got %v", err)
	}
	data, _ := os.ReadFile(notePath(root, "turn-once"))
	if string(data) != "original" {
		t.Fatalf("original artifact was replaced: %q", data)
	}
	// The refused attempt must not leave temp files lying in the directory.
	entries, _ := os.ReadDir(filepath.Join(root, "notes.local.write"))
	if len(entries) != 1 {
		names := []string{}
		for _, e := range entries {
			names = append(names, e.Name())
		}
		t.Fatalf("expected exactly one artifact, got %v", names)
	}
}

// Re-submitting a turn id at the HTTP layer is refused and audited, and the
// original file survives.
func TestResubmittedTurnCannotOverwriteTheArtifact(t *testing.T) {
	root := t.TempDir()
	srv := NewServerWithEffectRoot(0, fixedNow, root)

	noteTurn(t, srv, "turn-dup", "save a note the first time")
	original, err := os.ReadFile(notePath(root, "turn-dup"))
	if err != nil {
		t.Fatalf("first turn wrote nothing: %v", err)
	}

	noteTurn(t, srv, "turn-dup", "save a note the second time")

	after, _ := os.ReadFile(notePath(root, "turn-dup"))
	if string(after) != string(original) {
		t.Fatalf("resubmitted turn overwrote the artifact: %q -> %q", original, after)
	}
	last := srv.audit.events[srv.audit.Len()-1]
	if last.Kind != "tool.refused" {
		t.Fatalf("duplicate turn was not audited as refused: kind=%q", last.Kind)
	}
}
