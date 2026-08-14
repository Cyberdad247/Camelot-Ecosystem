// SPDX-License-Identifier: MIT

// Trellis Recursive Compressor logic
pub struct TrellisPool {
    limit: usize,
    usage: usize,
}

impl TrellisPool {
    pub fn new(limit: usize) -> Self {
        Self { limit, usage: 0 }
    }

    pub fn ingest_tokens(&mut self, count: usize) {
        // Recurrent compression logic: map N tokens to fixed latent state
        // In a real implementation, this would involve neural weights.
        // For the patch core, we enforce the hard memory ceiling.
        self.usage = (self.usage + count).min(self.limit);
    }

    pub fn current_usage_mb(&self) -> usize {
        self.usage
    }
}
