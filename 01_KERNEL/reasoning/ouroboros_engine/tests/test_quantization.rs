use ouroboros_engine::quantizer::quantize_1_58b;

#[test]
fn test_bitnet_quantization_clipping() {
    let weights = vec![0.5, -1.2, 0.8, 0.1];
    let quantized = quantize_1_58b(&weights);
    // 1.58-bit should map to {-1, 0, 1}
    assert!(quantized.iter().all(|&x| x == -1.0 || x == 0.0 || x == 1.0));
    assert_eq!(quantized.len(), weights.len());
}
