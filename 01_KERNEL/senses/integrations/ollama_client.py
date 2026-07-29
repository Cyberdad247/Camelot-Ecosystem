# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY

# -*- coding: utf-8 -*-
"""
OLLAMA INTEGRATION MODULE
Connects Camelot OS to local Ollama inference via the Zero-Trust Vault.

USAGE:
    from ollama_client import OllamaClient
    client = OllamaClient()
    response = client.generate("llama3.2", "Explain quantum computing")
"""
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# Add vault directory to path for vault_manager import
sys.path.append(str(Path(__file__).parents[3] / "03_VAULT"))
from vault_manager import VaultManager


class OllamaClient:
    """Client for interacting with local Ollama API."""
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.vault = VaultManager()
        
        # API key is optional for local Ollama
        try:
            self.api_key = self.vault.get("OLLAMA_API_KEY")
        except:
            self.api_key = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional API key."""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a completion from Ollama.
        
        Args:
            model: Model name (e.g., "llama3.2", "mistral")
            prompt: User prompt
            system: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            Response dictionary with 'response' key containing generated text
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        if system:
            payload["system"] = system
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=300  # Longer timeout for generation
        )
        
        if not response.ok:
            print(f"[ERROR] Ollama API returned {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
        
        response.raise_for_status()
        
        return response.json()
    
    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Chat completion with message history.
        
        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            Response dictionary with 'message' key containing the assistant's reply
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=300  # Longer timeout for chat
        )
        response.raise_for_status()
        
        return response.json()
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models.
        
        Returns:
            List of model dictionaries
        """
        url = f"{self.base_url}/api/tags"
        
        response = requests.get(
            url,
            headers=self._get_headers(),
            timeout=30
        )
        response.raise_for_status()
        
        return response.json().get("models", [])
    
    def pull_model(self, model: str) -> Dict[str, Any]:
        """
        Pull a model from the Ollama library.
        
        Args:
            model: Model name to pull
        
        Returns:
            Status dictionary
        """
        url = f"{self.base_url}/api/pull"
        
        payload = {"name": model}
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=600  # Model pulls can take a while
        )
        response.raise_for_status()
        
        return response.json()
    
    def embeddings(self, model: str, text: str) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            model: Model name (e.g., "nomic-embed-text")
            text: Text to embed
        
        Returns:
            List of embedding values
        """
        url = f"{self.base_url}/api/embeddings"
        
        payload = {
            "model": model,
            "prompt": text
        }
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json().get("embedding", [])


def main():
    """CLI demo of Ollama integration."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python ollama_client.py <model> <prompt>")
        print("Example: python ollama_client.py llama3.2 'What is the Law of Locality?'")
        return
    
    model = sys.argv[1]
    prompt = " ".join(sys.argv[2:])
    
    client = OllamaClient()
    
    print(f"[OLLAMA] Generating with {model}...")
    response = client.generate(
        model=model,
        prompt=prompt,
        system="You are a helpful AI assistant for Camelot OS."
    )
    
    print(f"\n[RESPONSE]\n{response.get('response', 'No response')}")


if __name__ == "__main__":
    main()
