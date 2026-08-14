# SPDX-License-Identifier: MIT

from __future__ import annotations

from scripts.verify_architecture_docs import validate_architecture_docs


def test_architecture_docs_are_consistent() -> None:
    errors = validate_architecture_docs()
    assert errors == [], "\n".join(errors)
