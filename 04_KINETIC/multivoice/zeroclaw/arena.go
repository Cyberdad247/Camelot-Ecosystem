// Package zeroclaw is the IPC shared-memory arena for skill cartridges.
//
// Skills selected by VSS are packed into a contiguous buffer that the LLM
// engines read zero-copy. On Linux this buffer is a memfd_create region and is
// reclaimed with MADV_DONTNEED; on other platforms it degrades to an in-process
// byte arena with identical lease accounting (the 4GB Scarcity Protocol budget
// is enforced the same way on every OS). The Linux memfd path is a build-tagged
// drop-in — the accounting and API are platform-agnostic by design.
package zeroclaw

import (
	"errors"
	"sync"

	"camelot-os/vault"
)

// SkillFD is a handle to a packed skill region.
type SkillFD struct {
	data []byte
}

// Bytes returns the packed skill payload (zero-copy view).
func (f *SkillFD) Bytes() []byte { return f.data }

// Len reports the packed size in bytes.
func (f *SkillFD) Len() int { return len(f.data) }

var (
	mu        sync.Mutex
	arenaCap  int // bytes
	leasedNow int // bytes currently leased
)

// InitializeArena sets the arena ceiling in MiB (4GB Scarcity Protocol budget).
func InitializeArena(maxMB int) error {
	if maxMB <= 0 {
		return errors.New("zeroclaw: arena size must be > 0")
	}
	mu.Lock()
	defer mu.Unlock()
	arenaCap = maxMB * 1024 * 1024
	leasedNow = 0
	return nil
}

// LoadEcosystemCartridges packs the given skills into a single arena region,
// stopping before the budget is breached (lower-priority skills are dropped).
// Returns a handle whose bytes the engines read directly.
func LoadEcosystemCartridges(skills []vault.Skill) (*SkillFD, error) {
	mu.Lock()
	defer mu.Unlock()
	if arenaCap == 0 {
		return nil, errors.New("zeroclaw: arena not initialized")
	}
	buf := make([]byte, 0, 1024)
	for _, s := range skills {
		dense := compressToToon(s)
		if leasedNow+len(buf)+len(dense) > arenaCap {
			break // budget reached — drop the rest (Scarcity Protocol)
		}
		buf = append(buf, dense...)
		buf = append(buf, '\n')
	}
	leasedNow += len(buf)
	return &SkillFD{data: buf}, nil
}

// Purge releases one region's lease (MADV_DONTNEED on Linux; frees here).
func Purge(fd *SkillFD) {
	if fd == nil {
		return
	}
	mu.Lock()
	leasedNow -= len(fd.data)
	if leasedNow < 0 {
		leasedNow = 0
	}
	mu.Unlock()
	fd.data = nil
}

// PurgeAll resets the arena, releasing every lease.
func PurgeAll() {
	mu.Lock()
	leasedNow = 0
	mu.Unlock()
}

// Leased reports current arena usage in bytes (for telemetry / tests).
func Leased() int {
	mu.Lock()
	defer mu.Unlock()
	return leasedNow
}

// compressToToon strips JSON noise into a dense TOON-ish payload (Alpha-Omega
// distiller stand-in) before packing — saves arena budget.
func compressToToon(s vault.Skill) string {
	r := s.Name + "|" + s.Payload
	for _, ch := range []string{"{", "}", "\"", "\n", "  "} {
		r = replaceAll(r, ch, "")
	}
	return r
}

func replaceAll(s, old, new string) string {
	out := make([]byte, 0, len(s))
	for i := 0; i < len(s); {
		if old != "" && i+len(old) <= len(s) && s[i:i+len(old)] == old {
			out = append(out, new...)
			i += len(old)
			continue
		}
		out = append(out, s[i])
		i++
	}
	return string(out)
}
