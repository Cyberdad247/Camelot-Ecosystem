import inspect

class MyConfig:
    _UNWANTED_PROPS = {"provider": "deprecated"}

    def __init__(self, a=1, b=2, provider="test", **kwargs):
        pass # Not using the dynamic set here for testing setattr issue

    def __setattr__(self, name, value):
        sig = inspect.signature(self.__init__)
        all_params = sig.parameters

        # Original buggy code:
        # if name in self._UNWANTED_PROPS and value is not all_params[name].default:

        # New safe code:
        if name in self._UNWANTED_PROPS:
            if name in all_params and value is not all_params[name].default:
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
            elif name not in all_params:
                # Still raise if it's an unwanted prop, even if not in init
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")

        super().__setattr__(name, value)

m = MyConfig()
m.c = 20
print(vars(m))
