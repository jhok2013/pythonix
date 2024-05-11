"""
Functions used to operate over data structures
"""
from typing import Callable, Iterable, Iterator, Any, SupportsIndex, TypeVar, Mapping
from functools import reduce
from pythonix.internals.res import null_and_error_safe

Val = TypeVar("Val")
SecondVal = TypeVar("SecondVal")
NewVal = TypeVar("NewVal")


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


def item(index: SupportsIndex):
    """
    Used to safely retrieve items from sequences and mappings in a functional way.
    Can be used with a `type_hint` parameter to provide better type hint support.
    #### Example
    ```python
    from pythonix import Res

    p1 = (5, 4)
    x: Res[int, Nil] = item(0)(p1)
    z: Res[int, Nil] = item(2)(p1)

    assert x.inner = 5
    assert z.inner is Nil
    ```
    """

    @null_and_error_safe(IndexError, KeyError)
    def inner(iterable: Iterable[Val]) -> Val:
        return iterable[index]

    return inner


def arg(val: Val):
    '''
    Applies a single argument to a function and returns its result.
    Useful for piping an argument into a function via `Bind` or `Do`
    '''
    def get_op(op: Callable[[Val], NewVal]):

        return op(arg)
    
    return get_op
