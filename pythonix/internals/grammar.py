"""Tools simulating prefix, infix, and suffix applications.

Includes decorator classes for creating new grammar functions, a ``P`` instance
for performing arbitrary piping of values on the left to functions on the right,
and the ``Piper`` class for chaining function binds, applies, and dos on
values sequentially using >>, |, and >.

Examples:

    Piper: ::

        >>> with_operators: str = (
        ...     Piper(5)               # Put value into Piper
        ...     >> (lambda x: x + 10)  # Bind with a function
        ...     | print                # Print without changing state
        ...     > str                  # Return finally thru str
        >>> )
        >>> with_methods: str = (      # Do all the same steps with methods
        ...     Piper(5)
        ...     .bind(lambda x: x + 10)
        ...     .do(print)
        ...     .apply(str)
        >>> )
        >>> with_operators == with_methods
        True

    Pipe:

        ```python
        assert (5, 5) |p| sum == 10
        ```

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
"""
from __future__ import annotations
from typing import TypeVar, Callable, Generic, Self
from pythonix.internals.curry import two

S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound="Exception")


class PipeSuffix(Generic[T, U], object):
    """Class decorator for custom operators using a left |

    Wrap functions whose parameters you want to receive from the left of a `|` in the class.
    You can still call the function normally.

    Args:
        *op* ((T) -> U): Func that takes inner and returns a result

    Examples: ::

        >>> @PipeSuffix
        >>> def add_one(x: int) -> int:
        ...     return x + 1
        ...
        >>> 1 | add_one == 2
        True
        >>> add_one(1) == 2
        True

    """

    op: Callable[[T], U]

    def __init__(self, op: Callable[[T], U]) -> None:
        self.op = op

    def __ror__(self, left: T) -> U:
        return self.op(left)

    def __call__(self, left: T) -> U:
        return self.op(left)


class PipePrefix(Generic[T, U], object):
    """Class decorator for custom operators using a right |

    Wrap functions whose parameters you want to receive from the right of a `|` in the class.
    You can still call the function normally.

    Args:
        *op* ((T) -> U): Func that takes inner and returns a result

    Example: ::

        >>> @PipePrefix
        >>> def add_one(x):
        ...     return x + 1
        ...
        >>> add_one | 1 == 2
        True
        >>> add_one(1) == 2
        True

    """

    op: Callable[[T], U]

    def __init__(self, op: Callable[[T], U]) -> None:
        self.op = op

    def __or__(self, right: T) -> U:
        return self.op(right)

    def __call__(self, right: T) -> U:
        return self.op(right)


class PipeInfix(Generic[T, S, U], object):
    """Class decorator used to define custom piping behavior with the `|` symbols

    Wrap functions whose parameters you want fixly from the left and right. You
    can still call the function normally with parentheses.

    Note:
        The

    Args:
        *op* ((T) -> ((S) -> U)): Curried func of two steps that returns a value

    Examples: ::

        >>> @PipeInfix
        >>> def add(x: int, y: int) -> int:
        ...    return x + y
        ...
        >>> 1 | add | 1 == 2
        True
        >>> add(1, 1) == 2
        True

    """

    op: Callable[[T], Callable[[S], U]]

    def __init__(self, op: Callable[[T, S], U]) -> None:
        self.op = two(op)

    def __ror__(self, left: T) -> PipePrefix[S, U]:
        return PipePrefix(self.op(left))

    def __call__(self, left: T, right: S) -> U:
        return self.op(left)(right)


class PipeApplySuffix(Generic[T], object):
    """Applies function on its left | with inner, returning the result

    Args:
        *inner* (T): Value to be wrapped, is applied to the received function

    Example: ::

        >>> expected: int = 10
        >>> actual: int = (lambda x: x + 5) | PipeApplySuffix(5)
        >>> actual == expected
        True

    """

    inner: T
    """Any value passed during initialization"""

    def __init__(self, inner: T) -> None:
        self.inner = inner

    def __ror__(self, op: Callable[[T], U]) -> U:
        return op(self.inner)


class PipeApplyPrefix(Generic[T], object):
    """Applies the function on its right | to its value, returning the result

    Args:
        *inner* (T): Value to be wrapped, is applied to the received function

    Example: ::

        >>> expected: int = 10
        >>> actual: int = PipeApplyPrefix(5) | (lambda x: x + 5)
        >>> actual == expected
        True

    """

    inner: T
    """Any value passed during initialization"""

    def __init__(self, inner: T) -> None:
        self.inner = inner

    def __or__(self, op: Callable[[T], U]) -> U:
        return op(self.inner)


class PipeApplyInfix(object):
    """Receives a value from the left, and loads it into ``PipeApplyPrefix``

    This is the base for piping values from the left into a function, and allows
    for chaining of arbitrary functions.

    Example: ::

        >>> P: PipeApplyInfix = PipeApplyInfix()
        >>> expected: int = 10
        >>> actual: int = 5 |P| (lambda x: x * 2)
        >>> expected == actual
        True

    """

    def __init__(self) -> None:
        ...

    def __ror__(self, inner: U) -> PipeApplyPrefix[U]:
        return PipeApplyPrefix(inner)


P: PipeApplyInfix = PipeApplyInfix()
"""Infix operator for pushing the left value into the right side function

Note:
    This operator can sometimes lose type information for complex types with
    Generics.

Examples: ::

    >>> foo: str = 5 |P| lambda x: x + 10 |P| str
    >>> foo == '15'
    True

"""


def do(func: Callable[[S], U]) -> Callable[[T], T]:
    """Run the ``func`` with the ``val``, but only return the ``val``

    This function is useful for performing side effects like logging,
    printing, or asserting without changing the value. It is very useful when
    using the `P` operator or the `Piper` monad.

    Args:
        *func* ((S) -> U): Func to be called with value received in next call.

    Returns:
        *output* ((T) -> T): Function that calls *func*, and then returns its
        passed in value

    Examples:

        Using the ``P`` operator ::

            >>> expected: str = '20'
            >>> actual: str = 10 |P| (lambda x: x + 10) |P| do(print) |P| str
            >>> expected == actual
            True

        Passing ``print`` to ``P`` would usually have the next value be ``None``.
        However, since we used ``do``, its original value was preserved.

    """

    def inner(val: T) -> T:
        """Returns the passed value while calling the previous steps *func*"""
        func(val)
        return val

    return inner


def inner(val: T) -> T:
    """Returns its only argument. Useful for Piper >

    Example:

        >>> expected: int = 10
        >>> actual: int = Piper(5) >> (lambda x: x + 5) > inner
        >>> expected == actual
        True

    """
    return val


class Piper(Generic[T], object):
    """Chain functions together with `>>`, `|`, and `>`

    Makes chaining of sequential function calls easy with specialized operators
    for different cases.

    Use `bind` or `>>` to chain function calls, use `do` or `|` to run the func
    but retain the current state, and `apply` or `>` to return the result of
    the func being ran with the contained value.

    Note:
        Calling `do` (`|`) after `bind` (`>>`) can sometimes lose type
        information. Use the `do`function with `bind` (`>>`) to overcome this.

    Examples:

        With Operators: ::

            >>> expected: str = '20'
            >>> actual: str = Piper(10) >> (lambda x: x + 10) >> do(print) > str
            >>> expected == actual
            True

        With Methods: ::

            >>> expected: str = '20'
            >>> actual: str = Piper(10).bind(lambda x: x + 10).do(print).apply(str)
            >>> expected == actual
            True

    FAQ:
        Q: Whats the difference between ``bind`` `>>` and ``apply`` ``>``?
        A: ``>>`` will return another instance of ``Piper`` to continue
        chaining functions. ``>`` will return the result itself, halting method
        chaining.

        Q: What is ``do`` ``|`` and why should I use it?
        A: ``do`` will run the function without changing the internal state.
        This is useful for when you need to log, test, or print values and
        you don't want to break the method chain.

    """

    inner: T
    """The wrapped value that will be used as input for the received  functions"""

    def __init__(self, inner: T):
        self.inner = inner

    def __or__(self, op) -> Piper[T]:
        return self.do(op)

    def __gt__(self, op: Callable[[T], U]) -> U:
        return self.apply(op)

    def __rshift__(self, op: Callable[[T], U]) -> Piper[U]:
        return self.bind(op)

    def bind(self, op: Callable[[T], U]) -> Piper[U]:
        """Run *op* with *inner* returning new *Piper* with result. Same as >>

        Args:
            *op* ((T) -> U): Func that takes inner and returns new value

        Examples:

            With >>: ::

                >>> expected: str = '10'
                >>> actual: str = Piper(5) >> (lambda x: x + 5) > str
                >>> actual == expected
                True

            With method: ::

                >>> expected: str = '10'
                >>> actual: str = Piper(5).bind(lambda x: x + 5).bind(str).inner
                >>> expected == actual
                True

        """
        return Piper(op(self.inner))

    def do(self, op: Callable[[T], U]) -> Self[T]:
        """Run *op* with *inner*, but return original `Piper`. Same as |

        Args:
            *op* ((S) -> U): Func that takes inner and returns a new value

        Examples:

            With |: ::

                >>> expected: int = 10
                >>> actual: int = Piper(10) | (lambda x: x + 10) > (lambda x: x)
                >>> expected == actual
                True

            With do: ::

                >>> expected: int = 10
                >>> actual: int = Piper(10).do(lambda x: x + 10).inner
                >>> expected == actual
                True

        """
        op(self.inner)
        return self

    def apply(self, op: Callable[[T], U]) -> U:
        """Run *op* with *inner*, returning the result. Same as >.

        Args:
            *op* ((T) -> U): Func that takes inner and returns a new value

        Examples:

            With >: ::

                >>> expected: str = '10'
                >>> actual: str = Piper(10) > str
                >>> expected == actual
                True

            With apply: ::

                >>> expected: str = '10'
                >>> actual: str = Piper(10) > str
                >>> expected == actual
                True
        """
        return op(self.inner)
