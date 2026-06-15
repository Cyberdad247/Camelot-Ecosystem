# CAMELOT MISSION: ONYX FORGE BLUEPRINT
## Task DAG — one-vizion-records Full Remediation
**Forged:** 2026-04-25  
**Architect:** ANYA_Omega (Gate) + SIR_ALEX (Cognitive) + SIR_LINK (ATC)  
**Lead:** SIR_BORIS v3.0  
**Target repo:** `C:\Users\vizio\onyx`  
**Source audit:** `//BOOT Session 2026-04-25`  
**Ledger note:** `1a90e838-d1c8-4857-a2f6-cab5a10a0a52` (Living Camelot-OS v.400)

---

## EXECUTION ORDER (Task DAG)

```
EPIC-01 (Repo Split) ─┬─► EPIC-02 (Cleanup)
                      └─► EPIC-03 (Audio Fixes) ──► EPIC-06 (Rhythm Engine)
EPIC-04 (CI/CD) ──────────────────────────────────► EPIC-05 (Security)
```

All EPICs below EPIC-01 can run in parallel after the repo is extracted.

---

## EPIC-01 — REPO SEPARATION
**Knight:** SIR_ALEX + SIR_LINK + MASON (nano)  
**Priority:** CRITICAL — all other work blocked until this is done  
**Rationale:** one-vizion-records has zero relation to the Onyx Haskell toolkit. Mixed repo inflates clone size, muddies CI, and creates provenance confusion.

### T-01.1 — Extract one-vizion-records to standalone repo
**Owner:** SIR_ALEX (strategy) + SIR_LINK (handoff)  
**Method:** git subtree split (preserves commit history for the subdirectory)

```bash
# Run from C:\Users\vizio\onyx
git subtree split --prefix=one-vizion-records -b one-vizion-records-branch

# Initialize new repo
mkdir C:\Users\vizio\one-vizion-records
cd C:\Users\vizio\one-vizion-records
git init
git pull C:\Users\vizio\onyx one-vizion-records-branch

# Create GitHub remote and push
gh repo create Cyberdad247/one-vizion-records --private --source=. --push

# Clean from onyx repo
cd C:\Users\vizio\onyx
git rm -r one-vizion-records/
git commit -m "chore: extract one-vizion-records to its own repo"
```

**Acceptance:** New repo exists at `github.com/Cyberdad247/one-vizion-records` with full git history. `one-vizion-records/` folder absent from `Cyberdad247/onyx`.

### T-01.2 — Update Vercel project binding
**Owner:** SIR_LINK  
After extraction, re-link Vercel project to new repo root.

```bash
cd C:\Users\vizio\one-vizion-records
vercel link  # Re-associate with Vercel project
vercel deploy --prod
```

**Acceptance:** Vercel deployment succeeds from new standalone repo. Old onyx-bound deployment removed or redirected.

### T-01.3 — MASON: Scaffold new repo root files
**Owner:** MASON (nano-knight)  
Create missing top-level files in the new `one-vizion-records` repo:

- `CLAUDE.md` — project-specific AI instructions
- `.github/` directory (see EPIC-04)
- `CHANGELOG.md` — initial entry

---

## EPIC-02 — ARTIFACT CLEANUP
**Knight:** SWEEP (nano) + SIR_SENTINEL  
**Priority:** HIGH  
**Blocks:** Nothing (run in parallel after EPIC-01)

### T-02.1 — Delete misplaced PROVENANCE_LEDGER.md from onyx root
**Owner:** SWEEP (nano)  

```bash
cd C:\Users\vizio\onyx
git rm PROVENANCE_LEDGER.md
git commit -m "chore: remove misplaced lisa-keychains provenance ledger (wrong repo)"
```

**Acceptance:** `PROVENANCE_LEDGER.md` absent from `Cyberdad247/onyx` root. File still present in its correct home (lisa-custom-keychains repo / CAMELOT_OS).

### T-02.2 — Remove defunct Travis CI config
**Owner:** SWEEP (nano)  

```bash
cd C:\Users\vizio\onyx
git rm .travis.yml
git commit -m "ci: remove defunct Travis CI config (replaced by GitHub Actions in T-04.1)"
```

**Acceptance:** `.travis.yml` absent. GitHub Actions workflow present (see EPIC-04).

### T-02.3 — Audit onyx root for any other CAMELOT_OS artifacts
**Owner:** SIR_SENTINEL  
Scan for any other files from CAMELOT_OS that don't belong in the Onyx toolkit repo.

```bash
cd C:\Users\vizio\onyx
grep -r "CAMELOT\|SIR_BORIS\|Invisioned\|Camelot-OS\|PROVENANCE" --include="*.md" --include="*.txt" --include="*.yml" -l
```

**Acceptance:** Zero CAMELOT_OS artifacts in onyx root outside of one-vizion-records (which will be extracted).

---

## EPIC-03 — AUDIO ENGINE FIXES
**Knight:** SIR_FORGE + SIR_DEBUG  
**Priority:** HIGH  
**File:** `one-vizion-records/src/app/components/Jukebox.tsx`  
**Note:** Perform these fixes in the NEW standalone repo after EPIC-01.

### T-03.1 — Fix AudioContext: defer to user gesture + add CORS header
**Owner:** SIR_FORGE  
**Bug:** `AudioContext` created on mount — suspended by browser autoplay policy. No `crossOrigin` on `<audio>` element causes CORS errors when piped through WebAudio API.

**Current (broken):**
```tsx
// Fires on mount, before user interaction — browser suspends context
useEffect(() => {
    const ctx = new AudioContextClass();
    const source = ctx.createMediaElementSource(audioRef.current);
    ...
}, []);
```

**Fix — Jukebox.tsx:**

```tsx
// 1. Remove the mount-time AudioContext useEffect entirely.
// 2. Add ref for context:
const audioCtxRef = useRef<AudioContext | null>(null);
const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);

// 3. Create context inside togglePlay (first user gesture):
const togglePlay = () => {
    if (!audioRef.current) return;

    // Initialize AudioContext on first play (gesture requirement)
    if (!audioCtxRef.current) {
        const AudioContextClass = (window.AudioContext ||
            (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext);
        const ctx = new AudioContextClass();
        const source = ctx.createMediaElementSource(audioRef.current);
        const node = ctx.createAnalyser();
        node.fftSize = 256;
        source.connect(node);
        node.connect(ctx.destination);
        audioCtxRef.current = ctx;
        setAnalyser(node);
    }

    // Resume if suspended (mobile browsers)
    if (audioCtxRef.current.state === 'suspended') {
        audioCtxRef.current.resume();
    }

    const newPlaying = !isPlaying;
    if (isPlaying) {
        audioRef.current.pause();
    } else {
        audioRef.current.play().catch(e => console.warn("Playback blocked:", e));
    }
    setIsPlayingLocal(newPlaying);
    setIsPlaying(newPlaying);
};

// 4. Add crossOrigin to <audio> element:
<audio
    key={current.id}
    ref={audioRef}
    src={current.audio_url}
    crossOrigin="anonymous"
    onEnded={nextTrack}
/>
```

**Acceptance:** No `AudioContext was not allowed to start` console errors. No CORS errors on WebAudio pipeline. Waveform visualizer activates on first play.

### T-03.2 — Wire real-time progress bar
**Owner:** SIR_FORGE  
**Bug:** Progress bar is hardcoded `w-1/4` and timestamp `"0:45"`.

**Fix — Jukebox.tsx:**

```tsx
// Add state:
const [progress, setProgress] = useState(0);   // 0–1 ratio
const [currentTime, setCurrentTime] = useState(0);

// Add handler:
const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const { currentTime: ct, duration } = audioRef.current;
    if (duration > 0) {
        setProgress(ct / duration);
        setCurrentTime(ct);
    }
};

// Reset on track change:
const nextTrack = () => {
    setProgress(0);
    setCurrentTime(0);
    // ... existing logic
};

// Helper:
const formatTime = (s: number) =>
    `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

// Update JSX:
<audio
    key={current.id}
    ref={audioRef}
    src={current.audio_url}
    crossOrigin="anonymous"
    onTimeUpdate={handleTimeUpdate}
    onEnded={nextTrack}
/>

// Progress bar (replace hardcoded):
<span className="text-[10px] text-zinc-600 font-mono">
    {formatTime(currentTime)}
</span>
<div className="flex-1 h-[2px] bg-white/5 rounded-full overflow-hidden">
    <div
        className="h-full bg-gradient-to-r from-cyan-500 to-fuchsia-500 shadow-[0_0_10px_rgba(6,182,212,0.8)] transition-all duration-100"
        style={{ width: `${progress * 100}%` }}
    />
</div>
```

**Acceptance:** Progress bar advances in real time. Timestamp shows `M:SS` format. Resets to `0:00` on track change.

### T-03.3 — Implement volume control
**Owner:** SIR_FORGE  
**Bug:** `Volume2` icon renders but has no handler. Volume is uncontrollable.

**Fix — Jukebox.tsx:**

```tsx
// Add state:
const [volume, setVolume] = useState(1);
const [showVolume, setShowVolume] = useState(false);

// Sync to audio:
useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
}, [volume]);

// Replace Volume2 icon with slider widget:
<div className="relative">
    <button onClick={() => setShowVolume(v => !v)}>
        <Volume2 size={18} className="text-zinc-600 hover:text-zinc-400 transition-colors" />
    </button>
    {showVolume && (
        <div className="absolute bottom-8 right-0 bg-black/90 border border-white/10 rounded-xl p-3 w-8 flex flex-col items-center gap-2">
            <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={volume}
                onChange={e => setVolume(Number(e.target.value))}
                className="h-24 appearance-none cursor-pointer accent-cyan-400"
                style={{ writingMode: 'vertical-lr', direction: 'rtl' }}
            />
        </div>
    )}
</div>
```

**Acceptance:** Volume icon toggle reveals vertical slider. Audio volume changes smoothly. State persists across tracks.

### T-03.4 — Fix isPlaying state naming collision
**Owner:** SIR_FORGE  
**Bug:** Local state `isPlaying` and context `setIsPlaying` share conceptual space, can drift.

**Fix:** Rename local state to `isPlayingLocal` throughout:

```tsx
const [isPlayingLocal, setIsPlayingLocal] = useState(false);
// Replace all uses of isPlaying in local logic with isPlayingLocal
// Context setIsPlaying(newPlaying) remains as-is (drives RhythmEngine)
```

**Acceptance:** `tsc --noEmit` clean. No state divergence between Jukebox local and EngineContext.

---

## EPIC-04 — CI/CD MIGRATION
**Knight:** LADY_APIS (research) + SIR_FORGE (forge) + SIR_SENTINEL (audit)  
**Priority:** MEDIUM  
**Target:** New `one-vizion-records` repo after EPIC-01.

### T-04.1 — Create GitHub Actions workflow: CI
**Owner:** SIR_FORGE (after LADY_APIS template forage)  
**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run build
    env:
      NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.NEXT_PUBLIC_SUPABASE_URL }}
      NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.NEXT_PUBLIC_SUPABASE_ANON_KEY }}
```

**Acceptance:** Workflow runs on every PR. `npm run build` passes. Secrets injected from GitHub repo settings (never in code).

### T-04.2 — Add GitHub Actions secrets
**Owner:** SIR_LINK (bridge)  
Register in GitHub repo settings → Secrets and Variables → Actions:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Acceptance:** CI workflow passes without `.env.local` present in repo.

### T-04.3 — LADY_APIS: Forage Next.js 16 + React 19 GH Actions best practices
**Owner:** LADY_APIS  
Search for updated patterns for:
- Next.js 16 build caching in GitHub Actions
- React 19 + Three.js CI stability notes
- Any known `@react-three/fiber` 9.x CI issues

**Acceptance:** Research note added to Living Camelot-OS v.400 notebook. Any findings incorporated into T-04.1 workflow.

---

## EPIC-05 — SECURITY HARDENING
**Knight:** SIR_SENTINEL + SIR_ALEX  
**Priority:** HIGH  
**Target:** one-vizion-records (new standalone repo) + Supabase project

### T-05.1 — Verify Supabase RLS on tracks table
**Owner:** SIR_SENTINEL  
The `tracks` table is queried client-side using an exposed anon key. Without RLS, any visitor can INSERT/UPDATE/DELETE tracks.

**Actions:**
1. Log into Supabase Dashboard → `cdmbpgjggqcsvjitbyaj`
2. Navigate: Authentication → Policies → `tracks` table
3. Verify `SELECT` policy exists and is scoped to public read-only
4. Add `INSERT/UPDATE/DELETE` restriction: deny all for `anon` role

**Required policy (SQL):**
```sql
-- Allow public read
CREATE POLICY "Public can read tracks"
  ON tracks FOR SELECT
  TO anon
  USING (true);

-- Block writes from anon
CREATE POLICY "Only service role can write"
  ON tracks FOR ALL
  TO authenticated
  USING (auth.role() = 'service_role');
```

**Acceptance:** Attempt to INSERT a track using only the anon key fails with RLS error. SELECT still works.

### T-05.2 — Enable Supabase RLS on tracks table
**Owner:** SIR_SENTINEL  

```sql
ALTER TABLE tracks ENABLE ROW LEVEL SECURITY;
```

**Acceptance:** `tracks.rls_enabled = true` in Supabase dashboard.

### T-05.3 — Verify .env.local is not committed anywhere in git history
**Owner:** SIR_SENTINEL  

```bash
cd C:\Users\vizio\onyx
git log --all --full-history -- "*/.env.local" "*.env*"
git log --all -p --follow -- one-vizion-records/.env.local
```

If found in history: run BFG Repo Cleaner or `git filter-repo` to purge.

**Acceptance:** `git log --all -- "*/.env.local"` returns empty. No credentials in history.

### T-05.4 — SIR_ALEX: Supabase audio bucket access review
**Owner:** SIR_ALEX  
The `.env.local.example` mentions `audio` and `covers` buckets set to PUBLIC. Public buckets allow unauthenticated reads of all stored audio files.

**Review:** Assess if audio should be behind signed URLs (prevents hotlinking/bandwidth theft) or if public CDN access is intentional for streaming performance.

**Acceptance:** Architecture decision documented in `CLAUDE.md` of new repo. Bucket policy matches decision.

---

## EPIC-06 — RHYTHM ENGINE IMPROVEMENTS
**Knight:** SIR_FORGE + SIR_DEBUG  
**Priority:** MEDIUM (non-blocking, quality upgrade)  
**File:** `one-vizion-records/src/app/components/RhythmEngine.tsx`

### T-06.1 — Implement real hit detection (replace placeholder)
**Owner:** SIR_FORGE  
**Bug:** Line 62: `// Check for hits (simplified for now)` — score added on ANY keypress regardless of note position.

**Fix:** Track note Z positions and check proximity to target zone (Z ≈ 3) on keypress:

```tsx
// In EngineCore, track note refs with positions:
const notePositions = useRef<{ [id: number]: { lane: number; z: number } }>({});

// In Note component, report position via callback:
function Note({ lane, speed, onMiss, onPositionUpdate, id }: ...) {
    useFrame((_state, delta) => {
        const newZ = ...; // existing logic
        onPositionUpdate(id, newZ);
        if (newZ > 10) onMiss();
    });
}

// In handleKeyDown, check proximity:
const TARGET_Z = 3;
const HIT_WINDOW = 1.5;

const lane = keyMap[e.key.toLowerCase()];
if (lane !== undefined) {
    const hit = Object.entries(notePositions.current).find(([, pos]) =>
        pos.lane === lane && Math.abs(pos.z - TARGET_Z) < HIT_WINDOW
    );
    if (hit) {
        addScore(100);
        setNotes(prev => prev.filter(n => n.id !== Number(hit[0])));
    }
    // Visual feedback fires regardless of hit
    window.dispatchEvent(new CustomEvent('lane-press', { detail: lane }));
}
```

**Acceptance:** Score only increments when a note is within `HIT_WINDOW` of target zone. Missed keypresses log nothing.

### T-06.2 — Fix `any` type on lane-press event handler
**Owner:** SIR_FORGE  
**File:** `RhythmEngine.tsx` line 124

```tsx
// Replace:
const handlePress = (e: any) => {
// With:
const handlePress = (e: Event) => {
    const lane = (e as CustomEvent<number>).detail;
```

**Acceptance:** `tsc --noEmit` clean. No `any` in component.

### T-06.3 — Notes not removed on hit (memory leak)
**Owner:** SIR_FORGE  
Notes are only removed via `onMiss`. After T-06.1 fix, hits call `setNotes` filter — this is included in T-06.1. Verify the slice(-20) cap doesn't race with hit removal.

**Acceptance:** Notes list never exceeds 20 items. Hit notes disappear immediately.

---

## BIOSWARM NANO-KNIGHT ASSIGNMENTS

| Knight | Tasks | Mode |
|---|---|---|
| SWEEP | T-02.1, T-02.2, T-02.3 | Clean / purge |
| MASON | T-01.3, T-04.1 scaffold | Scaffold / template |
| SCAN | Pre-flight on T-03.1–T-03.4 (read all Jukebox deps before patching) | Audit |
| JUDGE | Post-task validation on each EPIC (runs before SENTINEL QA) | Validate |
| SENTINEL (squire) | T-05.3 git history scan, T-02.3 artifact scan | Security |
| VECTOR | Index new one-vizion-records repo after EPIC-01 | Context |

---

## UKG CRYSTAL

```json
{
  "UKG_NODE": {
    "SESSION_ID": "onyx-forge-2026-04-25",
    "CONTEXT_STATE": ["REPO_SPLIT", "AUDIO_FIX", "CI_MIGRATE", "RLS_HARDEN", "RHYTHM_FIX"],
    "ACTIVE_KNIGHTS": ["SIR_FORGE", "SIR_ALEX", "SIR_LINK", "SIR_SENTINEL", "SIR_DEBUG", "LADY_APIS"],
    "ACTIVE_NANO": ["SWEEP", "MASON", "SCAN", "JUDGE", "SENTINEL-SQUIRE", "VECTOR"],
    "PENDING_ARTIFACTS": ["one-vizion-records standalone repo", "CI workflow", "Supabase RLS policies"],
    "BLOCKED_ON": ["EPIC-01 completion before EPIC-03/04/05/06 can execute in new repo"]
  }
}
```

---

## EXECUTION PROTOCOL
1. Begin with EPIC-01 (T-01.1) — repo split. All other work targets the new repo.
2. Once repo is live: EPIC-02, EPIC-03, EPIC-04, EPIC-05 execute in parallel swarm.
3. EPIC-06 runs after EPIC-03 is validated.
4. Run `onyx_validation.md` after each EPIC completes.
5. Log each completed task to `CAMELOT_OS/PROVENANCE_LEDGER.md`.
