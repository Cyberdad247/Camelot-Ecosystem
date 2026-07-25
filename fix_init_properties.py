import inspect

# Example class
class MyConfig:
    _UNWANTED_PROPS = {"provider": "deprecated"}

    def __init__(self, a=1, b=2, provider="test", **kwargs):
        # Current pattern sets variables directly:
        self.a = a
        self.b = b
        self.provider = provider

        # New pattern - set dynamically
        sig = inspect.signature(self.__init__)
        local_vars = locals()

        for name in sig.parameters:
            if name not in ("self", "kwargs") and name in local_vars:
                setattr(self, name, local_vars[name])
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, name, value):
        sig = inspect.signature(self.__init__)
        all_params = sig.parameters

        if name in self._UNWANTED_PROPS:
            # We want to check if the value is different from the default parameter value
            # Note: if a dynamically added property isn't in __init__ params, all_params[name] raises KeyError
            if name in all_params and value is not all_params[name].default:
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")

        super().__setattr__(name, value)

m = MyConfig(a=10)
print(vars(m))
try:
    m.provider = "changed"
    print("Should not print")
except AttributeError as e:
    print(e)

m.c = 20 # Does this work?
print(vars(m))
