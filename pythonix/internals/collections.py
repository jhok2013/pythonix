from __future__ import annotations
from typing import (
    cast,
    TypeVar,
    Generic,
    Callable,
    Tuple,
    overload,
    Iterable,
    SupportsIndex,
    Protocol,
)
from typing_extensions import Self
from collections import deque
from dataclasses import dataclass
from pythonix.internals.res import Res, Nil


_KT = TypeVar("_KT")
_VT_co = TypeVar("_VT_co", covariant=True)
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")
K = TypeVar("K")
L = TypeVar("L")
NewK = TypeVar("NewK")
NewV = TypeVar("NewV")


@dataclass(
    frozen=True, eq=True, init=True, match_args=True, order=True, repr=True, slots=True
)
class Pair(Generic[T]):
    """Wrapper for a key value pair

    Args:
        key (str): The name for the value
        value (T): The value

    """

    key: str
    value: T

    def map(self, using: Callable[[T], U]) -> Pair[U]:
        """Transforms the value using a function

        Args:
            using (Callable[[T], U]): Func that takes value and returns an output

        Returns:
            Pair[U]: The new Pair
        """
        return Pair(self.key, using(self.value))


class SupportsKeysAndGetItem(Protocol[_KT, _VT_co]):
    def keys(self) -> Iterable[_KT]:
        ...

    def __getitem__(self, key: _KT, /) -> _VT_co:
        ...


class Deq(deque[T]):
    """Upgraded version of `deque` with safe retrieval, fluent interface, and better type support"""

    def __init__(self, iterable: Iterable[T], maxlen: int | None = None):
        """Upgraded version of `deque` with safe retrieval, fluent interface, and better type support

        Args:
            iterable (Iterable[T]): Any singly typed iterable, like list or tuple
            maxlen (int | None, optional): The maximum number of elements allowed. Defaults to None.
        """
        super().__init__(iterable, maxlen)

    def __getitem__(self, key: SupportsIndex) -> Res[T, Nil]:
        try:
            return Res.Some(super().__getitem__(key))
        except (IndexError, KeyError) as e:
            return Res[T, Nil].Nil(str(e))

    def get(self, index: int) -> Res[T, Nil]:
        """Retrieves a value as an `Opt[T]` at a given index

        Args:
            index (int): Index of the desired value

        Returns:
            Opt[T]: The retrieved value as an Opt[T]. Must be handled.
        """
        return self[index]

    def append(self: Deq[T | U], x: U) -> Deq[T | U]:
        """Appends a value to the right of the Deq, updating type information.

        Args:
            x (U): The value to be appended

        Returns:
            Deq[T | U]: Updated version of the Deq
        """
        super().append(x)
        return self

    def appendleft(self: Deq[T | U], x: U) -> Deq[T | U]:
        """Appends a value to the right of the Deq, updating type information.

        Args:
            x (U): The value to be appended to the left

        Returns:
            Deq[T | U]: Updated version of the Deq
        """
        super().appendleft(x)
        return self

    def clear(self) -> Deq[T]:
        """Clears out the Deq

        Returns:
            Deq[None]: The cleared deq with nothing inside
        """
        super().clear()
        return self

    def extend(self: Deq[T | U], iterable: Iterable[U]) -> Deq[T | U]:
        """Appends an iterable to the Deq, updating type information

        Args:
            iterable (Iterable[U]): Any singly typed iterable

        Returns:
            Deq[T | U]: The updated Deq
        """
        super().extend(iterable)
        return self

    def extendleft(self: Deq[T | U], iterable: Iterable[U]) -> Deq[T | U]:
        """Appends an iterable to the left of the Deq, updating type information

        Args:
            iterable (Iterable[U]): Any singly typed iterable

        Returns:
            Deq[T | U]: The updated Deq
        """
        super().extendleft(iterable)
        return self

    def insert(self: Deq[T | U], i: int, x: U) -> Deq[T | U]:
        """Inserts a value at a given index

        Args:
            i (int): Insertion index for the value
            x (U): The value to be inserted

        Returns:
            Deq[T | U]: _description_
        """
        super().insert(i, x)
        return self

    def pop(self) -> Res[T, Nil]:
        """Returns and removes the right most element of the Deq as an `Opt`

        Returns:
            Opt[T]: The expected element wrapped in an `Opt`
        """
        try:
            return Res.Some(super().pop())
        except IndexError as e:
            return Res[T, Nil].Nil(str(e))

    def popleft(self) -> Res[T, Nil]:
        """Returns and removes the left most element of the Deq as an `Opt`

        Returns:
            Opt[T]: The left most element of the Deq in an `Opt`
        """
        try:
            return Res.Some(super().popleft())
        except IndexError as e:
            return Res[T, Nil].Nil(str(e))

    def remove(self, value: T) -> Res[Deq[T], ValueError]:
        """Removes the element with the provided value

        Args:
            value (T): The value to remove

        Returns:
            Res[Deq[T], ValueError]: A result containing the Deq without the element
        """
        try:
            super().remove(value)
            return Res[Deq[T], ValueError].Ok(self)
        except ValueError as e:
            return Res[Deq[T], ValueError].Err(e)

    def reverse(self) -> Deq[T]:
        """Reverses the order of the Deq

        Returns:
            Deq[T]: The reversed Deq
        """
        super().reverse()
        return self

    def rotate(self, n: int = 1) -> Deq[T]:
        """Rotates the Deq a number of times

        Args:
            n (int, optional): The number of times to rotate the Deq. Defaults to 1.

        Returns:
            Deq[T]: The rotated Deq
        """
        super().rotate(n)
        return self

    def map(self, using: Callable[[T], U]) -> Deq[U]:
        """Runs a function over each element in the Deq, returning a new one

        Args:
            using (Callable[[T], U]): Function that transforms the element

        Returns:
            Deq[U]: The transformed Deq
        """
        return Deq([using(elem) for elem in self])

    def where(self, using: Callable[[T], bool]) -> Deq[T]:
        """Filters the deq where each element evaluates to True

        Args:
            using (Callable[[T], bool]): Function to filter the Deq

        Returns:
            Deq[T]: The filtered Deq
        """
        return Deq([elem for elem in self if using(elem) == True])

    def index(
        self, x: T, start: int = 0, stop: int = 9223372036854775807
    ) -> Res[int, Nil]:
        """Retrieves the index of the specified value as an `Opt`

        Args:
            x (T): The desired value
            start (int, optional): Starting index for search. Defaults to 0.
            stop (int, optional): Ending index for search. Defaults to 9223372036854775807

        Returns:
            Opt[int]: The index of the value, or Nil
        """
        try:
            return Res.Some(super().index(x, start, stop))
        except ValueError as e:
            return Res[int, Nil].Nil(str(e))

    @property
    def maxlen(self) -> Res[int, Nil]:
        """Returns the maximum capacity if set, else Nil

        Returns:
            Opt[int]: Maximum capactity, else Nil
        """
        return Res.Some(super().maxlen)


class DictPlus(dict[K, V]):
    """Upgraded `dict` with safe getters, better type handling, and fluent methods

    Has an identical constructor to `dict`. All `dict` methods are supported.

    ### Examples

    `dict` methods return references to the new dict, which allows better chaining ::

        >>> d = (
        ...     DictPlus({"hello": "world"})
        ...     .put("hola", "mundo")
        ...     .update({"top": "ten"})
        ...     .map(str.lower)
        ...     .map_keys(str.upper)
        ...     .where(lambda k, v: k != "TOP")
        >>> )

    Safe getters return `Opt[V]` so no unexpected crashes or None values

        >>> hello_opt: Opt[str | int] = x.pop("HELLO")
        >>> hello_opt.unwrap()
        'world'

    """

    def __getitem__(self, key: K) -> Res[V, Nil]:
        try:
            return Res.Some(super().__getitem__(key))
        except (KeyError, IndexError) as e:
            return Res[V, Nil].Nil(str(e))

    def get(self, key: K) -> Res[V, Nil]:
        """Retrieves a value if key exists, else Nil

        Args:
            key (K): Hashable key whose value will be returned

        Returns:
            Opt[V]: The returned value
        """
        return self[key]

    def pop(self, key: K) -> Res[V, Nil]:
        """Returns a value and removes it from the `dict`

        Args:
            key (K): The key for the item desired

        Returns:
            Opt[V]: The desired item wrapped in an `Opt`
        """
        try:
            return Res.Some(super().pop(key))
        except (KeyError, IndexError) as e:
            return Res[V, Nil].Nil(str(e))

    def popitem(self) -> Res[Tuple[K, V], Nil]:
        """Removes and returns the farthest right key value tuple

        Returns:
            Opt[Tuple[K | V]]: The farthest right key value tuple or Nil
        """
        try:
            return Res.Some(super().popitem())
        except (KeyError, IndexError) as e:
            return Res[Tuple[K, V], Nil].Nil(str(e))

    @overload
    def update(
        self, m: SupportsKeysAndGetItem[NewK, NewV]
    ) -> DictPlus[K | NewK, V | NewV]:
        ...

    @overload
    def update(self, m: dict[NewK, NewV]) -> DictPlus[K | NewK, V | NewV]:
        ...

    @overload
    def update(self, m: Iterable[tuple[NewK, NewV]]) -> DictPlus[K | NewK, V | NewV]:
        ...

    def update(
        self,
        m: dict[NewK, NewV]
        | SupportsKeysAndGetItem[NewK, NewV]
        | Iterable[tuple[NewK, NewV]],
    ) -> DictPlus[K | NewK, V | NewV]:
        """Updates using keys value pairs from another `dict`

        Args:
            m (dict[NewK, NewV] | SupportsKeysAndGetItem[NewK, NewV] | Iterable[tuple[NewK, NewV]]): A dict or object that supports getitem and setitem

        Returns:
            DictPlus[K | NewK, V | NewV]: The updated dictionary
        """
        super().update(m)  # type: ignore
        return self  # type: ignore

    def put(self, key: NewK, value: NewV) -> DictPlus[K | NewK, V | NewV]:
        """Adds a key value pair

        Args:
            key (NewK): The key for the pairing
            value (NewV): The value for the pairing

        Returns:
            DictPlus[K | NewK, V | NewV]: The updated dictionary
        """
        return self.update({key: value})

    def map(
        self: DictPlus[K, V | NewV], using: Callable[[V], NewV]
    ) -> DictPlus[K, V | NewV]:
        """Runs a function over each value in the dictionary

        Args:
            using (Callable[[V], NewV]): A function that takes an input and returns an output

        Returns:
            DictPlus[K, V | NewV]: The updated dictionary
        """
        for k, v in self.items():
            self[k] = using(cast(V, v))
        return self

    def map_keys(self, using: Callable[[K], NewK]) -> DictPlus[K | NewK, V]:
        """Runs a functino over each key in the dictionary

        Args:
            using (Callable[[K], NewK]): A func that takes a key input and returns an output

        Returns:
            DictPlus[K | NewK, V]: _description_
        """
        cls = type(self)
        return cls.__new__(cls).update({using(k): v for k, v in self.items()})

    def where(self, using: Callable[[K, V], bool]) -> Self:
        """Filters the dictionary using a function that returns a `bool`

        Args:
            using (Callable[[K, V], bool]): A function that takes a key and value and returns True or False

        Returns:
            Self[K, V]: The dictionary where the function was `True`
        """
        for k, v in self.items():
            if not using(k, v):
                self.pop(k)
        return self

    def clear(self) -> Self:
        """Clears all entries from the dictionary

        Returns:
            Self[K, V]: An empty version of the dictionary
        """
        super().clear()
        return self

    def __copy__(self) -> Self:
        return DictPlus(super().copy())  # type: ignore

    def copy(self) -> Self:
        """Deep copies the dictionary

        Returns:
            Self[K, V]: An exact copy of the dictionary
        """
        return self.__copy__()

    @classmethod
    def fromkeys(
        cls: type[DictPlus[NewK, NewV]], iterable: Iterable[NewK], value: NewV
    ) -> DictPlus[NewK, NewV]:
        """Returns a new `DictPlus` with the given keys and default value

        Args:
            iterable (Iterable[NewK]): An iterable filled with the desired keys
            value (NewV): The default value

        Returns:
            DictPlus[NewK, NewV]: A dictionary filled with the keys and default values
        """
        d = super().fromkeys(iterable, value)
        return cls.__new__(cls).update(d)


class StrictDict(DictPlus[K, V]):
    """A subclass of `DictPlus` that enforces static typing on its keys and values.
    Union types are unsupported. Must use the `new` method for initialization.

    ### Example

    Createa typed dict using `new` ::

        >>> d = StrictDict.new(ktype=str, vtype=str).put("hello", "world)

    Constructing without `new` doesn't enforce types

    Setting items that are not the objects declared types raises an Exception

        >>> d.put("ten", 10)
        ValueError

    """

    _ktype: type[K]
    """The key type. Should not be changed except in the `new` method"""
    _vtype: type[V]
    """The value type. Should not be changed except in the `new` method"""

    @property
    def kt(self) -> type[K]:
        """The declared type of the key

        Returns:
            type[K]: The key type
        """
        return self._ktype

    @property
    def vt(self) -> type[V]:
        """The declared type of the values

        Returns:
            type[K]: The value type
        """
        return self._vtype

    @classmethod
    def new(cls, ktype: type[NewK], vtype: type[NewV]) -> StrictDict[NewK, NewV]:
        """Creates a new `StrictDict` with the enforced types

        Args:
            ktype (type[NewK]): The type to enforce for keys
            vtype (type[NewV]): The type to enforce for values

        Returns:
            StrictDict[NewK, NewV]: A new `StrictDict`
        """
        obj = cls.__new__(cls)
        object.__setattr__(obj, "_ktype", ktype)
        object.__setattr__(obj, "_vtype", vtype)
        return cast(StrictDict[NewK, NewV], obj)

    def __setitem__(self, key: K, value: V) -> None:
        if not isinstance(key, self.kt):
            raise ValueError(
                f"Expected key to be {type(self.kt)} but found {type(key)}"
            )

        if not isinstance(value, self.vt):
            raise ValueError(
                f"Expected key to be {type(self.vt)} but found {type(value)}"
            )

        return super().__setitem__(key, value)

    @overload
    def update(self, m: dict[K, V]) -> Self:
        ...

    @overload
    def update(self, m: Iterable[tuple[K, V]]) -> Self:
        ...

    def update(
        self,
        m: dict[K, V] | SupportsKeysAndGetItem[K, V] | Iterable[tuple[K, V]],
    ) -> Self:
        """Updates the dictionary with a new one. Raises `ValueError` on bad types

        Args:
            m (dict[K, V] | SupportsKeysAndGetItem[K, V] | Iterable[tuple[K, V]]): A new dictionary to merge in

        Returns:
            Self[K, V]: The updated dictionary
        """
        super().update(m)
        return self

    def put(self, key: K, value: V) -> Self:
        """Adds a new key value pair. Raises `ValueError` on bad types

        Args:
            key (K): A new key
            value (V): A new value

        Returns:
            Self[K, V]: An updated dictionary

        """
        return self.update({key: value})

    def map(self, using: Callable[[V], NewV]) -> StrictDict[K, NewV]:
        """Uses a function to return a new `StrictDict` with updated values

        Args:
            using (Callable[[V], NewV]): A func that takes a value and returns an output

        Returns:
            StrictDict[K, NewV]: A new dictionary
        """
        first, *rest = self.items()
        key, value = first
        new_vtype = type(using(value))
        obj = self.new(self.kt, new_vtype)
        for key, value in [(key, value)] + rest:
            obj[key] = using(value)
        return obj

    def map_keys(self, using: Callable[[K], NewK]) -> StrictDict[NewK, V]:
        """Uses a function to return a new `StrictDict` with updated keys

        Args:
            using (Callable[[K], NewK]): A funct that takes a key and returns a new key

        Returns:
            StrictDict[NewK, V]: A new dictionary
        """
        first, *rest = self.items()
        key, value = first
        new_ktype = type(using(key))
        obj = self.new(new_ktype, self.vt)
        for key, value in [(key, value)] + rest:
            obj[using(key)] = value
        return obj

    @classmethod
    def fromkeys(cls, iterable: Iterable[NewK], value: NewV) -> StrictDict[NewK, NewV]:
        """Creates a new dictionary using an iterable of keys and a default value

        Args:
            iterable (Iterable[NewK]): An iterable of desired keys
            value (NewV): A default value

        Returns:
            StrictDict[NewK, NewV]: A new dictionary
        """
        first, *rest = iterable
        ktype = type(first)
        vtype = type(value)
        obj = cls.__new__(cls).new(ktype, vtype)
        return obj.update(dict.fromkeys(iterable, value))
