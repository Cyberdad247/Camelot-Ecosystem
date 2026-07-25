import inspect

class TestGetInitParams:
    _UNWANTED_PROPS = {"provider": "deprecated"}

    # Simulate how it sets all properties dynamically based on __init__ signature
    def __init__(self, provider="default", api_token=None, other=123, **kwargs):
        # The goal is to replace explicit property setting:
        # self.provider = provider
        # self.api_token = api_token
        # self.other = other
        # with dynamic setting based on locals().

        # In __setattr__, there's a TODO:
        # "TODO: Planning to set properties dynamically based on the __init__ signature"

        # If the TODO is in __init__, we could use locals().
        # But wait, the TODO is in __setattr__ (or __init__?)
        # Let's check where the TODO is actually placed.
        pass
