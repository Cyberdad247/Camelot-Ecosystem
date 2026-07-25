import inspect

class TestClass:
    _UNWANTED_PROPS = {"foo": "bar"}
    def __init__(self, foo=1, **kwargs):
        pass

    def __setattr__(self, name, value):
        if name in self._UNWANTED_PROPS:
            sig = inspect.signature(self.__init__)
            all_params = sig.parameters
            # Fix: Use dict.get to safely check if it exists in all_params
            if name in all_params and value is not all_params[name].default:
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
            elif name not in all_params:
                raise AttributeError(f"Setting '{name}' is deprecated. {self._UNWANTED_PROPS[name]}")
        super().__setattr__(name, value)

t = TestClass()
t.foo = 1 # OK, it's default
try:
    t.foo = 2
    print("FAILED")
except AttributeError as e:
    print("SUCCESS", e)
