"""
Functions used to operate over data structures
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
    MutableMapping,
)
from functools import reduce
from copy import deepcopy
from pythonix.internals.res import null_and_error_safe, safe, combine_errors
from operator import setitem
from pythonix.internals.curry import three


Val = TypeVar("Val")
SecondVal = TypeVar("SecondVal")
NewVal = TypeVar("NewVal")
ObjT = TypeVar("ObjT", bound="object")
Key = TypeVar("Key", str, int, float, tuple)


def filterx(using: Callable[[Val], bool]) -> Callable[[Iterable[Val]], Iterator[Val]]:
    """
    Filter over an `Iterable` with a function that takes each of its elements and returns a True or False.
    True evaluations are kept while False are not kept in the result.
    """

    def get_data(iterable: Iterable[Val]) -> Iterator[Val]:
        return filter(using, iterable)

    return get_data


def mapx(using: Callable[[Val], NewVal]) -> Callable[[Iterable[Val]], Iterator[NewVal]]:
    """
    Run the `using` function over an `Iterable` and return an `Iterator` containing the result.
    """

    def get_data(iterable: Iterable[Val]) -> Iterator[NewVal]:
        return map(using, iterable)

    return get_data


def reducex(
    using: Callable[[Val, SecondVal], NewVal]
) -> Callable[[Iterable[Val | SecondVal]], Iterator[NewVal]]:
    """
    Run a function that takes two arguments over an `Iterable` to produce a single result.
    """

    def get_data(iterable: Iterable[Val | SecondVal]) -> NewVal:
        return reduce(using, iterable)

    return get_data


def attr(name: str, type_hint: type[NewVal] = Any):
    """
    Used to safely retrieve attributes from classes in a functional way.
    Can be used with a `type_hint` parameter to provide better type hint support.
    #### Example
    ```python
    from pythonix import Res
    from collections import namedtuple

    Point = namedtuple('Point', ('x', 'y'))
    p1 = Point(5, 4)
    x: Res[int, Nil] = attr('x', int)(p1)
    z: Res[int, Nil] = attr('z')(p1)

    assert x.inner = 5
    assert z.inner is Nil
    ```
    """

    @null_and_error_safe(AttributeError)
    def inner(obj: Val) -> NewVal:
        return getattr(obj, name)

    return inner


def item(index: SupportsIndex | Key):
    """
    Used to safely retrieve items from sequences and mappings in a functional way.
    #### Example
    ```python
    from pythonix.res import Res
    from pythonix.op import item

    p1 = (5, 4)
    p2 = {'hello': 0}
    x: Res[int, Nil] = item(0)(p1)
    z: Res[int, Nil] = item('invalid key')(p1)

    assert x.inner = 5
    assert z.inner is Nil
    ```
    """

    @null_and_error_safe(IndexError, KeyError)
    def inner(iterable: Iterable[Val]) -> Val:
        return iterable[index]

    return inner


def arg(val: Val):
    """
    Applies a single argument to a function and returns its result.
    Useful for piping an argument into a function via `Bind` or `Do`
    """

    def get_op(op: Callable[[Val], NewVal]) -> NewVal:
        return op(val)

    return get_op


class AssignError(Exception):
    def __init__(self, message="An error occurred assigning a value"):
        self.message = message


@three
@combine_errors(AssignError(), True)
@safe(IndexError, TypeError)
@overload
def assign_item(
    key: SupportsIndex | slice, val: NewVal, data: MutableSequence[Val]
) -> MutableSequence[Val | NewVal]:
    ...


@three
@combine_errors(AssignError(), True)
@safe(KeyError, TypeError, IndexError)
@overload
def assign_item(
    key: Key, val: NewVal, data: MutableMapping[Key, Val]
) -> MutableMapping[Key, Val | NewVal]:
    ...


@three
@combine_errors(AssignError(), True)
@safe(KeyError, IndexError, TypeError)
def assign_item(
    key: SupportsIndex | slice | Key,
    val: NewVal,
    data: MutableSequence[Val] | MutableMapping[Key, Val],
) -> MutableSequence[Val | NewVal] | MutableMapping[Key, Val | NewVal]:
    """
    Safely assigns a new value to a specific index for a mutable data structure, i.e a list or dictionary.
    Will not panic during failure, rather it will return a `Res` with either the expected value or its Exception.
    Returns a deepcopy of the original data, treating the mutable sequence like an immutable type.
    #### Example
    ```python
    x: list[str] = ['hello', 'world']
    ass_res = assign_item(0)('hola')(data)
    hola_x = res.unwrap(ass_res)

    assert x[0] == 'hello'
    assert hola_x[0] == 'hola'
    ```
    """
    copy: MutableSequence[Val] | MutableMapping[Key, Val] = deepcopy(data)
    setitem(copy, key, val)
    return copy


@three
@safe(AttributeError)
def assign_attr(key: str, val: NewVal, obj: ObjT) -> ObjT:
    """
    Safely assigns a new value to an attribute for an object. Will not panic upon failure, but instead
    returns a `Res` indicating the expected value on success, or the expected `Exception` on failure.
    Returns a deepcopy of the original object, treating the mutable object like an immutable type.
    #### Example
    ```python
    class Foo(object):
        def __init__(self, bar):
            self.bar = bar
    
    foo = Foo(0)
    ass_res = assign_attr('baz')(1)(foo)
    with_baz = res.unwrap(ass_res)

    assert with_baz.baz == 1
    assert hasattr(foo, 'baz') == False 
    ```
    """
    copy: ObjT = deepcopy(obj)
    setattr(copy, key, val)
    return copy
