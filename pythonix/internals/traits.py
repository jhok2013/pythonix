"""Base and concrete classes for shared mapping, filter, and other behavior."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import (
    TypeVar,
    Callable,
    Generic,
    Protocol,
    SupportsIndex,
    Iterator,
    runtime_checkable,
    Any,
)
from typing_extensions import Self

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
U = TypeVar("U")
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")


class Map(Generic[T], ABC):
    """Defines behavior for `map`, `>>` and `>>=`"""

    @abstractmethod
    def __irshift__(self, using: Callable[[T], U]):
        return self.map(using)

    @abstractmethod
    def __rshift__(self, using: Callable[[T], U]):
        return self.map(using)

    @abstractmethod
    def map(self, using: Callable[[T], U]) -> Map[U]:
        """Transforms inner value and returns updated instance of self"""
        ...


class Unwrap(Generic[T], ABC):
    """Base class for classes that wrap a value and need to perform a side effect while unwrapping it"""

    @abstractmethod
    def unwrap(self) -> T: ...

    @property
    def q(self) -> T:
        """Shorthand for unwrap"""
        return self.unwrap()


class UnwrapAlt(Generic[T], ABC):
    """Base class for classes that wrap a second value and need to perform a side effect while unwrapping it"""

    @abstractmethod
    def unwrap_alt(self) -> T: ...

    @property
    def e(self) -> T:
        """Shorthand for unwrap_alt"""
        return self.unwrap_alt()


class MapAlt(Generic[T], ABC):
    """Defines behavior for `map_alt`, `^` and `^=`"""

    @abstractmethod
    def __ixor__(self, using: Callable[[T], U]):
        return self.map_alt(using)

    @abstractmethod
    def __xor__(self, using: Callable[[T], U]):
        return self.map_alt(using)

    @abstractmethod
    def map_alt(self, using: Callable[[T], U]):
        """Transforms alternate inner value and returns updated instance of self"""
        ...


class Apply:
    """Concrete class that allows for applying a function to itself with `apply`, `<<`, and `<<=`"""

    def __ilshift__(self, using: Callable[[Self], U]) -> U:
        return self.apply(using)

    def __lshift__(self, using: Callable[[Self], U]) -> U:
        return self.apply(using)

    def apply(self, using: Callable[[Self], U]) -> U:
        """Applies function to self and returns result. Useful for terminating chains

        Args:
            using (Callable[[Self], U]): Function that takes self and returns a value

        Returns:
            U: Any value returned by the function

        #### Example ::

            >>> x = Apply() # Could be any class that inherits Apply
            >>> x.apply(lambda _: 10)
            10
            >>> x << lambda _: 10
            10
            >>> x <<= lambda _: 10
            >>> x
            10

        """
        return using(self)


class Where(ABC):
    """Defines behavior for filtering data on self with `where`, `//` and `//=`"""

    def __ifloordiv__(self, predicate: Callable[[T], bool]) -> Self:
        return self.where(predicate)

    def __floordiv__(self, predicate: Callable[[T], bool]) -> Self:
        return self.where(predicate)

    @abstractmethod
    def where(self, predicate: Callable[[T], bool]) -> Self: ...


class Fold(Generic[T], ABC):
    """Defines behavior for folding inner data using `fold`, `**`, and `**=`"""

    def __ipow__(self, using: Callable[[T, T], T]) -> T:
        return self.fold(using)

    def __pow__(self, using: Callable[[T, T], T]) -> T:
        return self.fold(using)

    @abstractmethod
    def fold(self, using: Callable[[T, T], T]) -> T: ...


class Ad(Map[T], Apply):
    """Defines behavior for a class to transform itself with `map`, and `apply`"""

    ...


class Collad(Ad[T], Where, Fold[T]):
    """Defines behavior for an `Iterable[T]` class to map and filter itself"""

    @abstractmethod
    def __iter__(self) -> Iterator[T]: ...


class SupportsGetItem(Protocol[T_co]):

    def __getitem__(self, key: SupportsIndex) -> T_co: ...

    def get(self, key: SupportsIndex) -> T_co: ...


@runtime_checkable
class Colladic(Protocol[T]):

    def fold(self, using: Callable[[T, T], T]) -> T: ...

    def where(self, predicate: Callable[[T], bool]) -> Self: ...

    def map(self, using: Callable) -> Any: ...

    def apply(self, using: Callable[[Self], U]) -> U: ...

    def __iter__(self) -> Iterator[T]: ...
