//! Compute backends. CPU is the guaranteed baseline; Vulkan is an optional,
//! probe-based acceleration path behind the `vulkan` cargo feature.
//! Selection NEVER fails and never blocks startup (ADR-001 rule 5).

pub mod cpu;
#[cfg(feature = "vulkan")]
pub mod vulkan;

use crate::compute::AudioFeatures;

pub trait ComputeBackend: Send + Sync {
    fn name(&self) -> &'static str;
    fn audio_features(&self, samples: &[f32], frame_size: usize) -> AudioFeatures;
}

/// Pick the best available backend. Order: Vulkan (if compiled in AND a
/// loader is actually present) then CPU. The CPU path always exists, so this
/// function is total.
pub fn select_backend() -> Box<dyn ComputeBackend> {
    #[cfg(feature = "vulkan")]
    {
        if let Some(vk) = vulkan::VulkanBackend::probe() {
            return Box::new(vk);
        }
    }
    Box::new(cpu::CpuBackend)
}
