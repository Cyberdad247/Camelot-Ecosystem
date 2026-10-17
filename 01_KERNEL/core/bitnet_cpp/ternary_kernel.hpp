#pragma once
#include <cstdint>
#include <vector>
#include <string>

namespace camelot {
namespace bitnet {

// BitNet b1.58 Ternary Weights: {-1, 0, +1}
// Packed 2-bit representation:
// 00 -> 0
// 01 -> +1
// 10 -> -1
// 11 -> reserved/padding
enum class TernaryVal : int8_t {
    Zero = 0,
    Positive = 1,
    Negative = -1
};

struct TernaryMatrix {
    size_t rows;
    size_t cols;
    std::vector<int8_t> weights; // values in {-1, 0, 1}

    TernaryMatrix(size_t r, size_t c) : rows(r), cols(c), weights(r * c, 0) {}

    inline int8_t get(size_t r, size_t c) const {
        return weights[r * cols + c];
    }

    inline void set(size_t r, size_t c, int8_t val) {
        weights[r * cols + c] = val;
    }
};

// Pure addition/subtraction GEMV (General Matrix-Vector multiplication)
// Zero float multiplications in the inner loop!
inline void ternary_gemv(
    const TernaryMatrix& mat,
    const float* in_vec,
    float* out_vec,
    float scale = 1.0f
) {
    for (size_t r = 0; r < mat.rows; ++r) {
        float sum = 0.0f;
        const size_t row_offset = r * mat.cols;
        for (size_t c = 0; c < mat.cols; ++c) {
            const int8_t w = mat.weights[row_offset + c];
            if (w == 1) {
                sum += in_vec[c];
            } else if (w == -1) {
                sum -= in_vec[c];
            }
            // w == 0 is skipped (zero cost)
        }
        out_vec[r] = sum * scale;
    }
}

} // namespace bitnet
} // namespace camelot
