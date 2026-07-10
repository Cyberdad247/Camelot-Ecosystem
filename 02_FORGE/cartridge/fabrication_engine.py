# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge Fabrication Engine (Node 3)

The assembly line for Project Chimera's dynamic agents. 
Uses template-driven synthesis to compile Just-in-Time (JIT) cartridges.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

from .cartridge_schemas import (
    CartridgeManifest, 
    JITToolAdapter, 
    APIMethod, 
    SandboxConstraints,
    STRATEGY_CARTRIDGE_TEMPLATE,
    ENGINEERING_CARTRIDGE_TEMPLATE,
    CREATIVE_CARTRIDGE_TEMPLATE,
    OPERATIONS_CARTRIDGE_TEMPLATE
)

class CartridgeFabricator:
    """
    Engine for synthesizing and deploying dynamic agent cartridges.
    Orchestrates the lifecycle from specification to signed manifest.
    """
    
    TEMPLATES = {
        "strategy": STRATEGY_CARTRIDGE_TEMPLATE,
        "engineering": ENGINEERING_CARTRIDGE_TEMPLATE,
        "creative": CREATIVE_CARTRIDGE_TEMPLATE,
        "operations": OPERATIONS_CARTRIDGE_TEMPLATE
    }

    def __init__(self, output_dir: str = "packages", *, rbac: Any = None,
                 principal: Optional[str] = None):
        self.output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), output_dir))
        os.makedirs(self.output_dir, exist_ok=True)
        # Optional lifecycle authorization. When set, fabricating a trusted (signed)
        # cartridge requires the principal to hold cartridge:fabricate + cartridge:sign.
        self.rbac = rbac
        self.principal = principal
        print(f"[Fabricator] Factory online. Output: {self.output_dir}")

    def fabricate(self, spec: Dict[str, Any], *, principal: Optional[str] = None) -> CartridgeManifest:
        """
        Synthesize a cartridge manifest from a partial specification.
        Uses templates to fill in defaults and enforces security constraints.
        If an RBAC policy is configured, the acting principal must be authorized to
        fabricate and sign before a trusted signature is produced.
        """
        acting = principal or self.principal
        if self.rbac is not None:
            from .cartridge_rbac import CAP_FABRICATE, CAP_SIGN
            self.rbac.require(acting, CAP_FABRICATE)
            self.rbac.require(acting, CAP_SIGN)

        template_key = spec.get("type", "engineering")
        template = self.TEMPLATES.get(template_key, ENGINEERING_CARTRIDGE_TEMPLATE).copy()
        
        # Merge spec into template
        cartridge_id = spec.get("cartridge_id", f"JIT_{template['cartridge_id']}_{int(datetime.utcnow().timestamp())}")
        
        manifest_data = {
            "cartridge_id": cartridge_id,
            "version": spec.get("version", "1.0.0"),
            "description": spec.get("description", template["description"]),
            "agents": list(set(template["agents"] + spec.get("agents", []))),
            "tools": list(set(template["tools"] + spec.get("tools", []))),
            "protocols": list(set(template["protocols"] + spec.get("protocols", []))),
            "capabilities": list(set(template["capabilities"] + spec.get("capabilities", []))),
            "risk_profile": spec.get("risk_profile", template["risk_profile"]),
            "governance": spec.get("governance", {}),
            "hooks": spec.get("hooks", {}),
            "embeddings": spec.get("embeddings", {}),
            "signature": "pending_calc",  # Will be updated after construction
            "created_at": datetime.utcnow().isoformat(),
            "created_by": "CartridgeFabricator_v1"
        }

        # Instantiate first so the signature covers the FULLY-resolved manifest
        # (with all schema defaults expanded) — the exact form the sandbox verifies.
        manifest = CartridgeManifest(**manifest_data)
        manifest.signature = self._calculate_signature(manifest)

        # Persist to disk
        self._persist_cartridge(manifest)
        
        return manifest

    def compile_jit_tool(self, tool_spec: Dict[str, Any]) -> JITToolAdapter:
        """
        Compile a Just-in-Time (JIT) tool adapter for external API integration.
        """
        adapter_id = tool_spec.get("adapter_id", f"jit_adapter_{int(datetime.utcnow().timestamp())}")
        
        methods = {}
        for m_name, m_data in tool_spec.get("methods", {}).items():
            methods[m_name] = APIMethod(
                method=m_data.get("method", "GET"),
                params=m_data.get("params", []),
                response_map=m_data.get("response_map", {})
            )

        adapter = JITToolAdapter(
            adapter_id=adapter_id,
            type=tool_spec.get("type", "api_wrapper"),
            endpoint=tool_spec.get("endpoint", ""),
            auth=tool_spec.get("auth", "none"),
            methods=methods,
            sandbox_constraints=SandboxConstraints(
                timeout_ms=tool_spec.get("timeout_ms", 1500),
                max_calls_per_minute=tool_spec.get("rate_limit", 20)
            )
        )
        
        print(f"[Fabricator] JIT Tool Compiled: {adapter_id}")
        return adapter

    def _calculate_signature(self, manifest: "CartridgeManifest") -> str:
        """
        Produce a real cryptographic signature (Ed25519, or HMAC fallback) over the
        fully-resolved manifest content. If no signing key is configured, degrade
        LOUDLY to a legacy SHA-256 checksum tagged ``sha256:`` — which the sandbox
        treats as UNSIGNED and will reject in STRICT mode. Fabrication should never
        silently ship trusted-looking-but-forgeable manifests.
        """
        from . import cartridge_crypto
        try:
            return cartridge_crypto.sign(manifest)
        except cartridge_crypto.SigningError as e:
            checksum = hashlib.sha256(cartridge_crypto.canonical_bytes(manifest)).hexdigest()
            print(f"[Fabricator][WARN] No signing key ({e}). Emitting UNSIGNED checksum "
                  f"— sandbox STRICT mode will reject this cartridge. "
                  f"Run `python -m cartridge.cartridge_crypto keygen` to enable signing.")
            return f"sha256:{checksum}"

    def _persist_cartridge(self, manifest: CartridgeManifest):
        """Save fabricated cartridge to the local packages directory."""
        package_path = os.path.join(self.output_dir, manifest.cartridge_id)
        os.makedirs(package_path, exist_ok=True)
        
        # Save manifest
        with open(os.path.join(package_path, "manifest.json"), "w") as f:
            if hasattr(manifest, "model_dump_json"):
                f.write(manifest.model_dump_json(indent=2))
            else:
                f.write(manifest.json(indent=2))
            
        # Create empty persona logic if missing
        persona_path = os.path.join(package_path, "persona.py")
        if not os.path.exists(persona_path):
            with open(persona_path, "w") as f:
                f.write(f'"""Persona logic for {manifest.cartridge_id}"""\n\n')
                f.write('class FabricatedPersona:\n    pass\n')

        print(f"[Fabricator] Cartridge Persisted: {package_path}")

if __name__ == "__main__":
    # Test fabrication
    fab = CartridgeFabricator()
    
    # Define a custom spec
    custom_spec = {
        "cartridge_id": "CYBER_SEC_V0",
        "type": "operations",
        "agents": ["Sir_Galahad"],
        "tools": ["FirewallGen", "PortScanner"],
        "capabilities": ["cyber_defense", "incident_response"]
    }
    
    manifest = fab.fabricate(custom_spec)
    print(f"Fabricated {manifest.cartridge_id} with signature {manifest.signature[:16]}...")