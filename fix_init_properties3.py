import inspect

class MyConfig:
    _UNWANTED_PROPS = {"provider": "deprecated"}

    def __init__(self, provider="test", **kwargs):
        pass # To focus on setattr

    def __setattr__(self, name, value):
        sig = inspect.signature(self.__init__)
        all_params = sig.parameters

        # The buggy line:
        # if name in self._UNWANTED_PROPS and value is not all_params[name].default:

        # When name is in _UNWANTED_PROPS, it checks if it's in all_params.
        # But if we change it to:
        if name in self._UNWANTED_PROPS:
            if name in all_params:
                if value is not all_params[name].default:
                    raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
            else:
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")

        super().__setattr__(name, value)

m = MyConfig()
m.a = 20
try:
    m.provider = "changed"
except AttributeError as e:
    print(e)
