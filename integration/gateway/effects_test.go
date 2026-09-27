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
	"time"
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

// Artifacts are named from the LEASE, not the turn, and carry a per-process
// run id — so tests locate them by globbing rather than by reconstructing a
// name the server owns.
func noteFiles(t *testing.T, root string) []string {
	t.Helper()
	matches, err := filepath.Glob(filepath.Join(root, "notes.local.write", "*.txt"))
	if err != nil {
		t.Fatalf("glob: %v", err)
	}
	return matches
}

func soleNote(t *testing.T, root string) string {
	t.Helper()
	files := noteFiles(t, root)
	if len(files) != 1 {
		t.Fatalf("expected exactly one artifact, got %d: %v", len(files), files)
	}
	return files[0]
}

// AC1: a valid lease produces the file AND an audit event carrying the result.
func TestGovernedWriteProducesFileAndAudit(t *testing.T) {
	root := t.TempDir()
	srv := NewServerWithEffectRoot(0, fixedNow, root)

	resp := noteTurn(t, srv, "turn-0001", "save a note about the staging rollout")

	if resp.Decision.Effect != "allow" || resp.Decision.SkillID != "notes.local.write" {
		t.Fatalf("unexpected decision: %+v", resp.Decision)
	}
	data, err := os.ReadFile(soleNote(t, root))
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
	if files := noteFiles(t, root); len(files) != 0 {
		t.Fatalf("a refused write still created files: %v", files)
	}

	// No lease at all.
	_, _, err = broker.Execute("notes.local.write", "turn-0003", "secret", nil)
	if !errors.Is(err, ErrLeaseRequired) {
		t.Fatalf("want ErrLeaseRequired, got %v", err)
	}
	if files := noteFiles(t, root); len(files) != 0 {
		t.Fatalf("an unleased write still created files: %v", files)
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
	first := soleNote(t, root)
	info, err := os.Stat(first)
	if err != nil {
		t.Fatalf("first write produced no file: %v", err)
	}
	firstModTime := info.ModTime()

	// Replay with the very same lease material.
	_, _, err = broker.Execute("notes.local.write", "turn-0005", "SECOND write", &lease)
	if !errors.Is(err, ErrLeaseConsumed) {
		t.Fatalf("replay: want ErrLeaseConsumed, got %v", err)
	}
	data, _ := os.ReadFile(first)
	if string(data) != "first write" {
		t.Fatalf("replay overwrote the note: %q", data)
	}
	if after, _ := os.Stat(first); !after.ModTime().Equal(firstModTime) {
		t.Fatal("replay touched the file")
	}
	if files := noteFiles(t, root); len(files) != 1 {
		t.Fatalf("replay created a second artifact: %v", files)
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

	if _, err := store.WriteNote("notes.local.write", "lease-once", "original"); err != nil {
		t.Fatalf("first write failed: %v", err)
	}
	_, err := store.WriteNote("notes.local.write", "lease-once", "replacement")
	if !errors.Is(err, ErrEffectExists) {
		t.Fatalf("second write: want ErrEffectExists, got %v", err)
	}
	data, _ := os.ReadFile(soleNote(t, root))
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

// Re-submitting a turn id is a SECOND authorization: policy issues a second
// lease, so it produces a second artifact rather than colliding with the
// first. What must never happen is the earlier approved action being
// overwritten or lost.
//
// This is why the artifact name comes from the lease. Keying on the turn id
// made a page reload — which resets the console's turn counter — collide with
// the previous run and fail closed until someone ran `make clean`, and let
// any caller pre-claim a name to block future governed writes.
func TestResubmittedTurnCreatesASecondArtifactAndKeepsTheFirst(t *testing.T) {
	root := t.TempDir()
	srv := NewServerWithEffectRoot(0, fixedNow, root)

	noteTurn(t, srv, "turn-dup", "save a note the first time")
	first := soleNote(t, root)
	original, err := os.ReadFile(first)
	if err != nil {
		t.Fatalf("first turn wrote nothing: %v", err)
	}

	noteTurn(t, srv, "turn-dup", "save a note the second time")

	files := noteFiles(t, root)
	if len(files) != 2 {
		t.Fatalf("expected two artifacts for two authorizations, got %v", files)
	}
	after, _ := os.ReadFile(first)
	if string(after) != string(original) {
		t.Fatalf("resubmitted turn altered the earlier artifact: %q -> %q", original, after)
	}
}

// A page reload resets the console turn counter. Under turn-keyed naming that
// silently bricked the demo; under lease-keyed naming it just works.
func TestReusedTurnIdsAcrossSessionsAllSucceed(t *testing.T) {
	root := t.TempDir()
	srv := NewServerWithEffectRoot(0, fixedNow, root)

	for i := 0; i < 3; i++ {
		resp := noteTurn(t, srv, "turn-0001", "save a note from a fresh page load")
		if resp.Decision.Effect != "allow" {
			t.Fatalf("load %d refused: %+v", i, resp.Decision)
		}
	}
	if files := noteFiles(t, root); len(files) != 3 {
		t.Fatalf("expected three artifacts, got %v", files)
	}
}

// A tier-3 lease that is neither approved nor denied simply expires. Nothing
// calls takeContent for it, so without a sweep its payload would live in
// memory for the process lifetime — the retention ADR rule 6 forbids.
func TestExpiredPendingPayloadIsSwept(t *testing.T) {
	current := fixedNow()
	srv := NewServerWithEffectRoot(0, func() time.Time { return current }, t.TempDir())

	// Tier-3 turn: content is held pending human confirmation.
	resp := noteTurn(t, srv, "turn-cr", "create a change request to scale the api tier")
	if resp.Lease == nil {
		t.Fatalf("expected a pending lease, got %+v", resp)
	}
	srv.pendingMu.Lock()
	held := len(srv.pendingContent)
	srv.pendingMu.Unlock()
	if held != 1 {
		t.Fatalf("expected the payload to be held, got %d entries", held)
	}

	// Walk past the lease TTL and let any later hold/take trigger the sweep.
	current = current.Add(leaseTTL + time.Minute)
	srv.holdContent("lease-unrelated", "another payload")

	srv.pendingMu.Lock()
	defer srv.pendingMu.Unlock()
	if _, still := srv.pendingContent[resp.Lease.LeaseID]; still {
		t.Fatal("abandoned tier-3 payload outlived its lease")
	}
}

// A refusal must be as traceable as a success: without the transcript hash it
// cannot be tied back to what was asked.
func TestRefusalCarriesTheTranscriptHash(t *testing.T) {
	srv := NewServerWithEffectRoot(0, fixedNow, t.TempDir())
	noteTurn(t, srv, "turn-refused", "save a note "+strings.Repeat("y", maxNoteBytes))

	last := srv.audit.events[srv.audit.Len()-1]
	if last.Kind != "tool.refused" {
		t.Fatalf("expected a refusal, got %q", last.Kind)
	}
	if last.TranscriptSHA256 == "" {
		t.Fatal("refusal has no transcript hash; it cannot be tied to a request")
	}
	if strings.Contains(last.RedactedSummary, "yyyy") {
		t.Fatalf("refusal leaked the material: %q", last.RedactedSummary)
	}
}

// The store must never be reachable without a lease id, even by a future
// caller that bypasses the broker's ordering.
func TestEffectStoreRefusesAnEmptyLeaseID(t *testing.T) {
	store := NewEffectStore(t.TempDir())
	if _, err := store.WriteNote("notes.local.write", "", "content"); !errors.Is(err, ErrEffectUnleased) {
		t.Fatalf("want ErrEffectUnleased, got %v", err)
	}
}
