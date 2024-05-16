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
    Sequence,
    MutableMapping,
    Mapping,
)
from functools import reduce
from copy import deepcopy
from pythonix.internals.res import null_and_error_safe, safe, Res
from operator import setitem


Val = TypeVar("Val")
SecondVal = TypeVar("SecondVal")
NewVal = TypeVar("NewVal")
ObjT = TypeVar("ObjT", bound="object")
Key = TypeVar("Key", str, int, float, tuple, slice)


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
    @overload
    def inner(mapping: Mapping[Key, Val]) -> Val:
        ...

    @null_and_error_safe(IndexError)
    @overload
    def inner(sequence: Sequence[Val]) -> Val:
        ...

    @null_and_error_safe(IndexError)
    @overload
    def inner(iterable: Iterable[Val]) -> Val:
        ...

    @null_and_error_safe(IndexError, KeyError)
    def inner(iterable: Mapping[Key, Val] | Sequence[Val] | Iterable[Val]) -> Val:
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


def assign(key: Key):
    """
    Assign a value to a given index or name on any mutable sequence (i.e. `list`), mutable mapping (i.e. `dict`)
    or any mutable object. Returns a copy of the updated object wrapped in a `Res` that reflects potential errors.
    Has full type support for each of the three different types.
    ```python
    # Assign to a dictionary
    start_d: dict[str, int] = {'foo': 1}
    end_d: dict[str, int | str] = assign('bar')('hello')(start_d)
    assert end_d['bar'] == 'hello'

    # Assign to a list
    start_l: list[int] = [1, 2, 3]
    end_l: list[int | str] = assign(0)('first')(start_l)
    assert end_l[0] == 'first'

    # Assign to an object
    start_obj: object = object.__new__(object)
    end_obj: object = assign('foo')('bar')(start_obj)
    assert end_obj == 'bar'
    ```
    """

    def get_val(val: NewVal):
        @overload
        def get_obj(
            sequence: MutableSequence[Val],
        ) -> Res[MutableSequence[Val | NewVal], IndexError]:
            ...

        @overload
        def get_obj(
            mapping: MutableMapping[Key, Val]
        ) -> Res[MutableMapping[Key, Val | NewVal], IndexError | KeyError]:
            ...

        @overload
        def get_obj(obj: ObjT) -> Res[ObjT, AttributeError]:
            ...

        @safe(IndexError, KeyError, AttributeError)
        def get_obj(
            obj: MutableSequence[Val] | MutableMapping[Key, Val] | ObjT
        ) -> MutableSequence[Val | NewVal] | MutableMapping[Key, Val | NewVal] | ObjT:
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
