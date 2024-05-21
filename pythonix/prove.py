"""Basic curried functions for assertions and comparisons

This module provides ways to perform common assertion patterns like
equals, type tests, and testing for the presence of elements in data.

Examples: ::

    >>> val: int = 10
    >>> is_even = lambda x: x % 2 == 0
    >>> _, err = that(is_even)(val)
    >>> err is None
    True

"""
from pythonix.internals.prove import contains, equals, is_an, is_true, that
