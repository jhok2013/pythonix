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
from __future__ import annotations
from typing import TypeVar, Callable, Generic
from pythonix.internals.curry import two

S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound="Exception")


class PipeSuffix(Generic[T, U], object):
    """Class decorator used to create custom behavior that uses the `|` symbol.

    Wrap functions whose parameters you want to receive from the left of a `|` in the class.
    You can still call the function normally. Type information is not preserved for nested classes like
    `Ok`, `Err`, `Bind`, or `Do`

    Examples:
        ```python
        @PipeSuffix
        def add_one(x: int) -> int:
            return x + 1

        assert 1 | add_one == 2
        assert add_one(1) == 2
        ```
    """

    op: Callable[[T], U]

    def __init__(self, op: Callable[[T], U]) -> None:
        self.op = op

    def __ror__(self, left: T) -> U:
        return self.op(left)

    def __call__(self, left: T) -> U:
        return self.op(left)


class PipePrefix(Generic[T, U], object):
    """
    Class decorator used to create custom behavior that uses the `|` symbol.
    Wrap functions whose parameters you want to receive from the right of a `|` in the class.
    You can still call the function normally.
    ```python
    @PipePrefix
    def add_one(x: int) -> int:
        return x + 1

    assert add_one | 1 == 2
    assert add_one(1) == 2
    ```
    """

    op: Callable[[T], U]

    def __init__(self, op: Callable[[T], U]) -> None:
        self.op = op

    def __or__(self, right: T) -> U:
        return self.op(right)

    def __call__(self, right: T) -> U:
        return self.op(right)


class PipeInfix(Generic[T, S, U], object):
    """
    Class decorator used to create custom behavior that uses the `|` symbol.
    Wrap functions whose parameters you want to receive from the left and right of a `|` in the class.
    You can still call the function normally
    ```python
    @PipeInfix
    def add(x: int, y: int) -> int:
        return x + y

    assert 1 | add | 1 == 2
    assert add(1, 1) == 2
    ```
    """

    op: Callable[[T], Callable[[S], U]]

    def __init__(self, op: Callable[[T, S], U]) -> None:
        self.op = two(op)

    def __ror__(self, left: T) -> PipePrefix[S, U]:
        return PipePrefix(self.op(left))

    def __call__(self, left: T, right: S) -> U:
        return self.op(left)(right)


class PipeApply(Generic[T], object):
    """
    Special infix operator that takes a value from the left and a function from the right. It calls
    the right function with the value from the left, which allows you to chain function calls together.
    Note though, that this can lose type hint support when using complex objects with nested types like
    the `res` functions.
    ### Example
    ```python
    p = PipeApply()
    add_three = lambda x: x + 3
    x: int = 0 |p| add_three |p| add_three
    y: int = p(x, add_three)
    assert y == 9
    ```
    """

    inner: T

    def __init__(self, inner: T) -> None:
        self.inner = inner

    def __ror__(self, inner: U) -> PipeApply[U]:
        return PipeApply(inner)

    def __or__(self, op: Callable[[T], U]) -> U:
        return op(self.inner)

    def __call__(self, op: Callable[[T], U]) -> U:
        return op(self.inner)


P: PipeApply[None] = PipeApply(None)
'''Special infix operator that pushes the value from the left into the right

Example:
    ```python
    foo = 'foo' |P| bytes |P| str
    ```
'''
