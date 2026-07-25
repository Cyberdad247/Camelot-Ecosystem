import inspect

class Test:
    def __init__(self, a=1, b=2, c=3, **kwargs):
        # We can also get parameters from kwargs
        # But wait, locals() won't have kwargs unrolled.
        # But the problem is actually about __setattr__ checking defaults.
        pass

    def __setattr__(self, name, value):
        sig = inspect.signature(self.__init__)
        all_params = sig.parameters

        # In current code:
        # if name in self._UNWANTED_PROPS and value is not all_params[name].default:

        # What if name is not in all_params? It raises KeyError.
        pass

t = Test()
t.d = 40
