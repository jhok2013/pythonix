"""Safely handles tuple sequences with an api like lists

Examples: ::

    >>> data = new(1, 2, 3)
    >>> data = push_right(4)(data)
    >>> data = extend_right(new(5, 6, 7))(data)
    >>> i, nil = index(7)(data)
    >>> i
    6
    >>> count_occurrences(3)(data)
    1
    >>> data, nil = remove(1)(data)
    >>> data
    (1, 3, 4, 5, 6, 7)

"""
from pythonix.internals.tup import (
    count_occurrences,
    extend,
    extend_left,
    extend_right,
    get,
    first,
    index,
    last,
    push,
    push_left,
    push_right,
    insert,
    remove,
    new,
    Side,
)
