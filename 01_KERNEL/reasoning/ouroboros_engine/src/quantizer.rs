// SPDX-License-Identifier: MIT

pub fn quantize_1_58b(weights: &[f32]) -> Vec<f32> {
    if weights.is_empty() {
        return Vec::new();
    }

    // Hardware-native scaling factor: mean of absolute weights
    let gamma: f32 = weights.iter().map(|&w| w.abs()).sum::<f32>() / weights.len() as f32;
    
    // Scale, round, and clamp to {-1, 0, 1}
    let eps = 1e-7;
    let scale = gamma + eps;
    
    weights
        .iter()
        .map(|&w| (w / scale).round().clamp(-1.0, 1.0))
        .collect()
}
