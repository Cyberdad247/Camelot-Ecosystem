use criterion::{black_box, criterion_group, criterion_main, Criterion};
use excalibur_trellis::{KvArena, ThreadSafeKvArena};

fn bench_alloc_free(c: &mut Criterion) {
    c.bench_function("arena_alloc_free_single", |b| {
        let mut arena = KvArena::new();
        b.iter(|| {
            let offset = arena.alloc().unwrap();
            arena.free(black_box(offset)).unwrap();
        })
    });

    c.bench_function("arena_alloc_free_threadsafe", |b| {
        let arena = ThreadSafeKvArena::new();
        b.iter(|| {
            let offset = arena.alloc().unwrap();
            arena.free(black_box(offset)).unwrap();
        })
    });
}

criterion_group!(benches, bench_alloc_free);
criterion_main!(benches);
