//! CPU reference implementation of the audio-feature kernel. Deterministic,
//! dependency-free, and the correctness baseline any accelerated backend
//! must match.

use super::ComputeBackend;
use crate::compute::AudioFeatures;

pub struct CpuBackend;

impl ComputeBackend for CpuBackend {
    fn name(&self) -> &'static str {
        "cpu"
    }

    fn audio_features(&self, samples: &[f32], frame_size: usize) -> AudioFeatures {
        let n = samples.len();
        if n == 0 {
            return AudioFeatures {
                sample_count: 0,
                rms: 0.0,
                peak: 0.0,
                zero_crossing_rate: 0.0,
                frame_energies: vec![],
            };
        }

        let mut sum_sq = 0.0f64;
        let mut peak = 0.0f32;
        let mut crossings = 0usize;
        for (i, &s) in samples.iter().enumerate() {
            sum_sq += f64::from(s) * f64::from(s);
            if s.abs() > peak {
                peak = s.abs();
            }
            if i > 0 && (s >= 0.0) != (samples[i - 1] >= 0.0) {
                crossings += 1;
            }
        }

        let frame_size = frame_size.max(1);
        let frame_energies = samples
            .chunks(frame_size)
            .map(|frame| {
                let e: f64 = frame.iter().map(|&s| f64::from(s) * f64::from(s)).sum();
                (e / frame.len() as f64) as f32
            })
            .collect();

        AudioFeatures {
            sample_count: n,
            rms: (sum_sq / n as f64).sqrt() as f32,
            peak,
            zero_crossing_rate: crossings as f32 / n as f32,
            frame_energies,
        }
    }
}
