"""Key value pair utility functions to make using pairs easier.

Includes methods for creating pairs, setting and gettings keys and values,
and mapping over a value.

Example: ::

    >>> pair = new('foo')(None)
    >>> pair = key('bar')(pair)
    >>> pair = value(5)(pair)
    >>> pair = map_value(lambda x: x + 5)(pair)
    >>> value(pair)
    10
    >>> key(pair)
    'bar'
    >>> key, val = unpack(pair)
    >>> (key, val)
    ('bar', 10)

"""
from typing import Tuple, TypeVar, Generic, TypeAlias, Callable, overload
from pythonix.curry import two
from dataclasses import dataclass


T = TypeVar("T")
U = TypeVar("U")
KeyStr: TypeAlias = str


@dataclass(frozen=True)
class Pair(Generic[T]):
    """A typed key value pair whose key is a `str`. Immutable by default.

    Attributes:
        key (str): The key for the pair
        value (T): Any valid value

    ## Example ::

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
        key (str): A string used as the key for the key value pair
        value (T): Any value to be paired with the key

    Returns:
        out (Pair[T]): Output pair

    ## Example ::

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
    """Returns the key from a Pair, or sets it
    
    Args:
        key (str): The new key for the upcoming Pair. Excludes pair
        pair (Pair[T]): A Pair with a valid key
    
    Returns:
        key (str): The key from the Pair[T] if a Pair is input
        func (Fn[T, U]): Function that receives a Pair and returns a Pair with the new key
    
    ## Examples ::

        >>> kv_pair: Pair[str] = new('key')('value')
        >>> key(kv_pair)
        'key'
        >>> new_pair: Pair[str] = key('new_key')(kv_pair)
        >>> key(new_pair)
        'new_key'

    """
    match val:
        case Pair(k):
            return k
        case k:
            def get_pair(pair: Pair[T]) -> Pair[T]:
                match pair:
                    case Pair(_, v):
                        return Pair(k, v)
                    case _:
                        raise TypeError('Invalid argument. Should be Pair')
            return get_pair

@overload
def value(val: Pair[T]) -> T: ...

@overload
def value(val: U) -> Callable[[Pair[T]], Pair[U]]: ...

def value(val: U | Pair[T]) -> T | Callable[[Pair[T]], Pair[U]]:
    """Sets or retrieves a value for a Pair
    
    Args:
        val (U): Any value. Will become the new value for a Pair
        pair (Pair[T]): Any pair. Will have its value returned
    
    Returns:
        val (T): The value retrieved from a Pair[T]
        pair (Fn[Pair[T], Pair[U]]): A Pair with the new value
    
    ## Example ::

        >>> kv_pair: Pair[str] = Pair('hello', 'world')
        >>> value(kv_pair)
        'world'
        >>> new_pair: Pair[int] = value(10)(kv_pair)
        >>> value(new_pair)
        10

    """

    match val:
        case Pair(_, v):
            return v
        case v:
            def get_pair(pair: Pair[T]) -> Pair[T]:
                match pair:
                    case Pair(k):
                        return Pair(k, v)
                    case _:
                        raise TypeError('Invalid argument. Should be Pair')
            return get_pair


@two
def map_value(op: Callable[[T], U], pair: Pair[T]) -> Pair[U]:
    """Change the inner value of a `Pair` with a function

    Args:
        op (Fn[T, U]): Function that takes an argument and returns a value
        pair (Pair[T]): A Pair with a valid key and value

    Returns:
        pair (Pair[U]): A new pair with the same key but new value from the output of the function

    ## Example ::

        >>> pair = new('foo')(5)
        >>> pair = map_value(lambda x: x + 5)(pair)
        >>> pair.value
        10

    """
    return value(op(pair.value))(pair)
