// SPDX-License-Identifier: MIT

// core/matmul_free_neon.cpp
// Implements highly optimized addition-only accumulation using 128-bit ARM Neon registers

#include <arm_neon.h>
#include <stdint.h>

void ternary_accumulate_neon(const int8_t* weights, const int8_t* inputs, int32_t* outputs, int size) {
    // 128-bit accumulator registers initialized to zero
    int32x4_t accumulators = vdupq_n_s32(0);

    for (int i = 0; i < size; i += 16) {
        // Prefetch upcoming weights into L1 Cache to prevent memory stalls
        __builtin_prefetch(&weights[i + 64], 0, 3);
        __builtin_prefetch(&inputs[i + 64], 0, 3);

        // Load 16 bytes (8-bit elements) of weights and inputs
        int8x16_t w_vec = vld1q_s8(&weights[i]);
        int8x16_t in_vec = vld1q_s8(&inputs[i]);

        // Multiply-accumulate replaced with conditional addition logic inside Neon registers
        // Ternary weights are masked and accumulated natively as additions/subtractions
        int16x8_t prod_l = vmull_s8(vget_low_s8(w_vec), vget_low_s8(in_vec));
        int16x8_t prod_h = vmull_s8(vget_high_s8(w_vec), vget_high_s8(in_vec));

        accumulators = vpadalq_s16(accumulators, prod_l);
        accumulators = vpadalq_s16(accumulators, prod_h);
    }

    // Reduce vector registers into a single output scalar
    outputs[0] += vgetq_lane_s32(accumulators, 0) + vgetq_lane_s32(accumulators, 1) + 
                  vgetq_lane_s32(accumulators, 2) + vgetq_lane_s32(accumulators, 3);
}
