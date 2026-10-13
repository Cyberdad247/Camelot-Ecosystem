// OpenMuse Spatial Canvas — WASM 3D/2D Projection Engine
// Coordinates bound to vfs://worldtree/ and Excalibur HUD

pub struct OpenMuseWASMCanvas {
    pub initialized: bool,
}

impl OpenMuseWASMCanvas {
    pub fn new() -> Self {
        Self { initialized: true }
    }
}
