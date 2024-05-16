"""
Module for handling key value pairs.
"""

from typing import NamedTuple, Tuple, TypeVar, Generic, TypeAlias, Callable
from pythonix.curry import two


Val = TypeVar("Val")
NewVal = TypeVar("NewVal")
KeyStr: TypeAlias = str


class Pair(Generic[Val], NamedTuple):
    """
    A typed key value pair whose key is a `str`
    """

    key: str
    value: Val


Pairs: TypeAlias = Tuple[Pair[Val], ...]


@two
def new(key: KeyStr, value: Val) -> Pair[Val]:
    """
    Create a new key value `Pair` safely
    """
    return Pair(key, value)


@two
def set_key(key: KeyStr, pair: Pair[Val]) -> Pair[Val]:
    """
    Creates a new `Pair` from a provided one with the provided key.
    """
    return new(key)(pair.value)


@two
def set_value(value: NewVal, pair: Pair[Val]) -> Pair[NewVal]:
    """
    Creates a new `Pair` with a new value, preserving its key.
    """
    return new(pair.key)(value)


def get_value(pair: Pair[Val]) -> Val:
    """
    Retrieves the `value` of a provided `Pair`
    """
    return pair.value


def get_key(pair: Pair[Val]) -> KeyStr:
    """
    Retrieves the `key` of a provided `Pair`
    """
    return pair.key


@two
def map(using: Callable[[Val], NewVal], pair: Pair[Val]) -> Pair[NewVal]:
    """
    Change the inner value of a `Pair` with a function
    """
    return set_value(using(pair.value))(pair)
