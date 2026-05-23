use ouroboros_engine::mamba::{mamba_forward, State};

#[test]
fn test_linear_scaling_identity() {
    let state = State::new(1024);
    let input = vec![1.0; 1000]; // Simulated 1k tokens
    let output = mamba_forward(&state, &input);
    // Identity check for failing test
    assert_eq!(output.len(), input.len());
}

#[test]
fn test_hybrid_layer_interleaving() {
    use ouroboros_engine::mamba::{get_layer_type, LayerType};
    
    assert_eq!(get_layer_type(0), LayerType::MambaSelectiveScan);
    assert_eq!(get_layer_type(1), LayerType::Attention);
    assert_eq!(get_layer_type(2), LayerType::Attention);
    assert_eq!(get_layer_type(3), LayerType::Attention);
    assert_eq!(get_layer_type(4), LayerType::MambaSelectiveScan);
    assert_eq!(get_layer_type(8), LayerType::MambaSelectiveScan);
}
