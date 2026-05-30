//! excalibur-trellis :: 512MB fixed KV-pool arena allocator
//! [STATUS: DONE] EXCALIBUR v1000.0.0 component crate.

use std::sync::Mutex;
use thiserror::Error;

pub const ARENA_SIZE: usize = 512 * 1024 * 1024; // 512 MB
pub const BLOCK_SIZE: usize = 4096; // 4 KB
pub const TOTAL_BLOCKS: usize = ARENA_SIZE / BLOCK_SIZE;

#[derive(Error, Debug, PartialEq)]
pub enum ArenaError {
    #[error("Out of memory: No free blocks available in the arena.")]
    OutOfMemory,
    #[error("Invalid block offset: {0}")]
    InvalidOffset(usize),
}

/// A fixed-size 512MB arena allocator for KV-pool.
/// Divides memory into 4KB blocks for OOM-safe alloc/free operations.
pub struct KvArena {
    memory: Box<[u8]>,
    free_blocks: Vec<usize>,
}

impl KvArena {
    /// Creates a new arena, allocating exactly 512MB of memory.
    pub fn new() -> Self {
        let mut free_blocks = Vec::with_capacity(TOTAL_BLOCKS);
        // Populate the free list with block offsets (reversed for cache locality on pop)
        for i in (0..TOTAL_BLOCKS).rev() {
            free_blocks.push(i * BLOCK_SIZE);
        }

        // Allocate 512MB initialized to 0
        let memory = vec![0u8; ARENA_SIZE].into_boxed_slice();

        Self {
            memory,
            free_blocks,
        }
    }

    /// Allocates a 4KB block, returning its offset within the arena.
    /// Returns `ArenaError::OutOfMemory` if no blocks are available.
    pub fn alloc(&mut self) -> Result<usize, ArenaError> {
        self.free_blocks.pop().ok_or(ArenaError::OutOfMemory)
    }

    /// Frees a block given its offset.
    pub fn free(&mut self, offset: usize) -> Result<(), ArenaError> {
        if offset % BLOCK_SIZE != 0 || offset >= ARENA_SIZE {
            return Err(ArenaError::InvalidOffset(offset));
        }
        self.free_blocks.push(offset);
        Ok(())
    }

    /// Retrieves a mutable reference to a block's memory.
    pub fn get_block_mut(&mut self, offset: usize) -> Result<&mut [u8], ArenaError> {
        if offset % BLOCK_SIZE != 0 || offset >= ARENA_SIZE {
            return Err(ArenaError::InvalidOffset(offset));
        }
        Ok(&mut self.memory[offset..offset + BLOCK_SIZE])
    }

    /// Retrieves a read-only reference to a block's memory.
    pub fn get_block(&self, offset: usize) -> Result<&[u8], ArenaError> {
        if offset % BLOCK_SIZE != 0 || offset >= ARENA_SIZE {
            return Err(ArenaError::InvalidOffset(offset));
        }
        Ok(&self.memory[offset..offset + BLOCK_SIZE])
    }

    /// Returns the number of currently available blocks.
    pub fn available_blocks(&self) -> usize {
        self.free_blocks.len()
    }
}

/// Thread-safe wrapper for the arena
pub struct ThreadSafeKvArena {
    inner: Mutex<KvArena>,
}

impl ThreadSafeKvArena {
    pub fn new() -> Self {
        Self {
            inner: Mutex::new(KvArena::new()),
        }
    }

    pub fn alloc(&self) -> Result<usize, ArenaError> {
        self.inner.lock().unwrap().alloc()
    }

    pub fn free(&self, offset: usize) -> Result<(), ArenaError> {
        self.inner.lock().unwrap().free(offset)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_alloc_free() {
        let mut arena = KvArena::new();
        assert_eq!(arena.available_blocks(), TOTAL_BLOCKS);

        let offset = arena.alloc().expect("Should allocate");
        assert_eq!(arena.available_blocks(), TOTAL_BLOCKS - 1);

        arena.free(offset).expect("Should free");
        assert_eq!(arena.available_blocks(), TOTAL_BLOCKS);
    }

    #[test]
    fn test_oom() {
        let mut arena = KvArena::new();
        // Exhaust the arena
        for _ in 0..TOTAL_BLOCKS {
            assert!(arena.alloc().is_ok());
        }

        // Next allocation should fail
        assert_eq!(arena.alloc(), Err(ArenaError::OutOfMemory));
    }

    #[test]
    fn test_invalid_free() {
        let mut arena = KvArena::new();
        // Trying to free an unaligned offset
        assert_eq!(arena.free(1), Err(ArenaError::InvalidOffset(1)));
        // Trying to free an out-of-bounds offset
        assert_eq!(arena.free(ARENA_SIZE), Err(ArenaError::InvalidOffset(ARENA_SIZE)));
    }
}
