// BitNet b1.58 Ternary Quantizer (OMEGA-PATCH / EXCALIBUR_A_QNF Phase 7)
//
// Implements the real BitNet b1.58 absmean quantization scheme rather than a
// naive round(). Weights are scaled by their mean absolute value, then mapped
// to the ternary set {-1, 0, 1}. This is the scheme that lets a 13B model run
// in ~4GB of RAM via integer accumulation (v999 / v700 NLM).
//
//   scale = (1/n) * Σ|w_i|              (absmean)
//   q_i   = clamp(round(w_i / scale), -1, 1)

/// Compute the absmean scale factor for a weight vector.
pub fn absmean_scale(weights: &[f32]) -> f32 {
    if weights.is_empty() {
        return 1.0;
    }
    let sum_abs: f32 = weights.iter().map(|w| w.abs()).sum();
    let scale = sum_abs / weights.len() as f32;
    // Guard against an all-zero vector (scale 0 -> div by zero).
    if scale <= f32::EPSILON {
        1.0
    } else {
        scale
    }
}

/// Quantize to ternary {-1, 0, 1} using BitNet b1.58 absmean scaling.
/// Returns the ternary weights (as f32 for downstream compatibility).
pub fn quantize_1_58b(weights: &[f32]) -> Vec<f32> {
    let scale = absmean_scale(weights);
    weights
        .iter()
        .map(|&w| (w / scale).round().clamp(-1.0, 1.0))
        .collect()
}

/// Quantize and also return the scale, so the consumer can reconstruct the
/// approximate magnitude (dequant = q * scale). Used by the matmul-free path
/// for integer accumulation with a single per-tensor scale.
pub fn quantize_1_58b_scaled(weights: &[f32]) -> (Vec<f32>, f32) {
    let scale = absmean_scale(weights);
    let q = weights
        .iter()
        .map(|&w| (w / scale).round().clamp(-1.0, 1.0))
        .collect();
    (q, scale)
}

/// Fraction of weights pruned to exactly 0 by quantization — a useful sparsity
/// metric (BitNet b1.58 typically drives substantial sparsity).
pub fn sparsity(quantized: &[f32]) -> f32 {
    if quantized.is_empty() {
        return 0.0;
    }
    let zeros = quantized.iter().filter(|&&x| x == 0.0).count();
    zeros as f32 / quantized.len() as f32
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ternary_domain_enforced() {
        let q = quantize_1_58b(&[0.5, -1.2, 0.8, 0.1, 0.0, 3.4]);
        assert!(q.iter().all(|&x| x == -1.0 || x == 0.0 || x == 1.0));
    }

    #[test]
    fn absmean_scale_is_mean_of_abs() {
        let s = absmean_scale(&[1.0, -1.0, 1.0, -1.0]);
        assert!((s - 1.0).abs() < 1e-6);
    }

    #[test]
    fn all_zero_vector_safe() {
        let q = quantize_1_58b(&[0.0, 0.0, 0.0]);
        assert!(q.iter().all(|&x| x == 0.0));
        assert_eq!(sparsity(&q), 1.0);
    }

    #[test]
    fn scaled_roundtrip_returns_scale() {
        let (q, scale) = quantize_1_58b_scaled(&[2.0, -2.0, 2.0]);
        assert!(scale > 0.0);
        assert!(q.iter().all(|&x| x == -1.0 || x == 0.0 || x == 1.0));
    }
}
