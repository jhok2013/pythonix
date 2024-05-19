"""Partialized functions for safe and simple assertions

This module provides ways to perform common assertion patterns like
equals, type tests, and testing for the presence of elements in data.

"""
from typing import Iterable, TypeVar, Callable
from pythonix.internals.curry import two
from pythonix.internals.res import safe

Val = TypeVar("Val")
NewVal = TypeVar("NewVal")


@two
@safe(AssertionError)
def that(predicate: Callable[[Val], bool], val: Val) -> None:
    """Assert that the provided function is true if given the value.

    Note:
        This is useful with a `Do` pipe to check that values match what you expect without
    changing the original value.

    Example:
        ```python
        val: int = 10
        is_even = lambda x: x % 2 == 0
        passed_inspection = prove.that(is_even)(val)
        res.unwrap(passed_inspection)

        # Bind shorthand
        Bind(10)(prove.that(is_even))(q)
        ```
    """
    assert predicate(val) == True


@two
@safe(AssertionError)
def equals(left: NewVal, right: Val) -> None:
    """Assert that two values are equal.

    Example:
        ```python
        expected: int = 10
        actual: int = 10
        comparison_result: Res[None, AssertionError] = prove.equals(expected)(actual)
        res.unwrap(comparison_result)
        ```
    """
    assert left == right


@safe(AssertionError)
def is_true(val: bool) -> None:
    """Assert that the provided value is `True`

    Example:
        ```python
        true_value: bool = True
        comparison_result
        ```
    """
    assert val == True


@two
@safe(AssertionError)
def is_an(expected: type[Val], actual: Val) -> None:
    """
    Assert that the value is an instance of the expected type
    """
    assert isinstance(actual, expected)


@two
@safe(AssertionError)
def contains(find: Val, iterable: Iterable[Val]) -> None:
    """
    Assert that the value is in the provided iterable
    """
    assert find in iterable
