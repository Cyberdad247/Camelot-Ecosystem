from __future__ import annotations

import asyncio
from unittest.mock import patch

from control_plane.bifrost import Bifrost


def test_bifrost_token_reduction_enrichment():
    # 1. Setup mock find_similar_dispatches to return a similar dispatch context
    mock_similar = [{"keywords": ["auth", "token"], "score": 0.85}]

    captured_args = {}

    async def mock_stream_openai(self_obj, base, model, prompt, system, max_tokens):
        captured_args["base"] = base
        captured_args["model"] = model
        captured_args["prompt"] = prompt
        captured_args["system"] = system
        captured_args["max_tokens"] = max_tokens
        yield "Success"

    async def run_test():
        bifrost = Bifrost()
        # Bind the mock method instance
        bifrost._stream_openai = lambda *args, **kwargs: mock_stream_openai(bifrost, *args, **kwargs)

        with patch("control_plane.symbol_compressor.find_similar_dispatches", return_value=mock_similar) as mock_find:
            results = []
            async for chunk in bifrost.stream(
                terminal_id="sir_boris",
                prompt="test prompt",
                system="original system"
            ):
                results.append(chunk)

            assert "".join(results) == "Success"
            mock_find.assert_called_once_with("test prompt", "sir_boris", limit=3)
            assert captured_args["prompt"] == "test prompt"
            assert "Similar past work:" in captured_args["system"]
            assert "['auth', 'token'] (confidence: 0.85)" in captured_args["system"]
            assert "original system" in captured_args["system"]

    asyncio.run(run_test())
