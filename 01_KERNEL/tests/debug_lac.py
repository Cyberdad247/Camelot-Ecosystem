# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import sys
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Mocks for "kernel" packages
mock_prism = MagicMock()
sys.modules['kernel.Engines.prism_gateway'] = mock_prism
mock_coherence = MagicMock()
sys.modules['kernel.Engines.coherence_engine'] = mock_coherence

# Read Source
with open(r'c:\Users\vizio\CAMELOT_OS\01_KERNEL\agora\videneptus.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Patch Imports
code = code.replace('from .node import AgentNode', 'class AgentNode: \n    def __init__(self, name): pass\n    async def send(self, router, recipient, protocol, payload): pass')
code = code.replace('from .protocol import ANPEnvelope', 'class ANPEnvelope: pass')
code = code.replace('from .router import AgoraRouter', 'class AgoraRouter: \n    def register(self, x): pass')

# Patch __init__ imports (dynamic)
code = code.replace('from kernel.agora.knights.notebook_knight import NotebookKnight', 'class NotebookKnight: \n    def __init__(self, name): pass')
code = code.replace('from kernel.agora.knights.omni_knight import OmniKnight', 'class OmniKnight: \n    def __init__(self, name, default_role=""): pass')

print("--- Defining Videneptus ---")
try:
    # We need to provide the mocked modules in the globals
    env = {
        'json': __import__('json'),
        'PrismAdapter': mock_prism.PrismAdapter,
        'coherence': mock_coherence.coherence,
        '__name__': '__main__'
    }
    
    exec(code, env)
    print("--- Class Defined ---")
    
    Videneptus = env['Videneptus']
    v = Videneptus()
    print("--- Instance Created ---")
    
    async def test():
        # Setup mocks
        mock_prism.PrismAdapter.transmit = AsyncMock(side_effect=[
             "Key 1: Microservices",
             "Score: 90",
             "Plan: Execute"
        ])
        
        print("--- Executing LaC Loop ---")
        res = await v.execute_lac_loop("Test Prompt", "CTX")
        print("\n--- RESULT ---")
        print(res)
    
    asyncio.run(test())

except Exception as e:
    import traceback
    traceback.print_exc()