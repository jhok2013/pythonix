"""Key value pair utility functions to make using pairs easier.

Includes methods for creating pairs, setting and gettings keys and values, and mapping over a value.

Example:
    ```python
    from pythonix.prelude import *

    (
        B(pair.new('foo')(None))
        (pair.set_key('bar'))
        (pair.set_value(5))
        (pair.map(lambda x: x + 5))
        .do
        (pair.get_value |P| prove.equals(10) |P| res.unwrap)
        (pair.get_key |P| prove.equals('bar') |P| res.unwrap)
        (prove.equals(('bar', 10)) |P| res.unwrap)
    )
    ```
"""
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
