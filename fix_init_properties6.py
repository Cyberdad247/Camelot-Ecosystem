import inspect

class TestClass:
    _UNWANTED_PROPS = {"foo": "bar"}
    def __init__(self, foo=1, **kwargs):
        pass

    def __setattr__(self, name, value):
        if name in self._UNWANTED_PROPS:
            sig = inspect.signature(self.__init__)
            if name in sig.parameters:
                if value is not sig.parameters[name].default:
                    raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
            else:
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
        super().__setattr__(name, value)
