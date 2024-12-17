"""Class and function decorators for operator syntax like `|`, `>>`, etc. Includes basic `Piper` that implements that behavior."""
from __future__ import annotations
from typing import TypeVar, Callable, Generic, ParamSpec
from dataclasses import dataclass
from pythonix.internals.curry import two
from pythonix.internals.traits import Unwrap, Ad

P = ParamSpec("P")
S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class PipeSuffix(Generic[T, U], object):
    """Class decorator for custom operators using a left |

    Wrap functions whose parameters you want to receive from the left of a `|` in the class.
    You can still call the function normally.

    Args:
        *op* ((T) -> U): Func that takes inner and returns a result

    Examples: ::

        >>> @PipeSuffix
        ... def add_ten(x: int) -> int:
        ...     return x + 10
        ...
        >>> 10 | add_ten
        20
        >>> add_ten(10)
        20

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
        ... def add_ten(x: int) -> int:
        ...     return x + 10
        ...
        >>> add_ten(10)
        20
        >>> add_ten | 10
        20

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

        >>> from functools import reduce
        >>> @PipeInfix
        ... def fold(func, iterable):
        ...     return reduce(func, iterable)
        ...
        >>> add = lambda x, y: x + y
        >>> add | fold | [1, 2, 3, 4]
        10
        >>> fold(add, [1, 2, 3, 4])
        10

    """

    op: Callable[[T], Callable[[S], U]]

    def __init__(self, op: Callable[[T, S], U]) -> None:
        self.op = two(op)

    def __ror__(self, left: T) -> PipePrefix[S, U]:
        return PipePrefix(self.op(left))

    def __call__(self, left: T, right: S) -> U:
        return self.op(left)(right)


class ShiftApplyPrefix(Generic[T], object):
    """Allows the loading of a function using a right shift `>>`

    Args:
        inner (T): The wrapped value used in the function received by `apply` or `>>`

    ## Examples ::

        >>> x: ShiftApplySuffix[int] = ShiftApplySuffix(10)
        >>> x >> str
        '10'
        >>> x >> float
        10.0

    """

    inner: T
    """The wrapped value used in the function received by `apply` or `>>`"""

    def __init__(self, inner: T) -> None:
        self.inner = inner

    def apply(self, op: Callable[[T], U]) -> U:
        """Returns the output of the function with inner as its argument

        Args:
            op (Callable[[T], U]): Function to be ran with inner as its argument

        Returns:
            U: The return value of the provided function
        """
        return op(self.inner)

    def __rshift__(self, op: Callable[[T], U]) -> U:
        """Returns the output of the function with inner as its argument

        Args:
            op (Callable[[T], U]): Function to be ran with inner as its argument

        Returns:
            U: The return value of the provided function
        """
        return self.apply(op)


class ShiftApplySuffix(Generic[T], object):
    """Allows the loading of a function using a left shift `>>`

    Args:
        inner (T): The wrapped value used in the function used by `apply` or `>>`

    ## Examples ::

        >>> x: ShiftApplyPrefix[int] = ShiftApplyPrefix(10)
        >>> str >> x
        '10'

    """

    inner: T
    """The wrapped value used in the function received by `apply` or `>>`"""

    def __init__(self, inner: T) -> None:
        self.inner = inner

    def apply(self, op: Callable[[T], U]) -> U:
        """Returns the output of the function with inner as its argument

        Args:
            op (Callable[[T], U]): Function to be ran with inner as its argument

        Returns:
            U: The return value of the provided function
        """
        return op(self.inner)

    def __rrshift__(self, op: Callable[[T], U]) -> U:
        """Returns the output of the function with inner as its argument

        Args:
            op (Callable[[T], U]): Function to be ran with inner as its argument

        Returns:
            U: The return value of the provided function
        """
        return self.apply(op)


class ShiftApplyInfix(object):
    """Used as an operator to pass arguments to functions

    ## Examples ::

        >>> x = ShiftApplyInfix()
        >>> 10 <<x>> str
        '10'

    """

    def __init__(self): ...

    def __rlshift__(self, other: T) -> ShiftApplyPrefix[T]:
        return ShiftApplyPrefix(other)


x: ShiftApplyInfix = ShiftApplyInfix()
"""Infix operator to pass arguments to functions using `<<` and `>>`

## Examples ::

    >>> '10' <<x>> int <<x>> float <<x>> str
    '10'

"""


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

    def __init__(self) -> None: ...

    def __ror__(self, inner: U) -> PipeApplyPrefix[U]:
        return PipeApplyPrefix(inner)


p: PipeApplyInfix = PipeApplyInfix()
"""Infix operator for pushing the left value into the right side function

Note:
    This operator can sometimes lose type information for complex types with
    Generics.

Examples: ::

    >>> foo: str = 5 |P| lambda x: x + 10 |P| str
    >>> foo == '15'
    True

"""


@dataclass(frozen=True, eq=True, init=True, order=True, match_args=True, repr=True)
class Piper(Ad[T], Unwrap[T]):
    """Wrapper enabling transformations of a value with `map` and `apply`. map uses `>>` `>>=` and apply `<<` and `<<=`

    #### Examples ::

        >>> p = Piper(10)
        >>> p >>= str
        >>> p >>= str.split
        >>> p >>= len
        >>> p <<= lambda l: f"Length is {l}"
        >>> p
        'Length is 2'

    """

    inner: T
    """The wrapped value"""

    def unwrap(self) -> T:
        """Returns the wrapped value

        Returns:
            T: The wrapped value
        """
        return self.inner

    def __irshift__(self, using: Callable[[T], U]) -> Piper[U]:
        return self.map(using)

    def __rshift__(self, using: Callable[[T], U]) -> Piper[U]:
        return self.map(using)

    def map(self, using: Callable[[T], U]) -> Piper[U]:
        """Transforms wrapped value with func, returning new Piper instance. Uses `>>` and `>>=`.

        Args:
            using ((T) -> U): Function that takes inner value and returns a value

        Returns:
            Piper[U]: New Piper instance with output
        """
        return Piper(using(self.inner))


class AndApplyPrefix(Generic[T], object):

    inner: T

    def __init__(self, inner: T) -> None:
        self.inner = inner

    def __and__(self, other: Callable[[T], U]) -> U:
        return other(self.inner)


class PipeFn(Generic[P, U]):
    """Function decorator enabling adding arguments via the left `|` operator"""

    op: Callable[P, U]

    def __init__(self, op: Callable[P, U]) -> None:
        self.op = op

    def __ror__(self, *args: P.args, **kwargs: P.kwargs) -> U:
        return self.op(*args, **kwargs)

    def __ior__(self, *args: P.args, **kwargs: P.kwargs) -> U:
        return self.op(*args, **kwargs)
    
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> U:
        return self.op(*args, **kwargs)


class FnPipe(Generic[P, U]):
    """Function decorator enabling adding arguments via the right `|` operator"""

    op: Callable[P, U]

    def __init__(self, op: Callable[P, U]) -> None:
        self.op = op

    def __or__(self, *args: P.args, **kwargs: P.kwargs) -> U:
        return self.op(*args, **kwargs)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> U:
        return self.op(*args, **kwargs)


class InfixPipe(Generic[T, U, V]):

    op: Callable[[T, U], V]
    left: T

    def __init__(self, op: Callable[[T, U], V]) -> None:
        self.op = op

    def __ror__(self, left: T) -> InfixPipe[T, U, V]:
        self.left = left
        return self

    def __or__(self, right: U) -> V:
        return self.op(self.left, right)

    def __call__(self, left: T, right: U) -> V:
        return self.op(left, right)
