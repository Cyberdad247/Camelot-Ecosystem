// SPDX-License-Identifier: MIT

// Package saga: SCAFFOLD PLACEHOLDER.
//
// Reversibility is state-dependent:
//   - Committed state (the natural post-scaffold state): revert with
//     `git checkout HEAD -- 01_KERNEL/core/mesh/saga.go`.
//   - Untracked state (right after the initial scaffold write, before
//     the first commit): clean with
//     `rm 01_KERNEL/core/mesh/saga.go && rmdir 01_KERNEL/core/mesh`.
//   - The dir `01_KERNEL/core/` itself is owned by other modules and
//     must NOT be removed; `rmdir` here only removes the leaf.
//
// Body intent: preserve the literal snippet from the sovereign:
//
//	package saga
//	import "github.com/camelot-os/core/mesh"
//
// The file currently declares only `package saga` + that exact import.
// Until `github.com/camelot-os/core/mesh` exports its first stable
// symbol (e.g. `Mesh`, an interface, or a type), the import will NOT
// resolve under `go build` — that is intentional and documented so a
// future maintainer does not "fix" it by mutating the sovereign's
// literal import.
//
// Once the mesh package lands, add a usage reference to satisfy the
// conventional Go "imported and not used" check, e.g.:
//
//	import "github.com/camelot-os/core/mesh"
//	var _ = mesh.Mesh // first placeholder; swap to real usage
package saga

// TODO(sovereign): once `github.com/camelot-os/core/mesh` grows its
// first exported symbol, replace this comment block with a real
// saga coordinator state machine (or remove this file entirely if
// the saga role is owned by a different package).
import "github.com/camelot-os/core/mesh"
