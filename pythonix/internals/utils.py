"""Useful functions for collections, classes, etc."""
from typing import (
    Callable,
    cast,
    TypeVar,
    Mapping,
    Sequence,
    ParamSpec,
)
from pythonix.internals.res import null_and_error_safe, Res, Nil
from pythonix.internals.traits import Unwrap, UnwrapAlt
from pythonix.internals.curry import two, three


P = ParamSpec("P")
T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")
V = TypeVar("V")
O = TypeVar("O", bound="object")
K = TypeVar("K")


@three
def attr(attr_type: type[U], name: str, obj: object) -> Res[U, Nil]:
    """Used to safely retrieve attributes from classes in a functional way.

    Args:
        name (str): The name of the attribute to retrieve
        expected_type (type[U]): The expected return type of the attribute
        obj (T): Any object

    Returns:
        opt (Res[U, Nil]): Result type containing the desired value if Ok, or
        Nil if Err

    Example: ::

        >>> from collections import namedtuple
        >>> Point = namedtuple('Point', ('x', 'y'))
        >>> P = Point(10, 10)
        >>> val, nil = attr(int)('x')(P).u
        >>> val
        10

    """
    try:
        return Res.Some(getattr(obj, name))
    except AttributeError as e:
        return Res.Nil(str(e))


@two
@null_and_error_safe(IndexError, KeyError, TypeError)
def item(index: K, iterable: Mapping[K, T] | Sequence[T]) -> T | None:
    """Safely retrieve items from data structures

    Note:
        The second arguments are overloaded. Different data types will result in different
        return types.

    Args:
        *index* (SupportsIndex | K): Any value that can be used for indexing or hashing for mappings or sequences
        *iterable* (Mapping[K, T], Variant): A key value mapping
        *iterable* (Sequence[T], Variant): A sequence with values
        *iterable* (Iterable[T], Variant): An iterable that does not inherit from Mapping or Sequence

    Returns:
        *opt* (Res[U, Nil]): Result type containing either the expected value if Ok, or a Nil if Err

    Example: ::

        >>> data = {'hello': [1, 2, 3]}
        >>> row, nil = item('hello')(data).u
        >>> row
        [1, 2, 3]
        >>> elem, nil = item(0)(row).u
        >>> elem
        1

    """
    if isinstance(iterable, Sequence):
        match index:
            case int() | slice():
                return cast(T, iterable[index])
            case _:
                raise TypeError("Index for sequence invalid. Needs int or slice")
    elif isinstance(iterable, Mapping):
        return iterable.get(index)
    else:
        raise TypeError("Invalid iterable. Must be a subclass of Mapping or Sequence")


@two
def arg(val: T, op: Callable[[T], U]) -> U:
    """Applies a single argument to a function and returns its result.

    Useful for piping an argument into a function.

    Args:
        *val* (T): The value to be applied to the single variable function
        *op* ((T) -> U): The function that will apply T and output U

    Returns:
        *output* (U): The output of the provided function

    Example: ::

        >>> add_ten = lambda x: x + 10
        >>> arg(10)(add_ten)
        20

    """

    return op(val)

def do(using: Callable[[U], V]):
    """Runs provided function but returns the input value.

    Args:
        using ((T) -> U): Func that takes following value and returns something

    Returns:
        ((T) -> T): Function that runs using and returns its input

    #### Examples ::

        >>> ok = Res.Some(10)
        >>> ok >>= do(print)
        >>> ok <<= unwrap
        10
    """

    def inner(val: T) -> T:
        using(cast(U, val))
        return val

    return inner

def unwrap(subj: Unwrap[T]) -> T:
    """Calls an objects `unwrap` method, with any side effects that were added

    Args:
        subj (Unwrap[T]): Any object that inherits and implements the `Unwrap` abstract class

    Returns:
        T: The wrapped value assigned to `Unwrap`
    """
    return subj.unwrap()


def unwrap_alt(subj: UnwrapAlt[T]) -> T:
    """Calls an objects `unwrap` method, with any side effects that were added

    Args:
        subj (UnwrapAlt[T]): Any object that inherits and implements the `Unwrap` abstract class

    Returns:
        T: The wrapped value assigned to `UnwrapAlt`
    """
    return subj.unwrap_alt()