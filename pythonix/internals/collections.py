"""Advanced versions of `list`, `tuple`, `dict`, and `deque` with builtin mapping, filtering, and folding"""

from __future__ import annotations
from abc import ABC
from copy import deepcopy
from collections.abc import Iterator, Set as AbstractSet
from functools import reduce
from typing import (
    Generic,
    List,
    cast,
    TypeVar,
    Callable,
    Tuple,
    Iterable,
    SupportsIndex,
    Protocol,
)
from typing_extensions import Self
from collections import deque
from dataclasses import dataclass, field
from pythonix.internals.res import Res, Nil, catch_all, null_and_error_safe
from pythonix.internals.utils import unwrap
from pythonix.internals.traits import Collad, MapAlt, Unwrap, Ad, UnwrapAlt, Map, Where


_KT = TypeVar("_KT")
_VT_co = TypeVar("_VT_co", covariant=True)
T_co = TypeVar("T_co", covariant=True)
T_con = TypeVar("T_con", contravariant=True)
E = TypeVar("E", bound="Exception")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")
K = TypeVar("K")
L = TypeVar("L")
_S = TypeVar("_S")
NewK = TypeVar("NewK")
NewV = TypeVar("NewV")


class SupportsKeysAndGetItem(Protocol[_KT, _VT_co]):
    def keys(self) -> Iterable[_KT]: ...

    def __getitem__(self, key: _KT, /) -> _VT_co: ...


class SupportsSafeGetItem(Protocol[T_co]):  # type: ignore

    def __getitem__(self, key: SupportsIndex) -> Res[T_co, Nil]: ...

    def get(self, key: SupportsIndex) -> Res[T_co, Nil]: ...


class Step(ABC, Generic[T, U]):
    op: Callable
    __match_args__ = ("op",)


@dataclass(frozen=True, match_args=True)
class Bind(Step[T, U]):
    op: Callable[[T], U]


@dataclass(frozen=True, match_args=True)
class Filter(Step[T, T]):
    op: Callable[[T], bool]


@dataclass(frozen=True, eq=True, match_args=True, repr=True)
class Zad(Map[T], Where, Generic[T, U]):

    data: Iterable[T] = tuple()
    steps: deque[Step] = field(default_factory=deque)

    def __new__(cls, data: Iterable[T]) -> Zad[T, T]:
        obj = object.__new__(cls)
        object.__setattr__(obj, "data", data)
        object.__setattr__(obj, "steps", deque())
        return cast(Zad[T, T], obj)

    def __rshift__(self, using: Callable[[U], V]) -> Zad[T, V]:
        return self.map(using)

    def __irshift__(self, using: Callable[[U], V]) -> Zad[T, V]:
        return self.map(using)

    def map(self, using: Callable[[U], V]) -> Zad[T, V]:
        self.steps.append(Bind(using))
        return cast(Zad[T, V], self)

    def __floordiv__(self, predicate: Callable[[U], bool]) -> Zad[T, U]:
        return self.where(predicate)

    def __ifloordiv__(self, predicate: Callable[[U], bool]) -> Zad[T, U]:
        return self.where(predicate)

    def where(self, predicate: Callable[[U], bool]) -> Zad[T, U]:
        self.steps.append(Filter(predicate))
        return cast(Zad[T, U], self)

    def __iter__(self) -> Iterator[U]:

        for element in self.data:
            out = deepcopy(element)
            for step in self.steps:
                match step:
                    case Bind(op):
                        out = op(out)
                    case Filter(predicate):
                        if predicate(out):
                            continue
            yield cast(U, out)


@dataclass(frozen=True, eq=True, init=True, match_args=True, order=True, repr=True)
class Pair(Tuple[K, T], Ad[T], Unwrap[T], MapAlt[T], UnwrapAlt[K]):
    """Wrapper for tuple key value pair with additional features and type safety

    Args:
        key (K): Key for the value
        inner (T): The value

    #### Notable Features ::

        >>> p = Pair("foo", 10)
        >>> p >>= str                   # Change value to str
        >>> p ^= lambda k: k + " bar"   # Add bar to key
        >>> k, v = p                    # Unpack like a tuple
        >>> p[0]                        # Access elements like a tuple
        'foo bar'
        >>> match p:                    # Pattern match easily
        ...     case Pair(k, v):
        ...         v
        10

    """

    key: K
    """Key associated with this value"""
    inner: T
    """Wrapped value"""

    def __irshift__(self, using: Callable[[T], U]) -> Pair[K, U]:
        return self.map(using)

    def __rshift__(self, using: Callable[[T], U]) -> Pair[K, U]:
        return self.map(using)

    def map(self, using: Callable[[T], U]) -> Pair[K, U]:
        """Transform wrapped value with function

        Args:
            using ((T) -> U): Func that takes inner value and returns an output

        Returns:
            Pair[K, U]: Transformed Pair
        """
        return Pair(self.key, using(self.inner))

    def __ixor__(self, using: Callable[[K], L]) -> Pair[L, T]:
        return self.map_alt(using)

    def __xor__(self, using: Callable[[K], L]) -> Pair[L, T]:
        return self.map_alt(using)

    def map_alt(self, using: Callable[[K], L]) -> Pair[L, T]:
        """Transform key value with function

        Args:
            using ((K) -> L): Function to take `key` and return a new key

        Returns:
            Pair[L, T]: Updated Pair
        """
        return Pair(using(self.key), self.inner)

    def unwrap_alt(self) -> K:
        """Returns key value

        Returns:
            K: Key value
        """
        return self.key

    def unwrap(self) -> T:
        """Returns inner value

        Returns:
            T: inner value
        """
        return self.inner


class Set(set[T], Collad[T]):
    """Upgraded version of `set` with builtin `map`, `where`, `fold`, and `apply` operators.

    NOTE:
        Using different operators in a chain can sometimes break type checking. For operations with multiple
        operators use the methods or inplace operators.

    ### Mappings
        - `>>` `>>=` and `map()` run functions over contained values
        - `//` `//=` and `where()` filter contained values
        - `**` `**=` and `fold()` apply folding functions over contained values
        - `<<` `<<=` and `apply()` run a function over the container itself

    ### Examples

    #### With Inplace operations ::

        >>> s = Set([15, 20, 30, 40])
        >>> s >>= lambda x: x * 2
        >>> s //= lambda x: x % 3 == 0
        >>> s **= lambda x, y: x + y
        >>> s <<= unwrap
        >>> s
        90

    #### With Operators ::

        >>> s = Set([15, 20, 30, 40])
        >>> s = s >> lambda x: x * 2
        >>> s = s // lambda x: x % 3 == 0
        >>> s = s ** lambda x, y: x + y
        >>> s << unwrap
        90

    #### With Methods ::

        >>> l = Set([15, 20, 30, 40])
        >>> l.map(lambda x: x * 2).where(lambda x: x % 3 == 0).fold(lambda x, y: x + y).unwrap()
        90

    """

    def __iter__(self) -> Iterator[T]:
        return super().__iter__()

    def __iand__(self, value: AbstractSet[object]) -> Self:
        return super().__iand__(value)

    def __and__(self, value: AbstractSet[object]) -> Set[T]:
        return Set(super().__and__(value))

    def __ior__(self, value: AbstractSet[T]) -> Self:
        return super().__ior__(value)

    def __or__(self, value: AbstractSet[_S]) -> Set[T | _S]:
        return Set(super().__or__(value))

    def __isub__(self, value: AbstractSet[object]) -> Self:
        return super().__isub__(value)

    def __sub__(self, value: AbstractSet[T | None]) -> Set[T]:
        return Set(super().__sub__(value))

    def __ixor__(self, value: AbstractSet[T]) -> Self:
        return super().__ixor__(value)

    def __xor__(self, value: AbstractSet[_S]) -> Set[T | _S]:
        return Set(super().__xor__(value))

    def __irshift__(self, using: Callable[[T], U]) -> Set[U]:
        return self.map(using)

    def __rshift__(self, using: Callable[[T], U]) -> Set[U]:
        return self.map(using)

    def map(self, using: Callable[[T], U]) -> Set[U]:
        """Runs function over each element and keeps the results. Maps to `>>` and `>>=`

        Args:
            using ((T) -> U): Function that takes an element and returns an output

        Returns:
            Set[U]: Updated Set
        """
        return Set(using(t) for t in self)

    def where(self, predicate: Callable[[T], bool]) -> Set[T]:
        """Filters elements using `predicate`, keeping whichever return True. Maps to `//` and `//=`.

        Args:
            predicate ((T) -> bool): Filter function that returns True or False

        Returns:
            Set[T]: Updated Set
        """
        return Set((t for t in self if predicate(t)))

    def fold(self, using: Callable[[T, T], T]) -> T:
        """Folds a function over the elements, returning its final result. Maps to `**` and `**=`

        Args:
            using ((T, T) -> T): Function that takes a pair of elements and returns a result

        Returns:
            T: The final result
        """
        return reduce(using, self)

    def pop(self) -> Res[T, Nil]:
        """Returns the left most element

        Returns:
            Res[T, Nil]: Element wrapped in Res
        """
        try:
            return Res.Some(super().pop())
        except KeyError:
            return Res.Nil()

    def add(self, element: T) -> Set[T]:
        """Adds an element to the set

        Args:
            element (T): The element to be added

        Returns:
            Set[T]: The initial Set
        """
        super().add(element)
        return self


class Listad(List[T], Collad[T]):
    """Upgraded version of `list` with builtin `map`, `where`, `fold`, and `apply` operators.

    NOTE:
        Using different operators in a chain can sometimes break type checking. For operations with multiple
        operators use the methods or inplace operators.

    ### Mappings
        - `>>` `>>=` and `map()` run functions over contained values
        - `//` `//=` and `where()` filter contained values
        - `**` `**=` and `fold()` apply folding functions over contained values
        - `<<` `<<=` and `apply()` run a function over the Listad itself

    ### Examples

    #### With Inplace operations ::

        >>> l = Listad([15, 20, 30, 40])
        >>> l >>= lambda x: x * 2
        >>> l //= lambda x: x % 3 == 0
        >>> l **= lambda x, y: x + y
        >>> l
        90

    #### With Operators ::

        >>> l = Listad([15, 20, 30, 40])
        >>> l = l >> lambda x: x * 2
        >>> l = l // lambda x: x % 3 == 0
        >>> l = l ** lambda x, y: x + y
        >>> l
        90

    #### With Methods ::

        >>> l = Listad([15, 20, 30, 40])
        >>> l.map(lambda x: x * 2).where(lambda x: x % 3 == 0).fold(lambda x, y: x + y)
        90

    """

    def __iter__(self) -> Iterator[T]:
        return super().__iter__()

    def __iadd__(self, value: Iterable[T]) -> Self:
        return super().__iadd__(value)

    def __add__(self, value: Iterable[_S]) -> Listad[T | _S]:
        return Listad(super().__add__(value))  # type: ignore

    def __irshift__(self, using: Callable[[T], U]) -> Listad[U]:
        return self.map(using)

    def __rshift__(self, using: Callable[[T], U]) -> Listad[U]:
        return self.map(using)

    def copy(self) -> Listad[T]:
        return Listad(super().copy())

    def map(self, using: Callable[[T], U]) -> Listad[U]:
        """Runs `using` over each element, returning a new Listad. Uses `>>` and `>>=`.

        Args:
            using ((T) -> U): Func to run over each element.

        Returns:
            Listad[U]: Updated Listad

        #### Examples ::

            >>> l = Listad([10, 20, 30])
            >>> l >>= lambda x: x * 2
            >>> first, *_ = l
            >>> first
            20
        """
        return Listad(using(elem) for elem in self)

    def __ifloordiv__(self, predicate: Callable[[T], bool]) -> Listad[T]:
        return self.where(predicate)

    def __floordiv__(self, predicate: Callable[[T], bool]) -> Listad[T]:
        return self.where(predicate)

    def where(self, predicate: Callable[[T], bool]) -> Listad[T]:
        """Filters elements using `predicate` that return True. Uses `//` and `//=`.

        Args:
            predicate ((T) -> bool): Func to test an element and return True or False

        Returns:
            Listad[T]: Updated Listad

        #### Examples ::

            >>> l = Listad([10, 20, 30])
            >>> l //= lambda x: x % 3 == 0
            >>> l[0]
            30
        """
        return Listad(elem for elem in self if predicate(elem))

    def fold(self, using: Callable[[T, T], T]) -> T:
        """Runs `using` over each pair of elements, returning final result. Uses `**` and `**=`.

        Args:
            using (Callable[[T, T], T]): Func that uses pairs of elements to return a final value

        Returns:
            T: Final value

        #### Examples ::

            >>> l = Listad([10, 20, 30])
            >>> l **= lambda x, y: x + y
            >>> l
            60
        """
        return reduce(using, self)

    def __ilshift__(self: Self, using: Callable[[Self], U]) -> U:
        return self.apply(using)

    def __lshift__(self: Self, using: Callable[[Self], U]) -> U:
        return self.apply(using)

    def apply(self, using: Callable[[Self], U]) -> U:
        """Runs function over whole value, returning result. Uses `<<` and `<<=`.

        Args:
            using ((Self) -> U): Func that takes Self, and returns a value

        Returns:
            U: Returned value from `using`

        #### Examples ::

            >>> l = Listad([10, 20, 30])
            >>> l <<= sum
            >>> l
            60
        """
        return using(self)

    def __getitem__(self, key: SupportsIndex) -> Res[T, Nil]:
        try:
            return Res.Some(super().__getitem__(key))
        except (IndexError, KeyError) as e:
            return Res[T, Nil].Nil(str(e))

    def get(self, index: SupportsIndex) -> Res[T, Nil]:
        """Retrieves a value as an `Res[T, Nil]` at a given index

        Args:
            index (SupportsIndex): Index of the desired value, or slice

        Returns:
            Res[T, Nil]: The retrieved value as an Opt[T]. Must be handled.
        """
        return self[index]

    @null_and_error_safe(IndexError)
    def pop(self, index: SupportsIndex = -1) -> T:
        """Retrieves and removes an element from the Litad

        Args:
            index (SupportsIndex, optional): Index of the item to be popped out. Defaults to -1.

        Returns:
            Res[T, Nil]: Res containing the popped value
        """
        return super().pop(index)


def flatten(iterable: Iterable[Iterable[T]]) -> Iterable[T]:
    """Flattens nested iterable

    Args:
        iterable (Iterable[Iterable[T]]): Nested iterable

    Returns:
        Iterable[T]: Unnested iterable
    """
    return (elem for niter in iterable for elem in niter)


def separate(iter_res: Iterable[Res[T, E]]) -> tuple[Listad[T], Listad[E]]:
    """Convenience func to separate Ok and Err into separate Listads

    Args:
        iter_res (Iterable[Res[T, E]]): Iterable full of Res[T, E]

    Returns:
        tuple[Listad[T], Listad[E]]: pair of Listads with Ok or Err values respectively

    #### Examples ::

        >>> results = Listad([Res.Some(10), Res.Some(10), Res.Nil()])
        >>> oks, errs = results << separate
        >>> oks >>= str
        >>> oks << print
        ['10', '10']
    """
    oks = Listad(res.q for res in iter_res if res)
    errs = Listad(res.e for res in iter_res if not res)
    return oks, errs


class Tuplad(Tuple[T], Collad[T]):
    """Upgraded version of `tuple` with builtin `map`, `where`, `fold`, and `apply` operators.

    NOTE:
        Using different operators in a chain can sometimes break type checking. For operations with multiple
        operators use the methods or inplace operators.

    ### Mappings
        - `>>` `>>=` and `map()` run functions over contained values
        - `//` `//=` and `where()` filter contained values
        - `**` `**=` and `fold()` apply folding functions over contained values
        - `<<` `<<=` and `apply()` run a function over the Listad itself

    ### Examples

    #### With Inplace operations ::

        >>> t = Tuplad([15, 20, 30, 40])
        >>> t >>= lambda x: x * 2
        >>> t //= lambda x: x % 3 == 0
        >>> t **= lambda x, y: x + y
        >>> t <<= unwrap
        >>> t
        90

    #### With Operators ::

        >>> t = Tuplad([15, 20, 30, 40])
        >>> t = t >> lambda x: x * 2
        >>> t = t // lambda x: x % 3 == 0
        >>> t = t ** lambda x, y: x + y
        >>> t << unwrap
        >>> t
        90

    #### With Methods ::

        >>> t = Tuplad([15, 20, 30, 40])
        >>> t.map(lambda x: x * 2).where(lambda x: x % 3 == 0).fold(lambda x, y: x + y).unwrap()
        90

    """

    def __iter__(self) -> Iterator[T]:
        return super().__iter__()

    def __irshift__(self, using: Callable[[T], U]) -> Tuplad[U]:
        return self.map(using)

    def __rshift__(self, using: Callable[[T], U]) -> Tuplad[U]:
        return self.map(using)

    def map(self, using: Callable[[T], U]) -> Tuplad[U]:
        """Runs `using` over each element, returning a new Tuplad. Uses `>>` and `>>=`.

        Args:
            using ((T) -> U): Func to run over each element.

        Returns:
            Tuplad[U]: Updated Listad

        #### Examples ::

            >>> l = Tuplad([10, 20, 30])
            >>> l >>= lambda x: x * 2
            >>> first, *_ = l
            >>> first
            20
        """
        return Tuplad(using(elem) for elem in self)

    def __ifloordiv__(self, predicate: Callable[[T], bool]) -> Tuplad[T]:
        return self.where(predicate)

    def __floordiv__(self, predicate: Callable[[T], bool]) -> Tuplad[T]:
        return self.where(predicate)

    def where(self, predicate: Callable[[T], bool]) -> Tuplad[T]:
        """Filters elements using `predicate` that return True. Uses `//` and `//=`.

        Args:
            predicate ((T) -> bool): Func to test an element and return True or False

        Returns:
            Tuplad[T]: Updated Listad

        #### Examples ::

            >>> l = Listad([10, 20, 30])
            >>> l //= lambda x: x % 3 == 0
            >>> l[0]
            30
        """
        return Tuplad(elem for elem in self if predicate(elem))

    def fold(self, using: Callable[[T, T], T]) -> T:
        """Runs `using` over each pair of elements, returning final result. Uses `**` and `**=`.

        Args:
            using ((T, T) -> T): Func that uses pairs of elements to return a final value

        Returns:
            T: Final value

        #### Examples ::

            >>> l = Tuplad([10, 20, 30])
            >>> l **= lambda x, y: x + y
            >>> l
            60
        """
        return reduce(using, self)

    def __ilshift__(self: Self, using: Callable[[Self], U]) -> U:
        return self.apply(using)

    def __lshift__(self: Self, using: Callable[[Self], U]) -> U:
        return self.apply(using)

    def apply(self, using: Callable[[Self], U]) -> U:
        """Runs function over whole value, returning result. Uses `<<` and `<<=`.

        Args:
            using ((Self) -> U): Func that takes Self, and returns a value

        Returns:
            U: Returned value from `using`

        #### Examples ::

            >>> l = Tuplad([10, 20, 30])
            >>> l <<= sum
            >>> l
            60
        """
        return using(self)

    def __getitem__(self, key: SupportsIndex) -> Res[T, Nil]:
        try:
            return Res.Some(super().__getitem__(key))
        except (IndexError, KeyError) as e:
            return Res[T, Nil].Nil(str(e))

    def get(self, index: SupportsIndex) -> Res[T, Nil]:
        """Retrieves a value as an `Res[T, Nil]` at a given index

        Args:
            index (SupportsIndex): Index of the desired value, or slice

        Returns:
            Res[T, Nil]: The retrieved value as an Opt[T]. Must be handled.
        """
        return self[index]

    def __iadd__(self, value: tuple[_S] | Tuplad[_S]) -> Tuplad[T | _S]:
        return Tuplad(super().__add__(value))

    def __add__(self, value: tuple[_S] | Tuplad[_S]) -> Tuplad[T | _S]:
        return Tuplad(super().__add__(value))


class Dictad(dict[K, T], Collad[T], MapAlt[K]):
    """Upgraded version of `dict` with builtin `map`, `where`, `fold`, and `apply` operators.

    NOTE:
        Using different operators in a chain can sometimes break type checking. For operations with multiple
        operators use the methods or inplace operators.

    ### Mappings
        - `>>` `>>=` and `map()` run functions over contained values
        - `//` `//=` and `where()` filter contained values
        - `**` `**=` and `fold()` apply folding functions over contained values
        - `<<` `<<=` and `apply()` run a function over the container itself

    ### Examples

    #### With Inplace operations ::

        >>> d = Dictad({"foo": 10})
        >>> d >>= lambda x: x + 10
        >>> d ^= lambda k: k + "lish"
        >>> d |= {"bar": 20}
        >>> d |= {"baz": 30}
        >>> d //= lambda k, v: v != 30
        >>> d **= lambda l, r: l + r
        >>> d <<= unwrap
        40

    #### With Operators ::

        >>> d = Dictad({"foo": 10})
        >>> d = d >> lambda x: x + 10
        >>> d = d ^ lambda k: k + "lish"
        >>> d = d | {"bar": 20}
        >>> d = d | {"baz": 30}
        >>> d = d // lambda k, v: v != 30
        >>> d = d ** lambda l, r: l + r
        >>> d << unwrap
        40

    #### With Methods ::

        >>> d = Dictad({"foo": 10})
        >>> d = d.map(lambda x: x + 10).map_alt(lambda k: x + "lish")
        >>> d["bar"] = 20
        >>> d["baz"] = 30
        >>> d.where(lambda k, v: v != 30).fold(lambda l, r: l + r).unwrap()
        40

    """

    def __irshift__(self, using: Callable[[T], U]) -> Dictad[K, U]:
        return self.map(using)

    def __rshift__(self, using: Callable[[T], U]) -> Dictad[K, U]:
        return self.map(using)

    def map(self, using: Callable[[T], U]) -> Dictad[K, U]:
        """Run a function over contained values, returning an updated version. Maps to `>>` and `>>=`.

        Args:
            using ((T) -> U): Function that takes a value and returns another

        Returns:
            Dictad[K, U]: Updated Dictad
        """
        return Dictad({k: using(t) for k, t in self.items()})  # type: ignore

    def __ipow__(self, using: Callable[[T, T], T]) -> Res[T, Exception]:
        return self.fold(using)

    def __pow__(self, using: Callable[[T, T], T]) -> Res[T, Exception]:
        return self.fold(using)

    @catch_all
    def fold(self, using: Callable[[T, T], T]) -> T:
        """Folds a function over pairs of elements, returning the final result. Maps to `**` and `**=`.

        Args:
            using ((T, T) -> T): Function that takes two arguments and returns one.

        Returns:
            Res[T, Exception]: Final result of the fold
        """
        return reduce(using, self.values())

    def apply(self, using: Callable[[Self], U]) -> U:
        """Runs function over whole value, returning result. Uses `<<` and `<<=`.

        Args:
            using ((Self) -> U): Func that takes Self, and returns a value

        Returns:
            U: Returned value from `using`

        #### Examples ::

            >>> l = Tuplad([10, 20, 30])
            >>> l <<= sum
            >>> l
            60
        """
        return using(self)

    def __xor__(self, using: Callable[[K], L]) -> Dictad[L, T]:
        return self.map_alt(using)

    def __ixor__(self, using: Callable[[K], L]) -> Dictad[L, T]:
        return self.map_alt(using)

    def map_alt(self, using: Callable[[K], L]) -> Dictad[L, T]:
        """Run a function over contained keys, returning an updated version. Maps to `^ and `^=`

        Args:
            using ((K) -> L): Function that takes a key and returns another

        Returns:
            Dictad[L, T]: Updated Dictad
        """
        return Dictad({using(k): v for k, v in self.items()})  # type: ignore

    def __ifloordiv__(self, predicate: Callable[[K, T], bool]) -> Dictad[K, T]:
        return self.where(predicate)

    def __floordiv__(self, predicate: Callable[[K, T], bool]) -> Dictad[K, T]:
        return self.where(predicate)

    def where(self, predicate: Callable[[K, T], bool]) -> Dictad[K, T]:
        """Filters over keys and values, retaining True values. Maps to `//` and `//=`

        Args:
            predicate ((K, T) -> bool): Function that takes a key and value, and returns True

        Returns:
            Dictad[K, T]: Updated Dictad
        """
        return Dictad({k: v for k, v in self.items() if predicate(k, v)})  # type: ignore

    def __getitem__(self, key: K) -> Res[T, Nil]:
        try:
            return Res.Some(super().__getitem__(key))
        except (IndexError, KeyError) as e:
            return Res[T, Nil].Nil(str(e))

    def get(self, key: K) -> Res[T, Nil]:
        """Retrieves a value as an `Res[T, Nil]` at a given index

        Args:
            key (K): Immutable key

        Returns:
            Res[T, Nil]: The retrieved value as an Res[T, Nil]. Must be handled.
        """
        return self[key]

    def pop(self, key: K) -> Res[T, Nil]:
        """Returns a value and removes it from the `dict`

        Args:
            key (K): The key for the item desired

        Returns:
            Opt[V]: The desired item wrapped in an `Opt`
        """
        try:
            return Res.Some(super().pop(key))
        except (KeyError, IndexError) as e:
            return Res[T, Nil].Nil(str(e))

    def popitem(self) -> Res[Tuple[K, T], Nil]:
        """Removes and returns the farthest right key value tuple

        Returns:
            Opt[Tuple[K | V]]: The farthest right key value tuple or Nil
        """
        try:
            return Res.Some(super().popitem())
        except (KeyError, IndexError) as e:
            return Res[Tuple[K, T], Nil].Nil(str(e))

    def __ior__(self, other: dict[L, U]) -> Dictad[K | L, T | U]:
        return Dictad(dict.__or__(self, other))

    def __or__(self, other: dict[L, U]) -> Dictad[K | L, T | U]:
        return Dictad(dict.__or__(self, other))

    def copy(self) -> Dictad[K, T]:
        """Shallow copies the Dictad and returns it"""
        return Dictad(super().copy())

    @staticmethod
    def fromkeys(keys: Iterable[K], value: T) -> Dictad[K, T]:
        return Dictad(dict.fromkeys(keys, value))

    def __iter__(self) -> Iterator[K]:
        return super().__iter__()


class Deq(deque[T], Collad[T]):
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

    def __irshift__(self, using: Callable[[T], U]) -> Deq[U]:
        return self.map(using)

    def __rshift__(self, using: Callable[[T], U]):
        return self.map(using)

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

    @catch_all
    def fold(self, using: Callable[[T, T], T]) -> T:
        return reduce(using, self)

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
