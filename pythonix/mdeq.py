"""
A mutable singly linked list with O(1) inserts and pops on the left and right ends.
If used with a pipe, use the `Do` pipe since the object is mutable and not copied after
every call with these functions.
"""
from pythonix.internals.mdeq import (
    MDeq,
    new,
    at,
    copy,
    extend,
    extendleft,
    first,
    index,
    insert,
    last,
    pop,
    popleft,
    push,
    pushleft,
    remove,
)
