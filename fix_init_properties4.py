import inspect

class MyConfig:
    _UNWANTED_PROPS = {"provider": "deprecated"}

    def __init__(self, provider="test", **kwargs):
        pass # To focus on setattr

    def __setattr__(self, name, value):
        if name in self._UNWANTED_PROPS:
            # Check if this property was passed dynamically and differ from default
            sig = inspect.signature(self.__init__)
            all_params = sig.parameters
            if name in all_params:
                if value is not all_params[name].default:
                    raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
            else:
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")

        super().__setattr__(name, value)
