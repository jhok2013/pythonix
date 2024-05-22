"""Covers for the ``deque`` methods with type hints. Error, None, and type safe.

Does not return copies of the ``deque``, but instead mutable references
to the ``deq`` it recieves. A useful data structure with thread safe
appends and pops.

Examples: ::

    >>> deq = new(1, 2, 3)
    >>> val, nil = unpack(get(0)(deq))
    >>> val
    1

"""
from collections import deque as deque
from typing import Iterable, TypeVar, cast, SupportsIndex
from pythonix.internals.res import null_and_error_safe, safe, null_safe, Opt
from pythonix.internals.curry import two, three
from pythonix.internals.res import unpack

T = TypeVar("T")
U = TypeVar("U")


def new(*vals: T, **kwargs: int) -> deque[T]:
    """Create a new typed ``deque`` object. Use the maxlen kwarg to specify maxlen

    Example: ::

        >>> deq: deque[T] = new(1, 2, 3)
        >>> deq
        deque([1, 2, 3])

    """
    return deque(vals, maxlen=kwargs.get('maxlen'))


@two
def append(element: U, deq: deque[T]) -> deque[T | U]:
    """Appends an element to the end of a ``deque``
    
    Example: ::

        >>> deq: deque[int] = append(4)(deque((1, 2, 3)))
        >>> val, nil = unpack(pop(deq))
        >>> val
        4
    
    """
    deq.append(cast(T, element))
    return cast(deque[T | U], deq)


@two
def appendleft(element: U, deq: deque[T]) -> deque[T | U]:
    """Appends an element to the beginning of a ``deque``
    
    Example: ::

        >>> deq: deque[int] = appendleft(4)(new(1, 2, 3))
        >>> val, nil = unpack(popleft(deq))
        >>> val
        4

    """
    deq.appendleft(cast(T, element))
    return cast(deque[T | U], deq)


def clear(deq: deque[T]) -> deque[T]:
    """Clears the deque of all elements
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> cleared = clear(deq)
        >>> val, nil = unpack(pop(cleared))
        >>> nil
        Nil('pop from an empty deque')
    
    """
    deq.clear()
    return deq


def copy(deq: deque[T]) -> deque[T]:
    """Returns a shallow copy of the deque
    
    Example: ::

        >>> deq1: deque[int] = new(1, 2, 3)
        >>> deq2: deque[int] = copy(deq1)
        >>> deq1 = appendleft(4)(deq1)
        >>> deq2
        deque([1, 2, 3])
    
    """
    return deq.copy()


@two
def count(element: T, deq: deque[T]) -> int:
    """Returns a count of how many elements match the provided one
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 2, 3)
        >>> count(2)(deq)
        2
    
    """
    return deq.count(element)


@two
def extend(iterable: Iterable[U], deq: deque[T]) -> deque[T | U]:
    """Combines an iterable to the right side of the deque
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> combined = extend([4, 5, 6])(deq)
        >>> deq
        deque([1, 2, 3, 4, 5, 6])
    
    """
    deq.extend(cast(Iterable[T], iterable))
    return cast(deque[T | U], deq)

@two
def extendleft(iterable: Iterable[U], deq: deque[T]) -> deque[T | U]:
    """Combines an iterable to the left side of the deque
    
    Example: ::

        >>> deq: deque[int] = new(4, 5, 6)
        >>> combined = extendleft([3, 2, 1])(deq)
        >>> deq
        deque([1, 2, 3, 4, 5, 6])
    
    """
    deq.extendleft(cast(Iterable[T], iterable))
    return cast(deque[T | U], deq)


@three
def insert(element: U, index: int, deq: deque[T]) -> deque[T | U]:
    """Insert a new element at the specified index
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> insert(0)(0)(deq)
        deque([0, 1, 2, 3])
    
    """
    deq.insert(index, cast(T, element))
    return cast(deque[T | U], deq)


def index(element: T, **kwargs: int):
    """Retrieves the index of the first occurence of a given element
    
    Use the ``start`` and ``stop`` *kwargs* to specify where to start and stop.

    Examples: ::

        >>> deq: deque[int] = new(1, 2, 2, 3, 4)
        >>> index(2)(deq)
        1
        >>> index(2, start=2)(deq)
        2
    
    """

    def inner(deq: deque[T]) -> int:
        if 'start' in kwargs.keys() and 'stop' in kwargs.keys():
            start = kwargs.get('start')
            stop = kwargs.get('stop')
            if start is not None and stop is not None:
                return deq.index(element, start, stop)
        if 'start' in kwargs.keys():
            start = kwargs.get('start')
            if start is not None:
                return deq.index(element, start) 
        return deq.index(element)
    
    return inner


@two
@null_and_error_safe(IndexError)
def get(index: SupportsIndex, deq: deque[T]) -> T:
    """Retrieve the element at a given index
    
    Examples: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> val, nil = unpack(get(0)(deq))
        >>> val
        1
        >>> val, nil = unpack(get(4)(deq))
        >>> nil
        Nil('deque index out of range')
    
    """
    return deq[index]


@null_and_error_safe(IndexError)
def pop(deq: deque[T]) -> T:
    """Retrieve and remove the last element
    
    Examples: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> val, nil = unpack(pop(deq))
        >>> val
        3
        >>> deq
        deque([1, 2])
    
    """
    return deq.pop()

@null_and_error_safe(IndexError)
def popleft(deq: deque[T]) -> T:
    """Retrieve and remove the first element
    
    Examples: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> val, nil = unpack(popleft(deq))
        >>> val
        1
        >>> deq
        deque([2, 3])
    
    """
    return deq.popleft()


@two
@safe(IndexError)
def remove(element: T, deq: deque[T]) -> deque[T]:
    """Remove an element if it's present
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> deq, nil = unpack(remove(2)(deq))
        >>> deq
        deque([1, 3])
    
    """
    deq.remove(element)
    return deq


def reverse(deq: deque[T]) -> deque[T]:
    """Reverse the order of elements
    
    Examples: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> reverse(deq)
        deque([3, 2, 1])
    
    """
    deq.reverse()
    return deq


def rotate(n: int = 1):
    """Brings the last element to be first *n* times
    
    Examples: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> rotate()(deq)
        deque([3, 1, 2])
        >>> rotate()(deq)
        deque([2, 3, 1])
        >>> rotate()(deq)
        deque([1, 2, 3])
    
    """
    def inner(deq: deque[T]) -> deque[T]:

        deq.rotate(n)
        return deq
    
    return inner


def first(deq: deque[T]) -> Opt[T]:
    """Gets the first element
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> val, nil = unpack(first(deq))
        >>> val
        1
    
    """
    return get(0)(deq)


def last(deq: deque[T]) -> Opt[T]:
    """Gets the last element
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 3)
        >>> val, nil = unpack(last(deq))
        >>> val
        3
    
    """
    return get(-1)(deq)


@null_safe
def maxlen(deq: deque[T]) -> int | None:
    """Gets the maximum length of the deque
    
    Example: ::

        >>> deq: deque[int] = new(1, 2, 3, maxlen=3)
        >>> m, nil = unpack(maxlen(deq))
        >>> m
        3

    """
    return deq.maxlen
