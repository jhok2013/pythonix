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

    Getting and Assigning: ::

        >>> data = [1, 2, 0]
        >>> data, err = assign(2)(3)(data)
        >>> val, err = item(2)(data)
        >>> val
        3
    
"""
from typing import (
    Callable,
    Iterable,
    Iterator,
    Any,
    SupportsIndex,
    TypeVar,
    overload,
    MutableSequence,
    Sequence,
    MutableMapping,
    Mapping,
)
from functools import reduce
from pythonix.internals.res import null_and_error_safe, safe, Res
from pythonix.internals.curry import two
from operator import setitem


T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")
O = TypeVar("O", bound="object")
K = TypeVar("K", str, int, float, tuple, slice)


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
def map_over(using: Callable[[T], U], iterable: Iterable[T]) -> Iterable[T]:
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
def fold(using: Callable[[T, S], U], iterable: Iterable[T | S]) -> U:
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


def attr(name: str, type_hint: type[U] = Any) -> Callable[[T], U]:
    """Used to safely retrieve attributes from classes in a functional way.

    Can be used with a `type_hint` parameter to provide better type hint support.

    Args:
        name (str): The name of the attribute to retrieve
        obj (T): Any object

    Returns:
        opt (Res[U, Nil]): Result type containing the desired value if Ok, or Nil if Err

    Example: ::

        >>> from collections import namedtuple
        >>> Point = namedtuple('Point', ('x', 'y'))
        >>> P = Point(10, 10)
        >>> val, nil = attr('x')(P)
        >>> val
        10
        >>> val, nil = attr('z')(P)
        >>> nil
        Nil("'Point' object has no attribute 'z'")

    """

    @null_and_error_safe(AttributeError)
    def inner(obj: T) -> U:
        return getattr(obj, name)

    return inner


def item(index: SupportsIndex | K):
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
        >>> row, nil = item('hello')(data)
        >>> row
        [1, 2, 3]
        >>> elem, nil = item(0)(row)
        >>> elem
        1

    """

    @null_and_error_safe(IndexError, KeyError)
    @overload
    def inner(iterable: Mapping[K, T]) -> T:
        ...

    @null_and_error_safe(IndexError)
    @overload
    def inner(iterable: Sequence[T]) -> T:
        ...

    @null_and_error_safe(IndexError)
    @overload
    def inner(iterable: Iterable[T]) -> T:
        ...

    @null_and_error_safe(IndexError, KeyError)
    def inner(iterable: Mapping[K, T] | Sequence[T] | Iterable[T]) -> T:
        return iterable[index]

    return inner


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


def assign(key: K):
    """Assign a value to an index or attr on a list, dict or mutable object.

    Has full type support for each of the three different types.

    Note:
        Returns a copy of the updated object wrapped in a `Res` that reflects potential errors.

    Args:
        *key* (K): Any value that can be used as a key for a data structure
        *val* (U): The value to be assigned to the mutable data structure or object
        *sequence* (MutableSequence[T], variant): First of three options. A list or list like object
        *mapping* (MutableMapping[K, V], variant): Second of three options. A dict or dict like object
        *obj* (O, variant): Third of three options. Any object that allows assigning attributes

    Returns:
        sequence_copy (Res[MutableSequence[T | U], IndexError]): A copy of the sequence with the additional value wrapped in a result
        mapping_copy (Res[MutableMapping[K, V], IndexError | KeyError]): A copy of the mapping with the additional value wrapped in a result
        obj_copy (Res[O, AttributeError]): A copy of the original object with the attribute assigned, wrapped in a result

    Example: ::

        >>> mapping = {'hello': 'world'}
        >>> val, err = assign('hola')('mundo')(mapping)
        >>> val
        {'hello': 'world', 'hola': 'mundo'}
        >>> sequence = [1, 2, 0]
        >>> val, err = assign(2)(3)(sequence)
        >>> val
        [1, 2, 3]
        >>> class Obj:
        ...     def __init__(self, foo = None):
        ...         self.foo = foo
        ...
        >>> obj, err = assign('foo')('bar')(Obj())
        >>> obj.foo
        'bar'

    """

    def get_val(val: U):
        @overload
        def get_obj(
            obj: MutableSequence[T],
        ) -> Res[MutableSequence[T | U], IndexError]:
            ...

        @overload
        def get_obj(
            obj: MutableMapping[K, T]
        ) -> Res[MutableMapping[K, T | U], IndexError | KeyError]:
            ...

        @overload
        def get_obj(obj: O) -> Res[O, AttributeError]:
            ...

        @safe(IndexError, KeyError, AttributeError)
        def get_obj(
            obj: MutableSequence[T] | MutableMapping[K, T] | O
        ) -> MutableSequence[T | U] | MutableMapping[K, T | U] | O:
            if not isinstance(obj, MutableMapping) and not isinstance(
                obj, MutableSequence
            ):
                setattr(obj, key, val)
                return obj
            setitem(obj, key, val)
            return obj

        return get_obj

    return get_val
