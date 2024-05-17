"""
Functions used to operate over data structures.

Comparable to the filter, map, reduce, getitem, getattr, setitem, and setattr functions.
Can be used easily with the Bind, Pipe, and Do wrapper types. All functions are as
error proof as possible.

Examples:
    List:
        ```python
        from pythonix.prelude import *
        from operator import add

        (
            Bind([1, 2, 3, 4])
            (op.item(0))(q)
            (op.filterx(lambda x: x % 2 == 0))
            (op.mapx(lambda x: x + 1))
            (list)
            (op.fold(add))
            (prove.equals(8))(q)
        )
        ```
    Dict:
        ```python
        from pythonix.prelude import *

        (
            Bind({'hello': 'world'})
            (op.item(1))(q)
            (op.item('hello'))(q)
            (prove.equals('world))(q)
        )
        ```

    Object:
        ```python
        from pythonix.prelude import *

        (
            Bind(object.__new__(object))
            (op.item(2))(q)
            (op.assign('foo')('bar'))(q)
            (op.attr('foo'))(q)
            (prove.equals('bar'))(q)
        )
        ```

    Arg Application:
    ```python
        (
            (lambda x: x + 1)
            |P| op.arg(10)
            |P| prove.equals(11)
            |P| q
        )
    ```
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
from copy import deepcopy
from pythonix.internals.res import null_and_error_safe, safe, Res
from operator import setitem


T = TypeVar("T")
S = TypeVar("S")
U = TypeVar("U")
O = TypeVar("O", bound="object")
K = TypeVar("K", str, int, float, tuple, slice)


def filterx(using: Callable[[T], bool]) -> Callable[[Iterable[T]], Iterator[T]]:
    """Filter over an `Iterable` with a function. 
    
    Function takes each of its elements and returns a True or False.
    True evaluations are kept while False are not kept in the result.

    Note:
        Returns a lazy iterator that must be collected.
    
    Args:
        using ((T) -> bool): Function that takes a value *T* and returns True or False
        iterable (Iterable[T]): List, tuple, or other iterable
    
    Returns:
        iterator (Iterator[T]): Lazy iterator of the same type as the iterable, but with only the elements
        that evaluated to True

    Example:
        ```python
        from pythonix.prelude import *

        (
            (1, 2, 3, 4)
            |P| op.filterx(lambda x: x % 2 == 0)
            |P| tuple
            |P| prove.that(lambda t: len(t) == 2)
            |P| res.unwrap
        )
        ```
    """

    def get_data(iterable: Iterable[T]) -> Iterator[T]:
        return filter(using, iterable)

    return get_data


def mapx(using: Callable[[T], U]) -> Callable[[Iterable[T]], Iterator[U]]:
    """Run a function over an `Iterable` and return an `Iterator` the outputs.

    Note:
        Returns a lazy iterator that must be collected.
    
    Args:
        using ((T) -> U): Function that will be applied over each element of the Iterable
        iterable (Iterable[T]): List, tuple, or other iterable.
    
    Returns:
        iterator (Iterator[U]): Lazy iterator containing the result of *using* over the *iterable*

    Example:
        ```python
        from pythonix.prelude import *

        (
            B((1, 2, 3, 4))
            (op.mapx(lambda x: x + 1))
            (tuple)
            (prove.contains(5))
            (res.unwrap)
        )
        ```        
    """

    def get_data(iterable: Iterable[T]) -> Iterator[U]:
        return map(using, iterable)

    return get_data


def fold(
    using: Callable[[T, S], U]
) -> Callable[[Iterable[T | S]], U]:
    """Apply a function to accumulated pairs of elements in an iterable to a single final value
    
    Args:
        using ((T, S) -> U): Function that takes two arguments and returns a single element of the same type
        iterable (Iterable[T | S]): List, tuple, or other sequence of the same type
    
    Returns:
        _ (U): Accumulated final value

    Example:
        ```python
        from pythonix.prelude import *
        from operator import add

        (
            (1, 2, 3, 4)
            |P| op.fold(add)
            |P| prove.equals(10)
            |P| res.unwrap
        )
        ```    
    """
    def get_data(iterable: Iterable[T | S]) -> U:
        return reduce(using, iterable)

    return get_data


def attr(name: str, type_hint: type[U] = Any) -> Callable[[T], U]:
    """Used to safely retrieve attributes from classes in a functional way.
    
    Can be used with a `type_hint` parameter to provide better type hint support.

    Args:
        name (str): The name of the attribute to retrieve
        obj (T): Any object
    
    Returns:
        opt (Res[U, Nil]): Result type containing the desired value if Ok, or Nil if Err
    
    Example:
        ```python
        from pythonix.prelude import *
        from collections import namedtuple

        Point = namedtuple('Point', ('x', 'y'))
        (
            B(Point(5, 4))
            (op.attr('x', int))
            (res.unwrap)
            (prove.equals(5))
            (res.unwrap)
        )
        ```
    """

    @null_and_error_safe(AttributeError)
    def inner(obj: T) -> U:
        return getattr(obj, name)

    return inner


def item(index: SupportsIndex | K):
    """Used to safely retrieve items from sequences and mappings in a functional way.

    Note:
        The second arguments are overloaded. Different data types will result in different
        return types.

    Args:
        index (SupportsIndex | K): Any value that can be used for indexing or hashing for mappings or sequences
        mapping (Mapping[K, T], Variant): A key value mapping
        sequence (Sequence[T], Variant): A sequence with values
        iterable (Iterable[T], Variant): An iterable that does not inherit from Mapping or Sequence
    
    Returns:
        opt (Res[U, Nil]): Result type containing either the expected value if Ok, or a Nil if Err
    
    Example
        ```python
        from pythonix.prelude import *

        (
            {'hello': [1, 2, 3]}
            |P| op.item('hello')
            |P| res.unwrap
            |P| op.item(0)
            |P| res.unwrap
        )

        ```
    """

    @null_and_error_safe(IndexError, KeyError)
    @overload
    def inner(mapping: Mapping[K, T]) -> T:
        ...

    @null_and_error_safe(IndexError)
    @overload
    def inner(sequence: Sequence[T]) -> T:
        ...

    @null_and_error_safe(IndexError)
    @overload
    def inner(iterable: Iterable[T]) -> T:
        ...

    @null_and_error_safe(IndexError, KeyError)
    def inner(iterable: Mapping[K, T] | Sequence[T] | Iterable[T]) -> T:
        return iterable[index]

    return inner


def arg(val: T) -> Callable[[Callable[[T], U]], U]:
    """Applies a single argument to a function and returns its result.
    
    Useful for piping an argument into a function via `Bind` or `Do`

    Args:
        val (T): The value to be applied to the single variable function
        op ((T) -> U): The function that will apply T and output U
    
    Returns:
        output (U): The output of the provided function
    
    Example:
        ```python
        from pythonix.prelude import *

        (
            B(lambda x: x + 1)
            (op.arg(10))
            (prove.equals(11))
            (res.unwrap)
        )
        ```
    """

    def get_op(op: Callable[[T], U]) -> U:
        return op(val)

    return get_op


def assign(key: K):
    """Assign a value to a given index or name on a list, dict or mutable object.
    Has full type support for each of the three different types.
    
    Note:
        Returns a copy of the updated object wrapped in a `Res` that reflects potential errors.
    
    Args:
        key (K): Any value that can be used as a key for a data structure
        val (U): The value to be assigned to the mutable data structure or object
        sequence (MutableSequence[T], variant): First of three options. A list or list like object
        mapping (MutableMapping[K, V], variant): Second of three options. A dict or dict like object
        obj (O, variant): Third of three options. Any object that allows assigning attributes
    
    Returns:
        sequence_copy (Res[MutableSequence[T | U], IndexError]): A copy of the sequence with the additional value wrapped in a result
        mapping_copy (Res[MutableMapping[K, V], IndexError | KeyError]): A copy of the mapping with the additional value wrapped in a result
        obj_copy (Res[O, AttributeError]): A copy of the original object with the attribute assigned, wrapped in a result
    
    Example:
        ```python
        from pythonix.prelude import *

        # Assign to a dictionary
        (
            {'foo': 1}
            |P| op.assign('bar')('hello')
            |P| res.unwrap
            |P| prove.that(lambda d: d['bar'] == 'hello')
            |P| res.unwrap
        )

        # Assign to a list
        (
            B([1, 2, 3])
            (op.assign(0)(4))(q)
            (op.item(0))(q)
            (prove.equals(4))(q)
        )

        # Assign to an object
        (
            object.__new__(object)
            |P| op.assign('foo')('bar')
            |P| q
            |P| op.attr('foo')
            |P| q
        )
        
        ```
    """

    def get_val(val: U):
        @overload
        def get_obj(
            sequence: MutableSequence[T],
        ) -> Res[MutableSequence[T | U], IndexError]:
            ...

        @overload
        def get_obj(
            mapping: MutableMapping[K, T]
        ) -> Res[MutableMapping[K, T | U], IndexError | KeyError]:
            ...

        @overload
        def get_obj(obj: O) -> Res[O, AttributeError]:
            ...

        @safe(IndexError, KeyError, AttributeError)
        def get_obj(
            obj: MutableSequence[T] | MutableMapping[K, T] | O
        ) -> MutableSequence[T | U] | MutableMapping[K, T | U] | O:
            copy = deepcopy(obj)
            if not isinstance(obj, MutableMapping) and not isinstance(
                obj, MutableSequence
            ):
                setattr(copy, key, val)
                return copy
            setitem(copy, key, val)
            return copy

        return get_obj

    return get_val
