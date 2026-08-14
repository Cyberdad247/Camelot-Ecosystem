// SPDX-License-Identifier: MIT

use ouroboros_engine::trellis::TrellisPool;

#[test]
fn test_trellis_pool_enforcement() {
    let mut pool = TrellisPool::new(512); // 512MB limit
    pool.ingest_tokens(1000000); // Simulate large context
    assert!(pool.current_usage_mb() <= 512);
    assert_eq!(pool.current_usage_mb(), 512);
}
