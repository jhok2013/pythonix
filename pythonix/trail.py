"""Wrap operations and values with logs that can be used at runtime.

Includes functions for wrapping values with logs, creating logs,
decorating functions to include logs, and running operations
over values that include or do not include logs.

Example: ::

        >>> add_ten = lambda x: x + 10
        >>> t = new(Info('Initial 10'))(10)
        >>> t = blaze(add_ten, Info('Added another ten'))(t)
        >>> val, logs = unpack(t)
        >>> message, dt = logs[-1]
        >>> message
        'Added another ten'
        >>> val
        20

    You can also use functions that return a Trail, and blaze will handle
    the log concatenation. ::

        >>> add_ten_trailer = on_start(Info('Adding ten with trail'))(add_ten)
        >>> t = blaze(add_ten_trailer)(t)
        >>> val, logs = unpack(t)
        >>> message, dt = logs[-1]
        >>> message
        'Adding ten with trail'
        >>> val
        30

"""
from pythonix.internals.trail import (
    new,
    Trail,
    on_start,
    blaze,
    Log,
    append,
    unpack,
    unwrap,
    Info,
    Critical,
    Debug,
    Error
)
