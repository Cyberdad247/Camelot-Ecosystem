# CAMELOT QA: ONYX VALIDATION MATRIX
## Quality Gate — one-vizion-records Remediation
**Forged:** 2026-04-25  
**QA Lead:** SIR_SENTINEL + SIR_DEBUG  
**Cognitive Review:** SIR_ALEX  
**Trigger:** Run after each EPIC in `onyx_task.md`  
**Pass threshold:** ALL checks in an EPIC must be ✅ before proceeding to next EPIC

---

## HOW TO USE
For each check, mark:
- `✅ PASS` — criterion met
- `❌ FAIL` — criterion not met (block EPIC, raise issue)
- `⚠ WARN` — partially met (document and continue)
- `⏭ SKIP` — explicitly deferred (document reason)

---

## EPIC-01 VALIDATION — REPO SEPARATION

### V-01.1 — Git subtree history integrity
**Knight:** SIR_ALEX  
**Method:** Manual verification

```bash
cd C:\Users\vizio\one-vizion-records
git log --oneline | head -20
```

**Pass criteria:**
- [ ] Commit history shows commits specific to `one-vizion-records/` subdirectory
- [ ] No Haskell/Onyx toolkit commits visible in new repo history
- [ ] First commit is NOT a squashed "initial commit" (history preserved)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-01.2 — New repo structure integrity
**Knight:** SIR_SENTINEL  

```bash
cd C:\Users\vizio\one-vizion-records
ls -la
ls src/app/
```

**Pass criteria:**
- [ ] `package.json` present at root (not nested)
- [ ] `src/app/page.tsx` resolves correctly
- [ ] `.gitignore` present and contains `.env*`
- [ ] `.env.local` NOT committed (`git status` shows untracked or absent)
- [ ] `node_modules/` NOT committed

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-01.3 — Onyx repo cleaned
**Knight:** SWEEP  

```bash
cd C:\Users\vizio\onyx
ls one-vizion-records 2>&1  # Must return "No such file"
git log --oneline -5
```

**Pass criteria:**
- [ ] `one-vizion-records/` directory absent from `C:\Users\vizio\onyx`
- [ ] Last commit message references extraction
- [ ] `git status` clean (no dangling refs)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-01.4 — Vercel deployment live from new repo
**Knight:** SIR_LINK  

```bash
cd C:\Users\vizio\one-vizion-records
vercel ls  # Show deployments
```

**Pass criteria:**
- [ ] Vercel project linked to `Cyberdad247/one-vizion-records`
- [ ] Latest deployment is from new repo (check Vercel dashboard → Git Integration)
- [ ] Production URL responds 200 OK
- [ ] No deployment still pointing to `Cyberdad247/onyx` for this app

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

## EPIC-02 VALIDATION — ARTIFACT CLEANUP

### V-02.1 — PROVENANCE_LEDGER.md absent from onyx
**Knight:** SIR_SENTINEL  

```bash
cd C:\Users\vizio\onyx
ls PROVENANCE_LEDGER.md 2>&1  # Must return error
git log --all -- PROVENANCE_LEDGER.md | head -3
```

**Pass criteria:**
- [ ] File absent from working tree
- [ ] Git log shows removal commit (not absence — removal must be explicit)
- [ ] Commit message explains WHY it was removed (wrong repo)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-02.2 — Travis CI config removed
**Knight:** SWEEP  

```bash
cd C:\Users\vizio\onyx
ls .travis.yml 2>&1  # Must return error
```

**Pass criteria:**
- [ ] `.travis.yml` absent from working tree
- [ ] GitHub Actions workflow present if CI was desired for Onyx toolkit (or explicitly noted as deferred)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-02.3 — Zero CAMELOT artifacts in onyx root
**Knight:** SIR_SENTINEL  

```bash
cd C:\Users\vizio\onyx
grep -r "CAMELOT\|SIR_BORIS\|Invisioned\|Camelot-OS" \
  --include="*.md" --include="*.txt" --include="*.yml" --include="*.json" \
  --exclude-dir=.git -l 2>/dev/null
```

**Pass criteria:**
- [ ] Command returns zero file matches
- [ ] (WARN acceptable if Onyx toolkit README mentions CAMELOT for unrelated reasons — review manually)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

## EPIC-03 VALIDATION — AUDIO ENGINE FIXES

### V-03.1 — AudioContext: No autoplay policy errors
**Knight:** SIR_DEBUG  
**Method:** Browser DevTools Console (Chrome/Edge)

**Steps:**
1. Open `http://localhost:3000` (fresh tab, no prior interaction)
2. Open DevTools → Console
3. DO NOT click play yet
4. Verify: no `AudioContext was not allowed to start` error logged
5. Click Play button
6. Verify: waveform visualizer activates, no CORS errors

**Pass criteria:**
- [ ] No `AudioContext was not allowed to start` on page load
- [ ] No `NotAllowedError` on play
- [ ] No CORS errors (`Cross-Origin Request Blocked`) in console
- [ ] Waveform bars animate after first play click
- [ ] Repeat on track change: no re-initialization errors

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-03.2 — AudioContext: Mobile Safari
**Knight:** SIR_DEBUG  
**Method:** Browser DevTools → Device simulation (iPhone 12)

**Pass criteria:**
- [ ] `ctx.state` is `'suspended'` before user gesture
- [ ] `ctx.state` transitions to `'running'` after play button tap
- [ ] Audio plays without silence on mobile

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-03.3 — Progress bar: real-time tracking
**Knight:** SIR_DEBUG  

**Steps:**
1. Play a track
2. Watch progress bar for 10 seconds
3. Seek via: (if seek is implemented) or let it run
4. Switch tracks

**Pass criteria:**
- [ ] Progress bar advances proportionally while audio plays
- [ ] Timestamp shows `M:SS` format (e.g. `0:07`, `1:23`)
- [ ] Progress resets to `0:00` immediately on track change
- [ ] `duration` denominator never shows `NaN` or `Infinity`

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-03.4 — Volume control functional
**Knight:** SIR_DEBUG  

**Steps:**
1. Click Volume2 icon
2. Verify vertical slider appears
3. Drag slider down
4. Verify audio volume decreases audibly

**Pass criteria:**
- [ ] Volume icon click reveals slider (no console errors)
- [ ] Slider range 0–100% matches audio element `.volume` (0–1)
- [ ] Volume change persists across track changes
- [ ] Slider dismisses on second icon click
- [ ] Volume at 0 is truly muted (not just quiet)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-03.5 — TypeScript clean after all fixes
**Knight:** SIR_DEBUG  

```bash
cd C:\Users\vizio\one-vizion-records
npx tsc --noEmit 2>&1
```

**Pass criteria:**
- [ ] Zero TypeScript errors
- [ ] Zero `any` types introduced by fixes (verify with: `grep -r ": any" src/`)
- [ ] `npm run build` exits code 0

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

## EPIC-04 VALIDATION — CI/CD

### V-04.1 — GitHub Actions workflow file valid
**Knight:** SIR_FORGE  

```bash
cd C:\Users\vizio\one-vizion-records
cat .github/workflows/ci.yml
# Validate YAML syntax:
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo VALID
```

**Pass criteria:**
- [ ] `ci.yml` exists at `.github/workflows/ci.yml`
- [ ] YAML is syntactically valid
- [ ] `on:` trigger includes `push` to `main` and `pull_request`
- [ ] `npm ci` (not `npm install`) used for reproducible builds
- [ ] Secrets referenced via `${{ secrets.* }}` not hardcoded

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-04.2 — CI runs green on GitHub
**Knight:** SIR_LINK  

**Steps:**
1. Push a trivial commit to `main`
2. Navigate to GitHub → Actions tab
3. Observe workflow run

**Pass criteria:**
- [ ] Workflow triggers automatically
- [ ] All steps pass (lint, build)
- [ ] Build does NOT fail due to missing env vars (secrets injected correctly)
- [ ] Build time under 3 minutes

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

## EPIC-05 VALIDATION — SECURITY

### V-05.1 — Supabase RLS enabled
**Knight:** SIR_SENTINEL  

```sql
-- Run in Supabase SQL Editor:
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE tablename = 'tracks';
```

**Pass criteria:**
- [ ] `rowsecurity = true` for `tracks` table
- [ ] At least one SELECT policy exists for `anon` role
- [ ] No INSERT/UPDATE/DELETE policy for `anon` role

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-05.2 — Anon key cannot write to tracks
**Knight:** SIR_SENTINEL  
**Method:** Run from terminal using only the anon key

```bash
# Replace SUPABASE_URL and ANON_KEY with values from .env.local
curl -X POST \
  https://cdmbpgjggqcsvjitbyaj.supabase.co/rest/v1/tracks \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <ANON_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"title":"rls-test","artist":"test","audio_url":"x","cover_url":"x"}'
```

**Pass criteria:**
- [ ] Response is `403 Forbidden` or RLS policy error
- [ ] No row inserted (verify in Supabase dashboard)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-05.3 — No credentials in git history
**Knight:** SIR_SENTINEL  

```bash
cd C:\Users\vizio\one-vizion-records
git log --all -p | grep -E "supabase|eyJhbGci|NEXT_PUBLIC_SUPABASE" | head -20
```

**Pass criteria:**
- [ ] Zero matches for Supabase URL in git history
- [ ] Zero matches for JWT token pattern (`eyJhbGci`)
- [ ] `.env.local` not in any commit: `git log --all -- .env.local` returns empty

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-05.4 — CI secrets not exposed in logs
**Knight:** SIR_SENTINEL  

**Steps:**
1. Navigate to GitHub → Actions → latest run → build step logs
2. Search logs for any Supabase URL or key fragments

**Pass criteria:**
- [ ] No Supabase URL visible in CI logs
- [ ] No JWT token fragments visible
- [ ] GitHub masks secrets (`***` appears in place of secret values if referenced directly)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

## EPIC-06 VALIDATION — RHYTHM ENGINE

### V-06.1 — Hit detection accuracy
**Knight:** SIR_DEBUG  

**Steps:**
1. Play a track (notes begin falling)
2. Press `A` key when NO note is near the target zone
3. Press `A` key when a note IS in the target zone

**Pass criteria:**
- [ ] Score does NOT increment on keypress with no note in zone
- [ ] Score DOES increment when note is within hit window
- [ ] Hit note disappears immediately from canvas
- [ ] Miss notes continue falling past target zone

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-06.2 — TypeScript: no `any` in RhythmEngine
**Knight:** SIR_DEBUG  

```bash
grep -n ": any\|as any" src/app/components/RhythmEngine.tsx
```

**Pass criteria:**
- [ ] Zero `any` types in file
- [ ] `CustomEvent<number>` cast used for lane-press events

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-06.3 — Notes list bounded at 20
**Knight:** SIR_DEBUG  
**Method:** Add temporary console.log to RhythmEngine during test:

```tsx
// Temporary — remove after validation
useFrame(...) {
    console.log('notes count:', notes.length);  // Must never exceed 20
}
```

**Pass criteria:**
- [ ] `notes.length` never exceeds 20 in console
- [ ] Notes list shrinks as notes are hit or missed
- [ ] No memory leak after 3 minutes of play (notes stay bounded)

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

## FINAL GATE — SOVEREIGN REVIEW

### V-FINAL.1 — Full build clean
**Knight:** SIR_DEBUG  

```bash
cd C:\Users\vizio\one-vizion-records
npm ci
npm run lint
npm run build
echo "Exit code: $?"
```

**Pass criteria:**
- [ ] `npm run lint` exits 0
- [ ] `npm run build` exits 0
- [ ] Zero TypeScript errors
- [ ] Zero ESLint errors (warnings acceptable)
- [ ] Build output present in `.next/`

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-FINAL.2 — Production deployment smoke test
**Knight:** SIR_LINK  

**Steps:**
1. Deploy to Vercel production
2. Open production URL
3. Test critical paths: home page load, play button, track switch, volume control

**Pass criteria:**
- [ ] Page loads in < 3s (LCP)
- [ ] Jukebox visible and playable
- [ ] RhythmEngine 3D canvas renders without WebGL errors
- [ ] Waveform visualizer activates on play
- [ ] No console errors on production domain

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

### V-FINAL.3 — SIR_ALEX Cognitive Architecture Review
**Knight:** SIR_ALEX  

Review the completed implementation for:
1. State architecture — is EngineContext the right scope for BPM sync?
2. WebAudio + R3F coexistence — any render loop conflicts?
3. Supabase client instantiated once (module-level singleton) — confirm no multi-instance issue in Next.js App Router

**Pass criteria:**
- [ ] No architectural regressions introduced
- [ ] State flows documented in `CLAUDE.md` of new repo
- [ ] Any deferred improvements logged as GitHub Issues

**Result:** `[ ] PASS  [ ] FAIL  [ ] WARN`  
**Notes:** ___

---

## VALIDATION SCOREBOARD

| EPIC | Checks | Passed | Failed | Warned | Status |
|---|---|---|---|---|---|
| EPIC-01 Repo Split | 4 | | | | |
| EPIC-02 Cleanup | 3 | | | | |
| EPIC-03 Audio Fixes | 5 | | | | |
| EPIC-04 CI/CD | 2 | | | | |
| EPIC-05 Security | 4 | | | | |
| EPIC-06 Rhythm Engine | 3 | | | | |
| FINAL GATE | 3 | | | | |
| **TOTAL** | **24** | | | | |

**Mission COMPLETE when:** 24/24 PASS or all FAILs explicitly escalated to SIR_BORIS for disposition.

---

## ESCALATION PROTOCOL
- **FAIL on V-05.x (Security)** → Halt deployment. Escalate to SIR_SENTINEL + SIR_BORIS immediately.
- **FAIL on V-03.1 (AudioContext CORS)** → Do not deploy. Audio engine non-functional.
- **FAIL on V-01.4 (Vercel)** → Halt. Production unreachable.
- **WARN on any V-06.x** → Log as GitHub Issue, continue (rhythm engine is non-blocking feature).

---

*Validation matrix forged by ANYA_Omega | SIR_ALEX | SIR_BORIS — 2026-04-25*  
*[Omega_SYNC] Ledger note: 1a90e838-d1c8-4857-a2f6-cab5a10a0a52*
