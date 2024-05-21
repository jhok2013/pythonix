"""Safely handles tuple sequences with an api like lists

Examples: ::

    >>> data = new(1, 2, 3)
    >>> data = push_right(4)(data)
    >>> data = extend_right(new(5, 6, 7))(data)
    >>> i, nil = index(7)(data)
    >>> i
    6
    >>> count_occurrences(3)(data)
    1
    >>> data, nil = remove(1)(data)
    >>> data
    (1, 3, 4, 5, 6, 7)

"""
from typing import Tuple, TypeVar
from pythonix.internals.op import item
from pythonix.internals.res import safe, null_and_error_safe, Opt
from pythonix.internals.curry import two, three
from enum import Enum

T = TypeVar("T")
U = TypeVar("U")
type IndexInt = int


class Side(Enum):
    LEFT: str = "LEFT"
    RIGHT: str = "RIGHT"


def new(*elements: T) -> Tuple[T, ...]:
    """Convenience function to create a new series of data of a given type

    Example: ::

        >>> new(1, 2, 3)
        (1, 2, 3)

    """
    return elements


def push(side: Side = Side.RIGHT):
    """Push an element to either side of a `Tuple`

    Example: ::

        >>> data = new(1, 2, 3)
        >>> push(Side.RIGHT)(4)(data)
        (1, 2, 3, 4)

    """

    def get_element(element: U):
        def inner(tuples: Tuple[T, ...]) -> Tuple[T | U, ...]:
            match side:
                case Side.LEFT:
                    return (element,) + tuples
                case Side.RIGHT:
                    return tuples + (element,)

        return inner

    return get_element


@two
def get(index: IndexInt, tuples: Tuple[T, ...]) -> Opt[T]:
    """Retrieve an element from a `Tuple` at the provided index

    Example: ::

        >>> data = new(1, 2, 3)
        >>> val, nil = get(0)(data)
        >>> val
        1
        >>> val, nil = get(3)(data)
        >>> nil
        Nil('tuple index out of range')

    """
    return item(index)(tuples)


def extend(side: Side = Side.RIGHT):
    """Combine two tuple series together

    Example: ::

        >>> data = new(1, 2, 3)
        >>> extend(Side.RIGHT)(new(4, 5, 6))(data)
        (1, 2, 3, 4, 5, 6)

    """

    def get_left(new: Tuple[T, ...]):
        def get_right(old: Tuple[U, ...]) -> Tuple[T | U, ...]:
            match side:
                case Side.LEFT:
                    return new + old
                case Side.RIGHT:
                    return old + new

        return get_right

    return get_left


@two
@null_and_error_safe(ValueError)
def index(element: T, tuples: Tuple[T, ...]) -> int:
    """Find the index of an element in `Tuple` if it exists

    Example: ::

        >>> data = new(3, 2, 1)
        >>> i, nil = index(3)(data)
        >>> i
        0

    """
    return tuples.index(element)


@two
def count_occurrences(value: T, tuples: Tuple[T, ...]) -> int:
    """Count the occurrences of the provided value in a `Tuple`

    Example: ::

        >>> data = new(1, 2, 3)
        >>> count_occurrences(3)(data)
        1
        >>> count_occurrences(5)(data)
        0

    """
    return tuples.count(value)


@three
def insert(
    index: IndexInt, insert: U, tuples: Tuple[T, ...]
) -> Tuple[T | U, ...]:
    """Recreate the `Tuple` with the provided element at the index

    Example: ::

        >>> data = new(1, 2, 3)
        >>> insert(1)(0)(data)
        (1, 0, 2, 3)

    """
    return tuples[:index] + (insert,) + tuples[index:]


@two
@safe(IndexError)
def remove(index: IndexInt, tuples: Tuple[T, ...]) -> Tuple[T, ...]:
    """Recreate the `Tuple` without the element at the provided index

    Examples: ::

        >>> data = new(1, 2, 3)
        >>> val, err = remove(0)(data)
        >>> val
        (2, 3)

    """
    if index > (length := len(tuples)):
        raise IndexError(f"Incompatible index {index} is greater than length {length}")
    return tuples[:index] + tuples[index + 1 :]


push_left = push(Side.LEFT)
'''Same as push(Side.LEFT)'''
push_right = push(Side.RIGHT)
'''Same as push(Side.RIGHT)'''
extend_left = extend(Side.LEFT)
'''Same as extend(Side.LEFT)'''
extend_right = extend(Side.RIGHT)
'''Same as extend(Side.RIGHT)'''
last = get(-1)
'''Same as get(-1)'''
first = get(0)
'''Same as get(0)'''
