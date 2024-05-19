"""Decorator classes that used to simulate prefix, infix, and suffix applications.

Includes the special `P` object to pipe values from left to right into functions.

Example:
    Prefix:
    ```python
    @PipePrefix
    def absorb_right[T](val: T) -> T:
        return val

    assert absorb_right | 10 == 10
    assert absorb_right(10) == 10
    ```

    Infix:
    ```python
    @PipeInfix
    def fold[T, U, V](func: Callable[[T, U], V], iterable: Iterable[T | U]) -> V:
        return reduce(func, iterable)

    assert operator.add | fold | [1, 2, 3, 4] == 10
    assert fold(operator.add)([1, 2, 3, 4]) == 10
    ```

    Suffix:
    ```python
    @PipeSuffix
    def inner[T](val: HasInner[T]) -> T:
        return val.inner

    assert Ok(5) | inner == 5
    assert inner(Ok(5)) == 5
    ```

    Pipe:
    ```python
    assert (5, 5) |p| sum == 10
    ```
"""
from pythonix.internals.grammar import (
    PipeSuffix,
    PipeInfix,
    PipePrefix,
    PipeApplyInfix,
    PipeApplyPrefix,
    PipeApplySuffix,
    Piper,
    P,
)
