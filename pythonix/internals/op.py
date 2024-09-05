"""Functions used to operate over data structures.

Comparable to the filter, map, reduce, getitem, getattr, setitem, and setattr functions.
Can be used easily with the Piper, and PipeApplyInfix, a.k.a P. All functions are as
error proof as possible.

Examples:

    Mapping and Filtering: ::

        >>> from operator import add
        >>> data = [1, 2, 3, 4]
        >>> is_even = lambda x: x % 2 == 0
        >>> add_one = lambda x : x + 1
        >>> mapped = map_over(add_one)(data)
        >>> where_even = where(is_even)(mapped)
        >>> total = fold(add)(where_even)
        >>> total
        6

    Getting from Data Structures: ::

        >>> data = [1, 2, 3]
        >>> val, err = item(2)(data).u
        >>> val
        3
    
"""
from typing import (
    Callable,
    Iterable,
    cast,
    Iterator,
    TypeVar,
    Mapping,
    Sequence,
    ParamSpec,
)
from functools import reduce
from pythonix.internals.res import null_and_error_safe, Res, Nil
from pythonix.internals.curry import two, three


P = ParamSpec("P")
T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")
O = TypeVar("O", bound="object")
K = TypeVar("K")


@two
def where(using: Callable[[T], bool], iterable: Iterable[T]) -> Iterator[T]:
    """Filter over an `Iterable` with a function.

    Function takes each of its elements and returns a True or False.
    True evaluations are kept while False are not kept in the result.

    Note:
        Returns a lazy iterator that must be collected.

    Args:
        *using* ((T) -> bool): Function that takes a value *T* and returns True or False
        iterable (Iterable[T]): List, tuple, or other iterable

    Returns:
        *iterator* (Iterator[T]): Lazy iterator of the same type as the iterable, but with
        only the elements that evaluated to True

    Example: ::

        >>> data: list[str] = [1, 2, 3, 4]
        >>> is_even = lambda x: x % 2 == 0
        >>> list(where(is_even)(data))
        [2, 4]

    """
    return filter(using, iterable)


@two
def map_over(using: Callable[[T], U], iterable: Iterable[T]) -> Iterable[U]:
    """Run a function over an `Iterable`, return an Iterator of the results

    Note:
        Returns a lazy iterator that must be collected.

    Args:
        *using* ((T) -> U): Function that will be applied over each element of the Iterable
        *iterable* (Iterable[T]): List, tuple, or other iterable.

    Returns:
        *iterator* (Iterator[U]): Lazy iterator containing the result of *using* over the *iterable*

    Example: ::

        >>> data = [1, 2, 3, 4]
        >>> add_one = lambda x : x + 1
        >>> list(map_over(add_one)(data))
        [2, 3, 4, 5]

    """
    return map(using, iterable)


@two
def fold(using: Callable[[T, T], T], iterable: Iterable[T]) -> T:
    """Accumulating pairs of elements to a final value recursively

    Args:
        *using* ((T, S) -> U): Function that takes two arguments and returns a single element of the same type
        *iterable* (Iterable[T | S]): List, tuple, or other sequence of the same type

    Returns:
        *output* (U): Accumulated final value

    Example: ::

        >>> data = [1, 2, 3, 4]
        >>> add = lambda x, y: x + y
        >>> fold(add)(data)
        10

    """
    return reduce(using, iterable)


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


def call(op: Callable[[], U]) -> U:
    return op()
