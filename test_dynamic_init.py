import inspect

class TestClass:
    def __init__(self, a=1, b=2, **kwargs):
        # Using inspect.signature to set properties dynamically
        sig = inspect.signature(self.__init__)
        # But we need the actual values passed to __init__!
        # inspect.signature only gives default values.
        # How to get the actual values? We can use locals() or frame.
        pass
