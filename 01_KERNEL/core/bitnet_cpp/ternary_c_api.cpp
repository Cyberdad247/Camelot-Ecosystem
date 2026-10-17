// SPDX-License-Identifier: MIT
// ============================================================================
// CAMELOT-OS :: C++20 BITNET b1.58 C-ABI EXPORT ENGINE
// Layer: L1/L2 Substrate & Kinetic Execution
// Invariant: Zero float multiplications, Zero heap copying in packed GEMV
// ============================================================================

#include "ternary_kernel.hpp"
#include <cstdint>
#include <cstddef>

extern "C" {

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT void* bitnet_create_matrix(size_t rows, size_t cols) {
    return new (std::nothrow) camelot::bitnet::TernaryMatrix(rows, cols);
}

EXPORT void bitnet_free_matrix(void* mat_ptr) {
    if (mat_ptr) {
        delete static_cast<camelot::bitnet::TernaryMatrix*>(mat_ptr);
    }
}

EXPORT void bitnet_set_weight(void* mat_ptr, size_t r, size_t c, int8_t val) {
    if (mat_ptr) {
        static_cast<camelot::bitnet::TernaryMatrix*>(mat_ptr)->set(r, c, val);
    }
}

EXPORT void bitnet_gemv(void* mat_ptr, const float* in_vec, float* out_vec, float scale) {
    if (mat_ptr && in_vec && out_vec) {
        camelot::bitnet::ternary_gemv(
            *static_cast<camelot::bitnet::TernaryMatrix*>(mat_ptr),
            in_vec,
            out_vec,
            scale
        );
    }
}

// Zero-copy Packed 2-bit GEMV:
// Operates directly on the Python bytearray without memory copies.
// 2 bits per weight: 00 = 0, 01 = +1, 10 = -1, 11 = padding
EXPORT void bitnet_packed_gemv(
    size_t rows,
    size_t cols,
    const uint8_t* packed_data,
    const float* in_vec,
    float* out_vec
) {
    if (!packed_data || !in_vec || !out_vec) return;

    for (size_t r = 0; r < rows; ++r) {
        float sum = 0.0f;
        const size_t row_base = r * cols;
        for (size_t c = 0; c < cols; ++c) {
            const size_t idx = row_base + c;
            const size_t byte_idx = idx >> 2;
            const uint32_t bit_shift = (idx & 3) << 1;
            const uint8_t raw = (packed_data[byte_idx] >> bit_shift) & 0x03;
            if (raw == 1) {
                sum += in_vec[c];
            } else if (raw == 2) {
                sum -= in_vec[c];
            }
        }
        out_vec[r] = sum;
    }
}

}
