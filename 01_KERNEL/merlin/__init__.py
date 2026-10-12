# SPDX-License-Identifier: MIT
"""Camelot-OS Merlin kernel package (regular package marker).

Ensures ``merlin.*`` resolves to ``01_KERNEL/merlin/`` even when other
``sys.path`` entries contain a top-level ``merlin.py`` regular module
(e.g. ``03_VAULT/training/configs/merlin.py``), which would otherwise
shadow this namespace package suite-wide under pytest collection.
Kept intentionally import-light: subpackages are imported explicitly.
"""
