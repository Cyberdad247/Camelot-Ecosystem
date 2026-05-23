pub fn quantize_1_58b(weights: &[f32]) -> Vec<f32> {
    weights.iter().map(|&w| w.round().clamp(-1.0, 1.0)).collect()
}
