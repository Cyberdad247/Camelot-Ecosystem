use ouroboros_engine::quantizer::quantize_1_58b;

#[test]
fn test_bitnet_quantization_clipping() {
    // Case 1: Standard weights
    let weights = vec![0.5, -1.2, 0.8, 0.1];
    let quantized = quantize_1_58b(&weights);
    assert!(quantized.iter().all(|&x| x == -1.0 || x == 0.0 || x == 1.0));
    
    // Case 2: Small weights that require scaling to reach 1.0
    // mean(|w|) = (0.1 + 0.1 + 0.1 + 0.1) / 4 = 0.1
    // w / mean = [1.0, 1.0, 1.0, 1.0]
    let small_weights = vec![0.1, 0.1, 0.1, 0.1];
    let quantized_small = quantize_1_58b(&small_weights);
    assert_eq!(quantized_small, vec![1.0, 1.0, 1.0, 1.0]);

    // Case 3: Mixed small weights
    // mean(|w|) = (0.01 + 0.02 + 0.03 + 0.04) / 4 = 0.025
    // w / mean = [0.4, 0.8, 1.2, 1.6]
    // round -> [0, 1, 1, 2]
    // clamp -> [0, 1, 1, 1]
    let mixed_small = vec![0.01, 0.02, 0.03, 0.04];
    let quantized_mixed = quantize_1_58b(&mixed_small);
    assert_eq!(quantized_mixed, vec![0.0, 1.0, 1.0, 1.0]);
}
