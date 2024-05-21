"""Functions used to operate over data structures.

Comparable to the filter, map, reduce, getitem, getattr, setitem, and setattr functions.
Can be used easily with the Piper, and PipeApplyInfix, a.k.a P. All functions are as
error proof as possible.

Examples:

    Mapping and Filtering: ::

        >>> from operator import add
        >>> data = [1, 2, 3, 4]
        >>> is_even = lambda x: x % 2 == 0
        >>> add_one = lambda x : x + 1
        >>> mapped = map_over(add_one)(data)
        >>> where_even = where(is_even)(mapped)
        >>> total = fold(add)(where_even)
        >>> total
        6

    Getting and Assigning: ::

        >>> data = [1, 2, 0]
        >>> data, err = assign(2)(3)(data)
        >>> val, err = item(2)(data)
        >>> val
        3
    
"""
from pythonix.internals.op import where, map_over, fold, attr, item, arg, assign
