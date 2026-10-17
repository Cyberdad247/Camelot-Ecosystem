// SPDX-License-Identifier: MIT
// Camelot-OS Kernel Micro-Benchmark: Rust / LLVM Performance
// Evaluates:
// 1. Bitwise LCG XOR throughput (acc += (i as u64) ^ 0x5DEECE66D)
// 2. Vector Dot Product on Float32 slices with LLVM autovectorization (AVX2/FMA)

use std::hint::black_box;
use std::time::Instant;

fn main() {
    println!("=== RUST KERNEL BENCHMARK (rustc / LLVM - release) ===");

    // ----------------------------------------------------
    // Task 1: Bitwise LCG XOR Loop (100,000,000 iterations)
    // ----------------------------------------------------
    const XOR_ITERATIONS: u64 = 100_000_000;
    let start_xor = Instant::now();
    let mut acc: u64 = 0;
    for i in 0..XOR_ITERATIONS {
        acc = acc.wrapping_add(i ^ 0x5DEECE66D);
    }
    let elapsed_xor = start_xor.elapsed();
    black_box(acc);

    let ns_per_op_xor = elapsed_xor.as_nanos() as f64 / XOR_ITERATIONS as f64;
    let mops_xor = XOR_ITERATIONS as f64 / elapsed_xor.as_secs_f64() / 1_000_000.0;

    println!(
        "[RUST] Task 1 (XOR 100M ops): {:?} | {:.3} ns/op | {:.2} MOps/sec | sink={}",
        elapsed_xor, ns_per_op_xor, mops_xor, acc
    );

    // ----------------------------------------------------
    // Task 2: Vector Dot Product (10,000,000 f32 elements)
    // ----------------------------------------------------
    const VEC_SIZE: usize = 10_000_000;
    let mut vec_a = Vec::with_capacity(VEC_SIZE);
    let mut vec_b = Vec::with_capacity(VEC_SIZE);
    for i in 0..VEC_SIZE {
        vec_a.push(i as f32 * 0.0001);
        vec_b.push((i % 100) as f32 * 0.01);
    }

    let start_vec = Instant::now();
    let mut dot: f32 = 0.0;
    for i in 0..VEC_SIZE {
        dot += vec_a[i] * vec_b[i];
    }
    let elapsed_vec = start_vec.elapsed();
    black_box(dot);

    let ns_per_elem = elapsed_vec.as_nanos() as f64 / VEC_SIZE as f64;
    let melem_sec = VEC_SIZE as f64 / elapsed_vec.as_secs_f64() / 1_000_000.0;

    println!(
        "[RUST] Task 2 (Dot Product 10M f32): {:?} | {:.3} ns/elem | {:.2} MElem/sec | dot={}",
        elapsed_vec, ns_per_elem, melem_sec, dot
    );
}
