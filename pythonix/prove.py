'''
Basic assertion functions that work well in a `Bind` or `Do` context.
Use these to verify a value without changing its value.
'''
from pythonix.internals.prove import (
    contains,
    equals,
    is_an,
    is_true,
    that
)