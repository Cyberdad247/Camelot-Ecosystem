import inspect
from typing import Dict, Optional
import time

class TestStrategy:
    _UNWANTED_PROPS = {
        "provider": "Use llm_config",
        "api_token": "Use llm_config"
    }

    def __init__(self, provider="default", api_token=None):
        self.provider = provider
        self.api_token = api_token
        self.usages = []

    def __setattr__(self, name, value):
        sig = inspect.signature(self.__init__)
        all_params = sig.parameters
        if name in self._UNWANTED_PROPS and value is not all_params[name].default:
            raise AttributeError("deprecated")
        super().__setattr__(name, value)

t = TestStrategy()
start = time.time()
for i in range(10000):
    t.usages = []
print("Time taken:", time.time() - start)
