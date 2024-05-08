from __future__ import annotations
from typing import Callable, Protocol, Tuple, overload, TypeVar, Generic
from pythonix.internals import trail
from pythonix.internals.trail import Trail, Log

Val = TypeVar('Val')
NewVal = TypeVar('NewVal')


class HasInner(Generic[Val], Protocol):

    inner: Val


class Bind(Generic[Val]):
    """
    Container that allows sequential functions calls to change its inner value and type.
    Transformations can be done with with either the `run` or `__call__` methods.
    #### Example
    ```python
    y: bool = (
        Bind(5)
        (lambda x: x + 6)   # -> 5 + 6 = 11
        (lambda x: x == 11) # -> 11 == 11 == True
    )
    assert y == True
    ```
    #### Methods
    - `run(Fn(T) -> U) -> Bind<U>`: Runs the provided function and returns a new `Bind` object containing
    its result
    - `__call__(Fn(T) -> U) -> Bind<U>`: Identical to the `run` function.
    """

    inner: Val

    def __init__(self, inner: Val) -> None:
        self.inner = inner

    def run(self, using: Callable[[Val], NewVal]) -> Bind[NewVal]:
        """
        Performs a transformation on the contained value using the function provided.
        Returns a new `Bind` object containing the new value. Works only with single arity
        functions.
        """
        return Bind(using(self.inner))

    def __call__(self, using: Callable[[Val], NewVal]) -> Bind[NewVal]:
        """
        Performs a transformation on the contained value using the function provided.
        Returns a new `Bind` object containing the new value. Works only with single arity
        functions.
        """
        return Bind(using(self.inner))


class Do(Generic[Val]):
    """
    Container used to run arbitrary functions on an `inner` value without changing its
    state. Useful for logging, printing, or other inconsequential side effects.
    #### Example
    ```python
    do: Do[int] = Do(5)
    (
        do
        (print)             # Prints 5
        (lambda x: x * 2)   # -> 10
        (lambda x: x - 3)   # -> 2
    )
    assert do.inner == 5
    ```
    #### Methods
    - `run(Fn(T) -> U) -> Do[T]`: Runs the provided function on the contained value and returns itself.
    - `__call__(Fn(T) -> U) -> Do[T]`: Identical to the `run` function.
    """

    inner: Val

    def __init__(self, inner: Val) -> None:
        self.inner = inner

    def run(self, using: Callable[[Val], NewVal]) -> Do[Val]:
        """
        Performs the provided function on the `inner` value, but does not return its result.
        Returns itself instead.
        """
        using(self.inner)
        return self

    def __call__(self, using: Callable[[Val], NewVal]) -> Do[Val]:
        """
        Performs the provided function on the `inner` value, but does not return its result.
        Returns itself instead.
        """
        return self.run(using)


class Blaze(Generic[Val]):
    """
    `Bind` container used to accumulate log messages during runtime without
    side effects to the functions being ran. Runs functions with an optional
    log message attached. If the function being called returns a `Trail` log container,
    then it will attach its logs to the currently accumulated logs.
    """

    logs: Tuple[Log, ...] = tuple()
    inner: trail.Trail[Val]

    def __init__(self, inner: Val | Trail[Val], *logs: Log):
        match inner:
            case Trail():
                self.inner = inner
                self.logs = logs + inner.logs
            case _:
                self.inner = trail.new()(inner)
                self.logs = logs

    @overload
    def __call__(self, using: Callable[[Val], trail.Trail[NewVal]], *logs: Log) -> Blaze[NewVal]: ...

    @overload
    def __call__(self, using: Callable[[Val], NewVal], *logs: Log) -> Blaze[NewVal]: ...

    def __call__(self, using: Callable[[Val], trail.Trail[NewVal] | NewVal], *logs: Log) -> Blaze[NewVal]:
        """
        Call the function and attach the logs from the function `Trail` and the optional logs
        to the new instance of `Blaze` containing the result.
        """
        return Blaze(using(self.inner.inner), *(self.logs + logs))
