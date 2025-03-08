import pytest


@pytest.fixture
def simple_callable():
    """
    Return a simple callable function for testing.
    """
    def func(x, y=1):
        return x + y
    return func


@pytest.fixture
def callable_class():
    """
    Return a callable class for testing.
    """
    class CallableClass:
        def __call__(self, x, factor=2):
            return x * factor
    return CallableClass()