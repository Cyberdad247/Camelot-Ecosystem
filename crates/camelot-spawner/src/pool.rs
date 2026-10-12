//! Pre-Warmed MicroVM Phial Pool (3.6GB Scarcity Protocol Governor)
//! ===============================================================
//!
//! Restricts swarm to max 5 pre-warmed 'Phial' MicroVMs (128 MiB each)
//! to guarantee thermal and memory equilibrium on Raspberry Pi 5 / ARM64.

use crate::firecracker::FirecrackerVMM;
use std::collections::VecDeque;
use tracing::{info, warn};

pub const DEFAULT_POOL_CAPACITY: usize = 5;

pub struct VMPool {
    capacity: usize,
    available_vms: VecDeque<FirecrackerVMM>,
    active_count: usize,
}

impl VMPool {
    pub fn new(capacity: usize) -> Self {
        info!("Initializing VMPool with strict capacity of {}", capacity);
        Self {
            capacity,
            available_vms: VecDeque::with_capacity(capacity),
            active_count: 0,
        }
    }

    pub fn prewarm_pool(&mut self) -> usize {
        info!("Pre-warming VMPool up to capacity {}...", self.capacity);
        while self.available_vms.len() + self.active_count < self.capacity {
            let id = format!("phial_{}", self.available_vms.len() + self.active_count + 1);
            let vmm = FirecrackerVMM::new(&id);
            let _ = vmm.configure_boot_source();
            let _ = vmm.configure_machine();
            self.available_vms.push_back(vmm);
        }
        info!("Pre-warmed {} available Phials in pool.", self.available_vms.len());
        self.available_vms.len()
    }

    pub fn acquire_vm(&mut self) -> Option<FirecrackerVMM> {
        if let Some(vm) = self.available_vms.pop_front() {
            self.active_count += 1;
            info!("Acquired Phial VM [{}]. Remaining in pool: {}", vm.id, self.available_vms.len());
            Some(vm)
        } else {
            warn!("VMPool exhausted! No available pre-warmed Phials.");
            None
        }
    }

    pub fn release_vm(&mut self, vm: FirecrackerVMM) {
        if self.available_vms.len() + self.active_count <= self.capacity && self.active_count > 0 {
            self.active_count -= 1;
            self.available_vms.push_back(vm);
            info!("Released Phial back to pool. Available: {}", self.available_vms.len());
        } else {
            warn!("VMPool overflow attempt: dropping released VM [{}]", vm.id);
        }
    }

    pub fn capacity(&self) -> usize {
        self.capacity
    }

    pub fn available_count(&self) -> usize {
        self.available_vms.len()
    }

    pub fn active_count(&self) -> usize {
        self.active_count
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pool_lifecycle_and_5_node_cap() {
        let mut pool = VMPool::new(DEFAULT_POOL_CAPACITY);
        assert_eq!(pool.capacity(), DEFAULT_POOL_CAPACITY);
        assert_eq!(pool.available_count(), 0);

        let prewarmed = pool.prewarm_pool();
        assert_eq!(prewarmed, 5);
        assert_eq!(pool.available_count(), 5);

        // Acquire 5 VMs
        let mut acquired = Vec::new();
        for _ in 0..5 {
            let vm = pool.acquire_vm().expect("must acquire");
            acquired.push(vm);
        }

        assert_eq!(pool.available_count(), 0);
        assert_eq!(pool.active_count(), 5);

        // 6th acquire must fail (exhausted / capped)
        assert!(pool.acquire_vm().is_none());

        // Release one VM
        let vm = acquired.pop().unwrap();
        pool.release_vm(vm);
        assert_eq!(pool.available_count(), 1);
        assert_eq!(pool.active_count(), 4);
    }
}
