"""Key value pair utility functions to make using pairs easier.

Includes methods for creating pairs, setting and gettings keys and values, and mapping over a value.

Example:
    ```python
    from pythonix.prelude import *

    (
        B(pair.new('foo')(None))
        (pair.set_key('bar'))
        (pair.set_value(5))
        (pair.map(lambda x: x + 5))
        .do
        (pair.get_value |P| prove.equals(10) |P| res.unwrap)
        (pair.get_key |P| prove.equals('bar') |P| res.unwrap)
        (prove.equals(('bar', 10)) |P| res.unwrap)
    )
    ```

"""
from typing import NamedTuple, Tuple, TypeVar, Generic, TypeAlias, Callable
from pythonix.curry import two


T = TypeVar("T")
U = TypeVar("U")
KeyStr: TypeAlias = str


class Pair(Generic[T], NamedTuple):
    """A typed key value pair whose key is a `str`. Immutable by default.

    Note:
        This can be created using the class, or thru
        the convenience function `new`

    Attributes:
        key (str): The key for the pair
        value (T): Any valid value

    Example:
        ```python
        from pythonix.prelude import *

        foo_pair = pair.Pair('foo', 10)
        assert foo_pair.key == 'foo'
        assert foo_pair.value == 10
        ```
    """

    key: str
    value: T


Pairs: TypeAlias = Tuple[Pair[T], ...]
"""Convenient type alias for a tuple of key value pairs"""


@two
def new(key: KeyStr, value: T) -> Pair[T]:
    """Create a new key value `Pair` safely

    Args:
        key (KeyStr): A string used as the key for the key value pair
        value (T): Any value to be paired with the key

    Returns:
        pair (Pair[T]): A new pair with the given key and value

    Example:
        ```python
        from pythonix.prelude import *

        foo_pair = pair.new('foo')(10)
        assert foo_pair.key == 'foo'
        assert foo_pair.value == 10
        ```
    """
    return Pair(key, value)


@two
def set_key(key: KeyStr, pair: Pair[T]) -> Pair[T]:
    """Creates a new `Pair` from a provided one with the provided key.

    Args:
        key (KeyStr): The desired key
        pair (Pair[T]): The pair whose key will be replaced

    Returns:
        pair (Pair[T]): A new Pair[T] with the same value but different key

    Example:
        ```python
        from pythonix.prelude import *

        (
            pair.new('foo')(10)
            |P| pair.set_key('bar')
            |P| pair.get_value
            |P| prove.equals(10)
            |P| res.unwrap
        )
        ```
    """
    return new(key)(pair.value)


@two
def set_value(value: U, pair: Pair[T]) -> Pair[U]:
    """Creates a new `Pair` with a new value, preserving its key.

    Args:
        value (U): The new value, of the same or different type
        pair (Pair[T]): A pair with the same or different inner type

    Returns:
        new_pair (Pair[U]): A pair with the updated value but identical key

    Example:
        ```python
        from pythonix.prelude import *

        (
            pair.new('foo')(5)
            |P| pair.set_value(10)
            |P| pair.get_value
            |P| prove.equals(10)
            |P| res.unwrap
        )
        ```
    """
    return new(pair.key)(value)


def get_value(pair: Pair[T]) -> T:
    """Retrieves the `value` of a provided `Pair`

    Args:
        pair (Pairt[T]): A pair that contains a value

    Returns:
        value (T): The contained value

    Example:
        ```python
        from pythonix.prelude import *

        (
            pair.new('foo')(10)
            |P| pair.get_value
            |P| prove.equals(10)
            |P| res.unwrap
        )
        ```
    """
    return pair.value


def get_key(pair: Pair[T]) -> KeyStr:
    """Retrieves the `key` of a provided `Pair`

    Args:
        pair (Pair[T]): A pair that contains a key and a value

    Returns:
        key (KeyStr): The key of the Pair

    Example:
        ```python
        from pythonix.prelude import *

        (
            pair.new('foo')(10)
            |P| pair.get_key
            |P| prove.equals('key')
            |P| res.unwrap
        )
        ```
    """
    return pair.key


@two
def map(using: Callable[[T], U], pair: Pair[T]) -> Pair[U]:
    """Change the inner value of a `Pair` with a function

    Args:
        using ((T) -> U): Function that takes an argument and returns a value
        pair (Pair[T]): A Pair with a valid key and value

    Returns:
        pair (Pair[U]): A new pair with the same key but new value from the output of the function

    Example:
        ```python
        from pythonix.prelude import *

        (
            pair.new('foo')(5)
            |P| pair.map(lambda x: x + 5)
            |P| pair.get_value
            |P| prove.equals(10)
            |P| res.unwrap
        )
        ```
    """
    return set_value(using(pair.value))(pair)
