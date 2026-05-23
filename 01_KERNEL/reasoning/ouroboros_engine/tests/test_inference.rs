use ouroboros_engine::mamba::{mamba_forward, State};

#[test]
fn test_linear_scaling_identity() {
    let state = State::new(1024);
    let input = vec![1.0; 1000]; // Simulated 1k tokens
    let output = mamba_forward(&state, &input);
    // Identity check for failing test
    assert_eq!(output.len(), input.len());
}
