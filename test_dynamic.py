import inspect

class Test:
    def __init__(self, a=1, b=2, c=3, **kwargs):
        local_vars = locals()
        sig = inspect.signature(self.__init__)
        for name in sig.parameters:
            if name not in ("self", "kwargs") and name in local_vars:
                setattr(self, name, local_vars[name])

t = Test(a=10, b=20, d=40)
print(t.__dict__)
