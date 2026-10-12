# SPDX-License-Identifier: MIT
# <!-- Copyright © 2026 Invisioned Marketing inc. All Rights Reserved. -->
"""
INVARIANT-4: Spectral Decomposition with Residual Correction
Enforces:
1. Low-rank SVD (rank k=64) projection preserving Hilbert space spectral norms.
2. Sparse 1.58-bit ternary quantized residual matrix {-1, 0, +1} representation.
3. Cosine-divergence triggered lazy evaluation (only applies correction if divergence > 0.038%).
4. fp32 internal accumulation registers to eliminate half-precision catastrophic cancellation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass
class SpectralProjectionResult:
    projected_vector: np.ndarray
    rank: int
    residual_applied: bool
    cosine_divergence: float
    error_bound_satisfied: bool


class SpectralProjectionEngine:
    """Manages low-rank matrix decomposition and 1.58-bit ternary residual error correction."""

    def __init__(self, rank: int = 64, divergence_threshold: float = 0.00038):
        self.rank: int = rank
        self.divergence_threshold: float = divergence_threshold  # 0.038% error bound

    def factorize_weight_matrix(self, weights: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
        """Perform truncated SVD (rank k=64) and quantize residual to 1.58-bit ternary {-1, 0, +1}.

        Returns (U_k, S_k, V_k_T, ternary_residual, scale_factor).
        """
        assert weights.ndim == 2, "Weights must be a 2D matrix"
        rows, cols = weights.shape
        k = min(self.rank, rows, cols)

        # Full SVD in fp32
        u, s, vt = np.linalg.svd(weights.astype(np.float32), full_matrices=False)

        u_k = u[:, :k]
        s_k = s[:k]
        vt_k = vt[:k, :]

        # Low-rank reconstruction
        w_k = np.dot(u_k * s_k, vt_k)

        # Exact residual in fp32
        residual = weights.astype(np.float32) - w_k

        # Quantize residual to 1.58-bit ternary {-1, 0, +1} with scale alpha
        abs_res = np.abs(residual)
        alpha = float(np.mean(abs_res)) if np.mean(abs_res) > 0 else 1.0
        ternary_res = np.zeros_like(residual, dtype=np.int8)

        # Threshold at 0.5 * alpha
        ternary_res[residual > 0.5 * alpha] = 1
        ternary_res[residual < -0.5 * alpha] = -1

        return u_k, s_k, vt_k, ternary_res, alpha

    def project_and_correct(
        self,
        input_vec: np.ndarray,
        u_k: np.ndarray,
        s_k: np.ndarray,
        vt_k: np.ndarray,
        ternary_res: np.ndarray,
        alpha: float,
        anchor_vec: Optional[np.ndarray] = None,
    ) -> SpectralProjectionResult:
        """Projects input_vec through rank-k matrices, evaluates cosine divergence,

        and applies 1.58-bit ternary residual correction only if threshold exceeded.
        """
        x = input_vec.astype(np.float32)

        # Low-rank projection: y_k = U_k * (S_k * (V_k_T * x))
        # O(kd) complexity
        temp = np.dot(vt_k, x)
        temp = temp * s_k
        y_k = np.dot(u_k, temp).astype(np.float32)

        # Calculate cosine divergence against anchor if provided
        divergence = 0.0
        if anchor_vec is not None:
            norm_y = np.linalg.norm(y_k)
            norm_a = np.linalg.norm(anchor_vec)
            if norm_y > 1e-9 and norm_a > 1e-9:
                cos_sim = float(np.dot(y_k, anchor_vec) / (norm_y * norm_a))
                divergence = max(0.0, 1.0 - cos_sim)

        # Cosine-triggered lazy evaluation
        residual_applied = False
        final_y = y_k.copy()

        if divergence > self.divergence_threshold or anchor_vec is None:
            # Apply ternary residual: r = alpha * (ternary_res * x)
            # Computationally lightweight integer dot product scaled by alpha
            ternary_dot = np.dot(ternary_res.astype(np.float32), x)
            correction = (alpha * ternary_dot).astype(np.float32)
            final_y = y_k + correction
            residual_applied = True

            # Recalculate divergence after correction
            if anchor_vec is not None:
                norm_final = np.linalg.norm(final_y)
                if norm_final > 1e-9 and norm_a > 1e-9:
                    new_sim = float(np.dot(final_y, anchor_vec) / (norm_final * norm_a))
                    divergence = max(0.0, 1.0 - new_sim)

        satisfied = divergence <= self.divergence_threshold

        return SpectralProjectionResult(
            projected_vector=final_y,
            rank=self.rank,
            residual_applied=residual_applied,
            cosine_divergence=divergence,
            error_bound_satisfied=satisfied,
        )
