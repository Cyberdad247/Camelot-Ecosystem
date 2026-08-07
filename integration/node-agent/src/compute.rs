//! Compute job wire types and batched execution. Kind "audio.features"
//! computes RMS / peak / zero-crossing rate / per-frame energies over f32 PCM
//! samples. Raw audio is processed in memory and dropped with the request —
//! nothing is persisted here (ADR-001 rule 3).

use crate::backend::ComputeBackend;
use serde::{Deserialize, Serialize};

pub const CAPABILITY_AUDIO_FEATURES: &str = "compute:audio.features";
pub const DEFAULT_FRAME_SIZE: usize = 512;

#[derive(Debug, Clone, Deserialize)]
pub struct ComputeLease {
    #[serde(rename = "leaseId")]
    pub lease_id: String,
    pub capability: String,
    pub status: String,
    #[serde(rename = "expiresAt")]
    pub expires_at: String,
    #[serde(default)]
    pub token: String,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ComputeFrame {
    #[serde(rename = "frameId")]
    pub frame_id: String,
    pub samples: Vec<f32>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ComputeJob {
    #[serde(rename = "jobId")]
    pub job_id: String,
    pub kind: String,
    pub lease: ComputeLease,
    /// Batch: one job may carry many frames (bootstrap-plan §3).
    pub frames: Vec<ComputeFrame>,
    #[serde(rename = "frameSize", default)]
    pub frame_size: Option<usize>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct AudioFeatures {
    #[serde(rename = "sampleCount")]
    pub sample_count: usize,
    pub rms: f32,
    pub peak: f32,
    #[serde(rename = "zeroCrossingRate")]
    pub zero_crossing_rate: f32,
    #[serde(rename = "frameEnergies")]
    pub frame_energies: Vec<f32>,
}

#[derive(Debug, Serialize)]
pub struct FrameResult {
    #[serde(rename = "frameId")]
    pub frame_id: String,
    pub features: AudioFeatures,
}

#[derive(Debug, Serialize)]
pub struct ComputeResult {
    #[serde(rename = "jobId")]
    pub job_id: String,
    pub backend: &'static str,
    pub results: Vec<FrameResult>,
}

/// Execute a validated batch. Validation happens BEFORE this is called —
/// see `validate::validate_job`, the only route into `run_job` in main.rs.
pub fn run_job(job: &ComputeJob, backend: &dyn ComputeBackend) -> ComputeResult {
    let frame_size = job.frame_size.unwrap_or(DEFAULT_FRAME_SIZE);
    let results = job
        .frames
        .iter()
        .map(|frame| FrameResult {
            frame_id: frame.frame_id.clone(),
            features: backend.audio_features(&frame.samples, frame_size),
        })
        .collect();
    ComputeResult {
        job_id: job.job_id.clone(),
        backend: backend.name(),
        results,
    }
}
