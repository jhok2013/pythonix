"""Simple way to construct type hinted inline functions, like lambdas

The module provides a single function, ``fn``, which allows the user to create
functions inline and assign them to variables with full type hinting support.
This makes it possible to use ``lambda`` functions with type support.

The ``fn`` is overloaded to support from 0 to 9 arguments and 1 output.

Note:
    The last argument in the first ``fn`` call is always the output type

Examples: ::

    >>> add = fn(int, int, int)(lambda x, y: x + y)
    >>> add(10, 10)
    20
    
    This makes preserving type info when using pipe applicators much easier

    >>> from pythonix.prelude import *
    >>> 10 |P| fn(int, int)(lambda x: x + 1)
    11
"""
from pythonix.internals.fn import fn, Fn, FnOnce, Predicate
