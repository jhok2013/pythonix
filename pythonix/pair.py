"""Key value pair utility functions to make using pairs easier.

Includes methods for creating pairs, setting and gettings keys and values,
and mapping over a value.

Example: ::

    >>> pair = new('foo')(None)
    >>> pair = set_key('bar')(pair)
    >>> pair = set_value(5)(pair)
    >>> pair = map_value(lambda x: x + 5)(pair)
    >>> get_value(pair)
    10
    >>> get_key(pair)
    'bar'
    >>> key, val = pair
    >>> (key, val)
    ('bar', 10)

"""
from pythonix.internals.pair import (
    Pair,
    Pairs,
    new,
    get_key,
    get_value,
    set_key,
    set_value,
    map_value,
)
