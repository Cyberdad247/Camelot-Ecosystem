# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Ω_SCOUT_SWARM_PRIME: Perplexity Native Adapter
Enables Lady Apis to forage using 'sonar-pro' with strict JSON Schema output.
"""

import json
import os
from typing import Any, Dict, List

import requests


class ScoutSonar:
    """
    Client for Perplexity's sonar-pro model with schema enforcement.
    Mimics OpenAI client interface for drop-in compatibility.
    """

    API_URL = "https://api.perplexity.ai/chat/completions"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            print("WARNING: PERPLEXITY_API_KEY not set. Scout Swarm running in mock mode.")

        # Define the UKG RepoPhial schema
        self.ukg_schema = {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {"repos": {"type": "array", "items": {"$ref": "#/$defs/RepoPhial"}}},
                    "$defs": {
                        "RepoPhial": {
                            "type": "object",
                            "properties": {
                                "REPO": {"type": "string"},
                                "DOMAIN": {"type": "string", "enum": ["Optimization", "Compression", "Infra"]},
                                "LANGS": {"type": "array", "items": {"type": "string"}},
                                "LICENSE": {"type": "string"},
                                "RESOURCE_IMPACT": {"type": "string"},
                                "TOKEN_IMPACT": {"type": "string"},
                                "ASSIMILATION_STRATEGY": {"type": "string"},
                            },
                            "required": ["REPO", "DOMAIN", "RESOURCE_IMPACT"],
                        }
                    },
                    "required": ["repos"],
                }
            },
        }

    def forage(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a foraging run using sonar-pro.
        """
        if not self.api_key:
            return self._mock_response()

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are LADY APIS, the Swarm Mother. You forage GitHub for high-performance, zero-burn technologies. You strictly adhere to the Law of Velocity (Rust/Go preferred, No GPL).",
                },
                {"role": "user", "content": query},
            ],
            "response_format": self.ukg_schema,
        }

        try:
            response = requests.post(self.API_URL, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse strictly typed JSON
            data = json.loads(content)
            return data.get("repos", [])

        except Exception as e:
            print(f"Error communicating with Perplexity: {e}")
            return []

    def _mock_response(self):
        """Mock response for testing without API key"""
        return [
            {
                "REPO": "mock-kvzip",
                "DOMAIN": "Compression",
                "LANGS": ["Python", "CUDA"],
                "LICENSE": "Apache-2.0",
                "RESOURCE_IMPACT": "3x memory reduction",
                "TOKEN_IMPACT": "70% pruning",
                "ASSIMILATION_STRATEGY": "Wrap as Phial",
            }
        ]


if __name__ == "__main__":
    scout = ScoutSonar()

    print("=" * 60)
    print("Ω_SCOUT_SWARM_PRIME: PERPLEXITY ADAPTER")
    print("=" * 60)

    query = "Find top Rust-based KV cache optimization tools from the last 6 months."
    print(f"Query: {query}")

    repos = scout.forage(query)

    print(f"\nDiscovered {len(repos)} Repos (formatted as UKG RepoPhials):")
    print("-" * 20)
    print(json.dumps(repos, indent=2))