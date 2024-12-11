"""Simple way to construct type hinted inline functions, like lambdas

The module provides a single function, ``fn``, which allows the user to create
functions inline and assign them to variables with full type hinting support.
This makes it possible to use ``lambda`` functions with type support.

The ``fn`` is overloaded to support from 0 to 9 arguments and 1 output.

Note:
    The last argument in the first ``fn`` call is always the output type

Examples: ::

    >>> add = fn(int, int, int)(lambda x, y: x + y)
    >>> add(10, 10)
    20
    
"""
from typing import TypeVar, Callable, overload, TypeAlias
from functools import wraps

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")
U = TypeVar("U")

Fn: TypeAlias = Callable[[T1], U]
"""Type alias for a function that takes an input and returns an output"""

FnOnce: TypeAlias = Callable[[], U]
"""Type alias for a function that takes no input but returns an output"""

Predicate: TypeAlias = Callable[[T1], bool]
"""Type alias for a function that takes a value and returns True or False"""

@overload
def fn(out: type[U]) -> Fn[FnOnce[U], FnOnce[U]]: ...


@overload
def fn(t1: type[T1], out: type[U]) -> Callable[[Callable[[T1], U]], Callable[[T1], U]]:
    ...


@overload
def fn(
    t1: type[T1], t2: type[T2], out: type[U]
) -> Callable[[Callable[[T1, T2], U]], Callable[[T1, T2], U]]:
    ...


@overload
def fn(
    t1: type[T1], t2: type[T2], t3: type[T3], out: type[U]
) -> Callable[[Callable[[T1, T2, T3], U]], Callable[[T1, T2, T3], U]]:
    ...


@overload
def fn(
    t1: type[T1], t2: type[T2], t3: type[T3], t4: type[T4], out: type[U]
) -> Callable[[Callable[[T1, T2, T3, T4], U]], Callable[[T1, T2, T3, T4], U]]:
    ...


@overload
def fn(
    t1: type[T1], t2: type[T2], t3: type[T3], t4: type[T4], t5: type[T5], out: type[U]
) -> Callable[[Callable[[T1, T2, T3, T4, T5], U]], Callable[[T1, T2, T3, T4, T5], U]]:
    ...


@overload
def fn(
    t1: type[T1],
    t2: type[T2],
    t3: type[T3],
    t4: type[T4],
    t5: type[T5],
    t6: type[T6],
    out: type[U],
) -> Callable[
    [Callable[[T1, T2, T3, T4, T5, T6], U]], Callable[[T1, T2, T3, T4, T5, T6], U]
]:
    ...


@overload
def fn(
    t1: type[T1],
    t2: type[T2],
    t3: type[T3],
    t4: type[T4],
    t5: type[T5],
    t6: type[T6],
    t7: type[T7],
    out: type[U],
) -> Callable[
    [Callable[[T1, T2, T3, T4, T5, T6, T7], U]],
    Callable[[T1, T2, T3, T4, T5, T6, T7], U],
]:
    ...


@overload
def fn(
    t1: type[T1],
    t2: type[T2],
    t3: type[T3],
    t4: type[T4],
    t5: type[T5],
    t6: type[T6],
    t7: type[T7],
    t8: type[T8],
    out: type[U],
) -> Callable[
    [Callable[[T1, T2, T3, T4, T5, T6, T7, T8], U]],
    Callable[[T1, T2, T3, T4, T5, T6, T7, T8], U],
]:
    ...


@overload
def fn(
    t1: type[T1],
    t2: type[T2],
    t3: type[T3],
    t4: type[T4],
    t5: type[T5],
    t6: type[T6],
    t7: type[T7],
    t8: type[T8],
    t9: type[T9],
    out: type[U],
) -> Callable[
    [Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], U]],
    Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], U],
]:
    ...



def fn(*type_args):  # type: ignore
    """Function to create lambdas with type hints. Supports up to 9 arguments.

    The first call allows specification of the types, with the last or the
    arguments always being the output type. The second call is always a
    lambda function or predefined function with an agreeing amount of arguments

    Args:
        *type_args* (type[Any]): A positional list of types to expect, with the
        last one always being the output type

    Examples:

        Simple Composition: ::

            >>> add = fn(int, int, int)(lambda x, y: x + y)
            >>> add(10, 10)
            20

        The example above specified a function whose first two arguments are
        ``int`` and outputs ``int``

        Zero Argument Functions: ::

            >>> ten = fn(int)(lambda: 10)
            >>> ten()
            10

        Functions with zero arguments still need a return type first

    """

    def inner(func):
        """The second call is for passing in a function.

        The arity (number of arguments), input types, and output need
        to agree with the types provided in the first call. However, as of
        now there is no type enforcement. You only risk unexpected behavior
        or unclear expectations.

        Examples:

            Good Example: ::

                >>> add = fn(int, int, int)(lambda x, y: x + y)
                >>> add(10, 10)
                20

            The number of arguments matches the input types in the ``lambda``

            Bad Example: ::

                >>> add = fn(int, int, int)(lambda x: x + 1)
                >>> add(10, 20)
                Traceback (most recent call last):
                  File "<stdin>", line 1, in <module>
                TypeError: <lambda>() takes 1 positional argument but 2 were given

            This example failed because the lambda only takes one argument and
            two were given. The type hints we gave in the first call told
            python to expect two arguments which misled the user.

        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return inner
