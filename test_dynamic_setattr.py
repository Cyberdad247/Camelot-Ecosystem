import inspect

class TestInit:
    def __init__(self, a=1, b=2, c=3, **kwargs):
        # Setting kwargs dynamically using inspect
        # Let's say we want to grab all variables passed to __init__
        local_vars = locals().copy()
        sig = inspect.signature(self.__init__)
        for name in sig.parameters:
            if name not in ("self", "kwargs") and name in local_vars:
                setattr(self, name, local_vars[name])
        for k, v in kwargs.items():
            setattr(self, k, v)

t = TestInit(a=10, b=20, extra=100)
print(vars(t))
