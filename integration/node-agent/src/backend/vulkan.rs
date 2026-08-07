//! Optional Vulkan backend — probe-based scaffold behind the `vulkan` cargo
//! feature. Contract (ADR-001 rule 5): Vulkan may accelerate, but its absence
//! must never prevent startup, so `probe()` returns None whenever no ICD
//! loader is present and selection falls back to the CPU backend.
//!
//! Scaffold status: the probe locates a Vulkan loader; the compute kernel
//! itself still delegates to the CPU reference implementation until a real
//! compute-shader path (ash + SPIR-V) lands. That keeps results bit-identical
//! across backends while the plumbing is proven.

use super::{cpu::CpuBackend, ComputeBackend};
use crate::compute::AudioFeatures;
use std::path::Path;

const LOADER_CANDIDATES: &[&str] = &[
    "/usr/lib/x86_64-linux-gnu/libvulkan.so.1",
    "/usr/lib/x86_64-linux-gnu/libvulkan.so",
    "/usr/lib64/libvulkan.so.1",
    "/usr/lib/libvulkan.so.1",
    "/usr/local/lib/libvulkan.so.1",
];

pub struct VulkanBackend {
    loader_path: &'static str,
    fallback: CpuBackend,
}

impl VulkanBackend {
    /// Returns Some only when a Vulkan loader is actually installed.
    pub fn probe() -> Option<Self> {
        let loader_path = LOADER_CANDIDATES
            .iter()
            .find(|p| Path::new(p).exists())?;
        Some(Self {
            loader_path,
            fallback: CpuBackend,
        })
    }

    pub fn loader_path(&self) -> &'static str {
        self.loader_path
    }
}

impl ComputeBackend for VulkanBackend {
    fn name(&self) -> &'static str {
        "vulkan-probe"
    }

    fn audio_features(&self, samples: &[f32], frame_size: usize) -> AudioFeatures {
        // Scaffold: identical math via the CPU reference path (see module docs).
        self.fallback.audio_features(samples, frame_size)
    }
}
