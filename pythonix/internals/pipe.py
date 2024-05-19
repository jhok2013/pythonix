"""Essential classes for chaining function calls over values in a concise way

The module contains classes for repeatedly binding, piping, or doing things to values
sequentially and concisely.

For when you want to chain function calls that change the internal state, use Bind.
For when you want to test side effects without changing the internal state, use Do.

Examples:

    Normal Flow:
        ```python
        import logging

        foo_list: list[int] = [0, 1, 3, 4]
        first: int = foo_list[0] 
        
        assert first == 0
            
        ```
    
    With Bind and Do:
        ```python
        import logging
        from pythonix.prelude import *

        (
            Bind([0, 1, 3, 4])
            (lambda d: d[0])
            (prove.equals(10))
            (res.unwrap)
        )
        ```
"""
from __future__ import annotations
from typing import Callable, TypeVar, Generic, NamedTuple

T = TypeVar("T")
U = TypeVar("U")


class Bind(Generic[T], NamedTuple):
    """Immutable container that transforms its value sequentially with calls or a run method

    Attributes:
        inner (T): Currently contained value

    Example:
        ```python
        y: bool = (
            Bind(5)
            (lambda x: x + 6)   # -> 5 + 6 = 11
            (lambda x: x == 11) # -> 11 == 11 == True
        )
        assert y == True
        ```
    """

    inner: T
    """The value contained in the Bind"""

    @property
    def do(self) -> Do[T]:
        """Converts the `Bind` pipe to a `Do` pipe

        Returns:
            do (Do[T]): The wrapped value put into a Do pipe
        Example:
            ```python
            x: Do[int] = Bind(10).do
            ```
        """
        return Do(self.inner)

    def run(self, using: Callable[[T], U]) -> Bind[U]:
        """Runs a function over the wrapped value T, returning a new Bind with the result inside

        Note:
            This function can be called by treating the Bind as a function.

        Args:
            using ((T) -> U): Function that takes the inner value and returns a new value

        Returns:
            bind (Bind[U]): A new Bind with the value returned from `using`

        Example:

            Simple:
                ```python
                from pythonix.prelude import *

                assert Bind(10).run(lambda x: x + 10).inner == 20
                ```

            Advanced:
                ```python
                from pythonix.prelude import *

                (
                    Bind(10)
                    .run(lambda x: x + 10)
                    .run(prove.equals(20))
                    .run(res.unwrap)
                    .run(print)
                )
                ```
        """
        return Bind(using(self.inner))

    def __call__(self, using: Callable[[T], U]) -> Bind[U]:
        """Runs a function over the wrapped value T, returning a new Bind with the result inside

        Args:
            using ((T) -> U): Function that takes the inner value and returns a new value

        Returns:
            bind (Bind[U]): A new Bind with the value returned from `using`

        Example:

            Simple:
                ```python
                from pythonix.prelude import *

                b: Bind[int] = Bind(10)
                assert b(lambda x: x + 10).inner == 20
                ```

            Advanced:
                ```python
                from pythonix.prelude import *

                (
                    Bind(10)
                    (lambda x: x + 10)
                    (prove.equals(20))
                    (res.unwrap)
                    (print)
                )
                ```

        """
        return self.run(using)


class Do(Generic[T], NamedTuple):
    """Immutable container that runs functions over its value, but does not change its state

    Note:
        Useful for logging, printing, assertions, or mutable datatypes like list or deque

    Attributes:
        inner (T): The wrapped container

    Example:
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
    """

    inner: T
    """The value contained in the Do"""

    def run(self, using: Callable[[T], U]) -> Do[T]:
        """Runs the function on the value, but does not return its result.

        Arg:
            using ((T) -> U): Function that takes a value and returns a result

        Returns:
            do (Do[T]): A Do container with the same value as before

        Example:

            Simple:
                ```python
                from pythonix.prelude import *

                assert Do(10).run(False).inner == 10
                ```

            Advanced:
                ```python
                from pythonix.prelude import *

                (
                    Do(10)
                    .run(info)
                    .run(print)
                    .run(prove.equals(10) |P| q)
                    .inner
                )
                ```
        """
        using(self.inner)
        return self

    @property
    def bind(self) -> Bind[T]:
        """Converts the `Do` pipe to a `Bind` pipe.

        Note:
            You can use this to switch context between Do and Bind

        Returns:
            bind (Bind[T]): Bind pipe with the same wrapped value

        Example:
            ```python
            from pythonix.prelude import *

            bind: Bind[int] = Do(10).bind
            assert bind.inner == 10
            ```
        """
        return Bind(self.inner)

    def __call__(self, using: Callable[[T], U]) -> Do[T]:
        """Runs the function on the value, but does not return its result.

        Arg:
            using ((T) -> U): Function that takes a value and returns a result

        Returns:
            do (Do[T]): A Do container with the same value as before

        Example:

            Simple:
                ```python
                from pythonix.prelude import *

                assert Do(10)(False).inner == 10
                ```

            Advanced:
                ```python
                from pythonix.prelude import *

                (
                    Do(10)
                    (info)
                    (print)
                    (prove.equals(10) |P| q)
                    .inner
                )
                ```
        """
        return self.run(using)
