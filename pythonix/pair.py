'''
Functions for creating and mutating key value pairs in a safe and immutable way.
Pairs well with the `Bind` wrapper type.
'''
from pythonix.internals.pair import (
    Pair,
    Pairs,
    new,
    get_key,
    get_value,
    set_key,
    set_value,
    map,
)
