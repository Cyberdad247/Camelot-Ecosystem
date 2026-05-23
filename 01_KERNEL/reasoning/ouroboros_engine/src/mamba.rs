// Simplified Mamba State
pub struct State {
    pub dimension: usize,
    pub latent: Vec<f32>,
}

impl State {
    pub fn new(dimension: usize) -> Self {
        Self { 
            dimension,
            latent: vec![0.0; dimension],
        }
    }
}

#[derive(Debug, PartialEq)]
pub enum LayerType {
    Attention,
    MambaSelectiveScan,
}

pub fn get_layer_type(index: usize) -> LayerType {
    if index % 4 == 0 {
        LayerType::MambaSelectiveScan
    } else {
        LayerType::Attention
    }
}

// Mamba forward pass with Selective Scan recurrence
pub fn mamba_forward(state: &mut State, input: &[f32]) -> Vec<f32> {
    assert_eq!(input.len(), state.dimension, "Input dimension must match state dimension");
    // TODO(Ouroboros): Implement data-dependent SSM parameters (A, B, C, Delta) per step.

    // Selective Scan: h_t = A * h_{t-1} + B * x_t
    // For this minimal implementation, we use a fixed A (0.9) and B (1.0)
    // to verify state persistence across sequence steps.
    
    let a = 0.9f32;
    let b = 1.0f32;

    for (l, &x) in state.latent.iter_mut().zip(input.iter()) {
        *l = a * (*l) + b * x;
    }

    state.latent.clone()
}
