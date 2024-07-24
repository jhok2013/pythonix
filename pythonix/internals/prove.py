"""Basic curried functions for assertions and comparisons

This module provides ways to perform common assertion patterns like
equals, type tests, and testing for the presence of elements in data.

Examples: ::

    >>> val: int = 10
    >>> is_even = lambda x: x % 2 == 0
    >>> _, err = unpack(that(is_even)(val))
    >>> err is None
    True

"""
from typing import Iterable, TypeVar, Callable
from pythonix.internals.curry import two
from pythonix.internals.res import safe, unpack

T = TypeVar("T")
U = TypeVar("U")


@two
@safe(AssertionError)
def that(predicate: Callable[[T], bool], val: T) -> T:
    """Assert that the provided function is true if given the value.

    Note:
        This is useful with a `Do` pipe to check that values match what
        you expect without changing the original value.

    Example: ::

        >>> val: int = 10
        >>> is_even = lambda x: x % 2 == 0
        >>> _, err = unpack(that(is_even)(val))
        >>> err is None
        True

    """
    assert predicate(val) == True
    return val


@two
@safe(AssertionError)
def equals(left: U, right: T) -> T:
    """Assert that two values are equal.

    Example: ::

        >>> expected: int = 10
        >>> actual: int = 10
        >>> _, err = unpack(equals(expected)(actual))
        >>> err is None
        True

    """
    assert left == right
    return right


@safe(AssertionError)
def is_true(val: bool) -> bool:
    """Assert that the provided value is `True`

    Example: ::

        >>> true_value: bool = True
        >>> _, err = unpack(is_true(true_value))
        >>> err is None
        True

    """
    assert val == True
    return val


@two
@safe(AssertionError)
def is_an(expected: type[T], actual: T) -> T:
    """Assert that the value is an instance of the expected type

    Example: ::

        >>> x: int = 10
        >>> _, err = unpack(is_an(int)(x))
        >>> err is None
        True

    """
    assert isinstance(actual, expected)
    return actual


@two
@safe(AssertionError)
def contains(find: T, iterable: Iterable[T]) -> Iterable[T]:
    """Assert that the value is in the provided iterable

    Example: ::

        >>> data = [1, 2, 3]
        >>> _, err = unpack(contains(1)(data))
        >>> err is None
        True

    """
    assert find in iterable
    return iterable
