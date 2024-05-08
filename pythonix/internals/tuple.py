"""
Module for handling tuples without risk of panics
"""
from typing import Tuple, TypeVar
from pythonix.op import item
from pythonix.res import safe, null_and_error_safe
from pythonix.curry import two, three
from enum import Enum

Val = TypeVar('Val')
NewVal = TypeVar('NewVal')
type IndexInt = int

class Side(Enum):
    LEFT: str = "LEFT"
    RIGHT: str = "RIGHT"


def new(*elements: Val) -> Tuple[Val, ...]:
    """
    Convenience function to create a new series of data of a given type
    """
    return elements


def push(side: Side = Side.RIGHT):
    """
    Push an element to either side of a `Tuple`
    """
    def get_element(element: NewVal):
        
        def inner(tuples: Tuple[Val, ...]) -> Tuple[Val | NewVal, ...]:

            match side:
                case Side.LEFT:
                    return (element,) + tuples
                case Side.RIGHT:
                    return tuples + (element,)

        return inner

    return get_element


@two
def get(index: IndexInt, tuples: Tuple[Val, ...]):
    """
    Retrieve an element from a `Tuple` at the provided index
    """
    return item(index)(tuples)


def extend(side: Side = Side.RIGHT):
    """
    Combine two tuple series together
    """
    def get_left(new: Tuple[Val, ...]):

        def get_right(old: Tuple[NewVal, ...]) -> Tuple[Val | NewVal, ...]:

            match side:
                case Side.LEFT:
                    return new + old
                case Side.RIGHT:
                    return old + new

        return get_right

    return get_left


@two
@null_and_error_safe(ValueError)
def index(element: Val, tuples: Tuple[Val, ...]) -> int:
    """
    Find the index of an element in `Tuple` if it exists
    """
    return tuples.index(element)


@two
def count_occurrences(value: Val, tuples: Tuple[Val, ...]) -> int:
    """
    Count the occurrences of the provided value in a `Tuple`
    """
    return tuples.count(value)


@three
def insert(index: IndexInt, insert: NewVal, tuples: Tuple[Val, ...]) -> Tuple[Val | NewVal, ...]:
    """
    Recreate the `Tuple` with the provided element at the index
    """
    return tuples[:index] + (insert,) + tuples[index:]


@two
@safe(IndexError)
def remove(index: IndexInt, tuples: Tuple[Val, ...]) -> Tuple[Val, ...]:
    """
    Recreate the `Tuple` without the element at the provided index
    """
    if index > (length := len(tuples)):
        raise IndexError(f'Incompatible index {index} is greater than length {length}')
    return tuples[:index] + tuples[index+1:] 


push_left = push(Side.LEFT)
push_right = push(Side.RIGHT)
extend_left = extend(Side.LEFT)
extend_right = extend(Side.RIGHT)
last = get(-1)
first = get(0)
