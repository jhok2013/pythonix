"""Key value pair utility functions to make using pairs easier.

Includes methods for creating pairs, setting and gettings keys and values,
and mapping over a value.

Example: ::

    >>> pair = new('foo')(None)
    >>> pair = set_key('bar')(pair)
    >>> pair = set_value(5)(pair)
    >>> pair = map_value(lambda x: x + 5)(pair)
    >>> get_value(pair)
    10
    >>> get_key(pair)
    'bar'
    >>> key, val = pair
    >>> (key, val)
    ('bar', 10)

"""
from functools import singledispatch
from typing import Tuple, TypeVar, Generic, TypeAlias, Callable, overload
from pythonix.curry import two
from dataclasses import dataclass


T = TypeVar("T")
U = TypeVar("U")
KeyStr: TypeAlias = str


@dataclass(frozen=True)
class Pair(Generic[T]):
    """A typed key value pair whose key is a `str`. Immutable by default.

    Note:
        This can be created using the class, or thru
        the convenience function `new`

    Attributes:
        *key* (str): The key for the pair
        *value* (T): Any valid value

    Example: ::

        >>> foo_pair = Pair('foo', 10)
        >>> foo_pair.key
        'foo'
        >>> foo_pair.value
        10

    """

    key: str
    value: T


Pairs: TypeAlias = Tuple[Pair[T], ...]
"""Convenient type alias for a tuple of key value pairs"""

def unpack(pair: Pair[T]) -> Tuple[str, T]:
    return pair.key, pair.value

@two
def new(key: KeyStr, value: T) -> Pair[T]:
    """Create a new key value `Pair` safely

    Args:
        key (KeyStr): A string used as the key for the key value pair
        value (T): Any value to be paired with the key

    Returns:
        pair (Pair[T]): A new pair with the given key and value

    Example: ::

        >>> foo_pair = new('foo')(10)
        >>> foo_pair.key
        'foo'
        >>> foo_pair.value
        10

    """
    return Pair(key, value)

@overload
def key(val: str) -> Callable[[Pair[T]], Pair[T]]: ...

@overload
def key(val: Pair[T]) -> str: ...

def key(val: str | Pair[T]) -> Callable[[Pair[T]], Pair[T]] | str:
    
    @singledispatch
    def dispatch(val: str) -> Callable[[Pair[T]], Pair[T]]:
        return lambda pair: Pair(val, pair.value)
    
    @dispatch.register(Pair)
    def _(val: Pair[T]) -> str:
        return val.key
    
    def _(_):
        raise TypeError('Invalid argument. Expected str or Pair[T]')
    
    return dispatch(val)

@overload
def value(val: Pair[T]) -> T: ...

@overload
def value(val: T) -> Callable[[Pair[T]], Pair[T]]: ...

def value(val: T | Pair[T]) -> T | Callable[[Pair[T]], Pair[T]]:

    match val:
        case Pair(_, value):
            return value
        case new_val:
            return lambda pair: Pair(pair.key, new_val)


@two
def map_value(using: Callable[[T], U], pair: Pair[T]) -> Pair[U]:
    """Change the inner value of a `Pair` with a function

    Args:
        using ((T) -> U): Function that takes an argument and returns a value
        pair (Pair[T]): A Pair with a valid key and value

    Returns:
        pair (Pair[U]): A new pair with the same key but new value from the output of the function

    Example:

        >>> pair = new('foo')(5)
        >>> pair = map_value(lambda x: x + 5)(pair)
        >>> pair.value
        10

    """
    return value(using(pair.value))(pair)
