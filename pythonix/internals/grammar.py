from __future__ import annotations
from typing import TypeVar, Callable, Generic
from pythonix.internals.curry import two

Val = TypeVar("Val")
Val2 = TypeVar("Val2")
RetVal = TypeVar("RetVal")
ErrVal = TypeVar("ErrVal", bound="Exception")


class PipeSuffix(Generic[Val, RetVal], object):
    """
    Class decorator used to create custom behavior that uses the `|` symbol.
    Wrap functions whose parameters you want to receive from the left of a `|` in the class.
    You can still call the function normally. Type information is not preserved for nested classes like
    `Ok`, `Err`, `Bind`, or `Do`
    ```python
    @PipeSuffix
    def add_one(x: int) -> int:
        return x + 1

    assert 1 | add_one == 2
    assert add_one(1) == 2
    ```
    """

    _op: Callable[[Val], RetVal]

    def __init__(self, op: Callable[[Val], RetVal]) -> None:
        self._op = op

    def __ror__(self, left: Val) -> RetVal:
        return self._op(left)

    def __call__(self, left: Val) -> RetVal:
        return self._op(left)


class PipePrefix(Generic[Val, RetVal], object):
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

    _op: Callable[[Val], RetVal]

    def __init__(self, op: Callable[[Val], RetVal]) -> None:
        self._op = op

    def __or__(self, right: Val) -> RetVal:
        return self._op(right)

    def __call__(self, right: Val) -> RetVal:
        return self._op(right)


class PipeInfix(Generic[Val, Val2, RetVal], object):
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

    _op: Callable[[Val], Callable[[Val2], RetVal]]

    def __init__(self, op: Callable[[Val, Val2], RetVal]) -> None:
        self._op = two(op)

    def __ror__(self, left: Val) -> PipePrefix[Val2, RetVal]:
        return PipePrefix(self._op(left))

    def __call__(self, left: Val, right: Val2) -> RetVal:
        return self._op(left)(right)


class PipeApply(Generic[Val], object):
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

    inner: Val

    def __init__(self, inner: Val) -> None:
        self.inner = inner

    def __ror__(self, inner: RetVal) -> PipeApply[RetVal]:
        return PipeApply(inner)

    def __or__(self, op: Callable[[Val], RetVal]) -> RetVal:
        return op(self.inner)

    def __call__(self, op: Callable[[Val], RetVal]) -> RetVal:
        return op(self.inner)


Pipe: PipeApply[None] = PipeApply(None)
