from __future__ import annotations
from typing import Generic, TypeVar, Callable, TypeAlias
from dataclasses import dataclass, field

T = TypeVar("T")
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


class UnwrapError(Exception):
    """Exception used for when a `Res` is unwrapped while in an error state"""

    def __init__(self, message: str = 'Unwrapped while in an Err state'):
        super().__init__(self, message)

class ExpectError(Exception):
    """Exception used for when a `Res` is unwrapped with `expect`"""

    def __init__(self, message: str):
        super().__init__(self, message)

class Nil(Exception):
    """Exception used for when a `Res` is None while expecting something"""

    def __init__(self, message: str = 'Found None while expecting something'):
        super().__init__(self, message)

@dataclass(frozen=True, init=False, eq=True)
class Res(Generic[T, E], object):
    """Container used for capturing the outcome of something that could fail.

    Use the factory methods `Ok`, `Err`, or `Some` as needed.
    
    Attributes:
        inner (T | E): The wrapped value, could be an Exception.
    
    """

    inner: T | E
    """The wrapped value, could be an Exception"""
    _is_err: bool = field(repr=False)
    """Whether the `Res` is an Exception. Only set on creation."""

    __match_args__ = ("inner",)

    @classmethod
    def Ok(cls, value: U, other_type: type[F]) -> Res[U, F]:
        """Creates a `Res` in an `Ok` state.

        Args:
            value (U): The value to be wrapped
            other_type (type[F]): An Exception type if it were `Err`

        Returns:
            Res[U, F]: The new `Res` in an `Ok` state
        """
        obj = object.__new__(cls)
        object.__setattr__(obj, 'inner', value)
        object.__setattr__(obj, '_is_err', False)
        return obj
    
    @classmethod
    def Err(cls, value: F, other_type: type[U]) -> Res[U, F]:
        """Creates a `Res` in an `Err` state

        Args:
            value (F): The captured Exception to be wrapped
            other_type (type[U]): The type if it were `Ok`k

        Raises:
            TypeError: Raised if the value is not bound to `Exception`

        Returns:
            Res[U, F]: The new `Res` in an `Err` state
        """
        obj = object.__new__(cls)
        if not isinstance(value, Exception):
            raise TypeError(f"Expected subclass of Exception but found {value}")
        object.__setattr__(obj, 'inner', value)
        object.__setattr__(obj, '_is_err', True)
        return obj
    
    @classmethod
    def Some(cls, value: U | None) -> Opt[U]:
        """Creates an `Opt[U]`, checking for None

        Args:
            value (U | None): Value that could be None

        Returns:
            Opt[U]: A new `Res` that has checked for None
        """
        if value is None:
            return Res.Err(Nil(), U)
        return Res.Ok(value, Nil)
    
    def unpack(self) -> tuple[T | None, U | None]:
        """Unpacks the `Res` a la Go for quick checking if desired

        Returns:
            Tuple[T | None, U | None]: The results as a tuple
        """
        match self._is_left:
            case True:
                return self._left, None
            case False:
                return None, self._right
    
    def some(self) -> Opt[T]:
        """Converts the `Res` to an `Opt`, consuming the `E` value

        Returns:
            Opt[T]: The new `Opt`
        """
        if self.is_err() or self.inner is None:
            return Res.Err(Nil(), T)
        return Res.Ok(self.inner, E)
    
    def is_err(self) -> bool:
        """Indicates if the `Res` is in err state

        Returns:
            bool: True if in Err, False if Ok
        """
        return self._is_err
    
    def is_ok(self) -> bool:
        """Indicates if the `Res` is in Ok state

        Returns:
            bool: True if Ok, False if Err
        """
        return not self._is_err
    
    def is_err_and(self, predicate: Callable[[E], bool]) -> bool:
        """Runs the predicate on the wrapped value if Err

        Args:
            predicate (Callable[[E], bool]): Func taking `inner` and returns `bool`

        Returns:
            bool: If state is Err and predicate returns True then True
        """
        if self.is_err():
            return predicate(self.inner)
        return False

    def is_ok_and(self, predicate: Callable[[T], bool]) -> bool:
        """Runs the predicate on the wrapped value if Ok

        Args:
            predicate (Callable[[T], bool]): Func taking `inner` and returns `bool`

        Returns:
            bool: If state is Ok and predicate returns True then True
        """
        if self.is_ok():
            return predicate(self.inner)
        return False
    
    def unwrap(self) -> T:
        """Returns wrapped value, or panics if Err

        Raises:
            UnwrapError: Expected Ok state but found Err

        Returns:
            T: Returns wrapped value if Ok
        """
        if not self.is_err():
            return self.inner
        raise UnwrapError()
    
    def unwrap_err(self) -> E:
        """Returns wrapped Exception if Err, else panics

        Raises:
            UnwrapError: Expected Err state but found Ok

        Returns:
            E: Returns wrapped Exception if Err
        """
        if self.is_err():
            return self.inner
        raise UnwrapError()
    
    def unwrap_or(self, default: T) -> T:
        """Returns wrapped value or default

        Args:
            default (T): Default value for when Err

        Returns:
            T: Wrapped value if Ok else default
        """
        if self.is_err():
            return default
        return self.inner
    
    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        """Returns wrapped value or runs default

        Args:
            default (Callable[[], T]): Default func for when Err

        Returns:
            T: Wrapped value if Ok else output from default
        """
        if self.is_err():
            return default()
        return self.inner
    
    def expect(self, message: str) -> T:
        """Returns `inner` else raises ExpectError with custom message

        Args:
            message (str): Custom error message

        Raises:
            ExpectError: Raised if Err, but with custom error message

        Returns:
            T: Inner value if Ok
        """
        if self.is_err():
            raise ExpectError(message)
        return self.inner
    
    def expect_err(self, message: str) -> E:
        """Returns wrapped Exception if Err else panics with ExpectError

        Args:
            message (str): Custom error message for if it panics

        Raises:
            ExpectError: Raised if Ok with custom error message

        Returns:
            E: Exception if Err
        """
        if self.is_err():
            return self.inner
        raise ExpectError(message)
    
    def map(self, using: Callable[[T], U]) -> Res[U, E]:
        """Changes inner if Ok with a function

        Args:
            using (Callable[[T], U]): Func taking `inner` and returns something else

        Returns:
            Res[U, E]: Transformed `Res` if Ok
        """
        if self.is_err():
            return Res.Err(self.inner, T)
        return Res.Ok(using(self.inner), E)
    
    def map_or(self, using: Callable[[T], U], default: U) -> Res[U, E]:
        """Changes inner if Ok or uses default if Err

        Args:
            using (Callable[[T], U]): Func taking `inner` and returns something else
            default (U): Matching default for if Err

        Returns:
            Res[U, E]: Transformed `Res` if Ok, or using default if Err
        """
        if self.is_err():
            return Res.Ok(default, E)
        return Res.Ok(using(self.inner), E)
    
    def map_or_else(self, using: Callable[[T], U], default: Callable[[E], U]) -> Res[U, E]:
        """Changes inner if Ok or with default func if Err

        Args:
            using (Callable[[T], U]): Func taking `inner` and returns something else
            default (Callable[[E], U]): Func taking Exception and returns matching something

        Returns:
            Res[U, E]: Transformed `Res` if Ok, or else with default if Err
        """
        if self.is_err():
            return Res.Ok(default(self.inner), E)
        return Res.Ok(using(self.inner), E)
    
    def map_err(self, using: Callable[[E], F]) -> Res[T, F]:
        """Changes the inner Exception if Err

        Args:
            using (Callable[[E], F]): Func taking Exception and returns a new one

        Returns:
            Res[T, F]: Transformed `Res` if Err
        """
        if self.is_err():
            return Res.Err(using(self.inner), T)
        return Res.Ok(self.inner, F)
    
    def and_then(self, using: Callable[[T], Res[U, F]]) -> Res[U, F]:
        """Returns a new Res using inner if Ok

        Args:
            using (Callable[[T], Res[U, E]]): Func taking inner and returns a new `Res`

        Returns:
            Res[U, E]: New `Res` using inner value
        """
        if self.is_err():
            return Res.Err(self.inner)
        return using(self.inner)
    
    def or_else(self, using: Callable[[E], Res[U, F]]) -> Res[U, F]:
        """Returns a new Res using inner Exception if Err

        Args:
            using (Callable[[E], Res[T, F]]): Func taking inner Exception returning a new `Res`

        Returns:
            Res[T, F]: New `Res` using inner Exception
        """
        if self.is_err():
            return using(self.inner)
        return Res.Ok(self.inner, F)
    
    def and_(self, res: Res[U, F]) -> Res[U, F]:
        """Replaces with a new `Res` if Ok

        Args:
            res (Res[U, F]): A new `Res`

        Returns:
            Res[U, F]: A new `Res` if Ok
        """
        if self.is_err():
            return Res.Err(self.inner, U)
        return res
    
    def or_(self, res: Res[U, F]) -> Res[U, F]:
        """Replaces with a new `Res` if `Err`

        Args:
            res (Res[U, F]): A new `Res`

        Returns:
            Res[U, F]: A new `Res` if Err
        """
        if self.is_err():
            return res
        return Res.Ok(self.inner, F)
    
    def do(self, using: Callable[[T], U]) -> Res[T, E]:
        """Runs a function over inner if Ok, but stays the same

        Args:
            using (Callable[[T], U]): Function taking `inner` returning something else

        Returns:
            Res[T, E]: The same `Res`
        """
        if self.is_err():
            return Res.Err(self.inner, T)
        using(self.inner)
        return Res.Ok(self.inner, E)
    
    def do_err(self, using: Callable[[E], U]) -> Res[T, E]:
        """Runs a function over inner if Err, but stays the same

        Args:
            using (Callable[[E], U]): Function taking Exception returning something else

        Returns:
            Res[T, E]: The same `Res`
        """
        if self.is_err():
            using(self.inner)
            return Res.Err(self.inner, T)
        return Res.Ok(self.inner, E)
    
    @property
    def q(self) -> T:
        """Shorthand for unwrap"""
        return self.unwrap()
    
    @property
    def u(self) -> tuple[T | None, E | None]:
        """Shorthand for unpack"""
        return self.unpack()
    
Opt: TypeAlias = Res[T, Nil]
"""Type alias for a `Res` that has checked for None. Uses the `Nil` Exception"""
