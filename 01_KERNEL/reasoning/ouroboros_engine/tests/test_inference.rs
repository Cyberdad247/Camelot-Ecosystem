// SPDX-License-Identifier: MIT

use ouroboros_engine::{mamba_forward, State};

#[test]
fn test_ssm_state_persistence() {
    let mut state = State::new(10);
    let input = vec![1.0; 10];
    
    // First pass
    let output1 = mamba_forward(&mut state, &input);
    // Second pass with same input
    let output2 = mamba_forward(&mut state, &input);
    
    // In a stateful SSM, output2 should be different from output1 
    // because the state has been updated.
    assert_ne!(output1, output2, "State should persist and influence subsequent outputs");
}

#[test]
fn test_linear_scaling_identity() {
    let mut state = State::new(1024);
    let input = vec![1.0; 1024]; // Simulated 1k tokens
    let output = mamba_forward(&mut state, &input);
    // Length check
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
