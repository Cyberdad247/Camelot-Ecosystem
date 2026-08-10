//! T5: the node agent uses CPU when Vulkan is unavailable, and enabling the
//! `vulkan` feature never breaks startup or changes results.

use camelot_node_agent::backend::{cpu::CpuBackend, select_backend, ComputeBackend};

#[test]
fn backend_selection_always_succeeds() {
    // Total function: never panics, never blocks startup (ADR-001 rule 5).
    let backend = select_backend();
    assert!(!backend.name().is_empty());
}

#[cfg(not(feature = "vulkan"))]
#[test]
fn default_build_selects_cpu() {
    assert_eq!(select_backend().name(), "cpu");
}

#[cfg(feature = "vulkan")]
#[test]
fn vulkan_build_falls_back_to_cpu_without_loader() {
    use camelot_node_agent::backend::vulkan::VulkanBackend;
    let backend = select_backend();
    match VulkanBackend::probe() {
        // No Vulkan loader on this machine: selection MUST fall back to CPU.
        None => assert_eq!(backend.name(), "cpu"),
        // Loader present: probe backend is fine, but results must match CPU.
        Some(_) => assert_eq!(backend.name(), "vulkan-probe"),
    }
}

#[test]
fn accelerated_backends_match_cpu_reference() {
    let samples: Vec<f32> = (0..2048).map(|i| ((i as f32) * 0.05).sin() * 0.5).collect();
    let reference = CpuBackend.audio_features(&samples, 512);
    let selected = select_backend().audio_features(&samples, 512);
    assert_eq!(reference, selected, "backend results must be bit-identical");
}
