"""Covers for the ``deque`` methods with type hints. Error, None, and type safe.

Does not return copies of the ``deque``, but instead mutable references
to the ``deq`` it recieves. A useful data structure with thread safe
appends and pops.

Examples: ::

    >>> from pythonix.internals.res import unpack
    >>> deq = new(1, 2, 3)
    >>> val, nil = unpack(get(0)(deq))
    >>> val
    1

"""
from pythonix.internals.deq import (
    new,
    get,
    copy,
    extend,
    extendleft,
    first,
    index,
    insert,
    last,
    pop,
    popleft,
    append,
    appendleft,
    remove,
    reverse,
    rotate,
    maxlen,
    clear,
    count
)
