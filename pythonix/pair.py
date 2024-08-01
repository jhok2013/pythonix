"""Key value pair utility functions to make using pairs easier.

Includes methods for creating pairs, setting and gettings keys and values,
and mapping over a value.

Example: ::

    >>> pair = new('foo')(None)
    >>> pair = key('bar')(pair)
    >>> pair = value(5)(pair)
    >>> pair = map_value(lambda x: x + 5)(pair)
    >>> value(pair)
    10
    >>> key(pair)
    'bar'
    >>> key, val = unpack(pair)
    >>> (key, val)
    ('bar', 10)

"""
from pythonix.internals.pair import (
    Pair,
    Pairs,
    new,
    key,
    value,
    map_value,
    unpack
)
