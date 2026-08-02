// 02_FORGE/kinetic/omni_nexus_ide/src/lib.rs
// Recognized forge subtree for the omni-nexus-ide daughter project.
// FOLD-IN scope PR: sibling of actor/contracts/cribo/pmcp/rotel; no new
// workspace. Stub state — awaits a real artifact forge_nexus.sh (currently
// REJECTED-class in narrative; user confirmed Q2: do not scaffold).

/// Canonical subtree path. Stable string for AGENTS.md / cargo metadata.
pub const SUBTREE_PATH: &str = "02_FORGE/kinetic/omni_nexus_ide";

/// Returns the canonical subtree path string. Tree-gating key.
pub fn subtree_marker() -> &'static str {
    "02_FORGE/kinetic/omni_nexus_ide"
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn subtree_marker_matches_constant() {
        assert_eq!(subtree_marker(), SUBTREE_PATH);
    }
}
