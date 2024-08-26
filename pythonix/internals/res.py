"""Gracefully handle Errors and None as result values. Catch them as values with decorators."""

from __future__ import annotations
from typing import Generic, TypeVar, Callable, TypeAlias, overload, ParamSpec
from dataclasses import dataclass, field
from functools import wraps

P = ParamSpec("P")
T = TypeVar("T")
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")
U = TypeVar("U")


class UnwrapError(Exception):
    """Exception used for when a `Res` is unwrapped while in an error state"""

    def __init__(self, message: str = 'Unwrapped while in an Err state'):
        super().__init__(self, message)

class ExpectError(Exception):
    """Exception used for when a `Res` is unwrapped with `expect`"""

    def __init__(self, message: str):
        super().__init__(self, message)

class NoneError(Exception):
    """Exception used for when a `Res` is None while expecting something"""

    def __init__(self, message: str = 'Found None while expecting something'):
        super().__init__(self, message)

@dataclass(frozen=True, init=False, eq=True)
class Res(Generic[T, E], object):
    """Container used for capturing the outcome of something that could fail.

    Use the factory methods `Ok`, `Err`, or `Some` for construction instead of __init__.
    
    Attributes:
        inner (T | E): The wrapped value, could be an Exception.
    
    """

    _inner: T | E
    """The wrapped value, could be an Exception"""
    _is_err: bool = field(repr=False)
    """Whether the `Res` is an Exception. Only set on creation."""

    __match_args__ = ("inner",)

    def __repr__(self) -> str:
        if self.is_err:
            return f"Err(inner={self.inner})"
        if isinstance(self.inner, str):
            return f"Ok(inner='{self.inner}')"
        return f"Ok(inner={self.inner})"

    @property
    def inner(self) -> T | E:
        """The wrapped value.

        Returns:
            T | E: The wrapped value
        """
        return self._inner

    @classmethod
    def Ok(cls, value: U, err_type: type[F]) -> Res[U, F]:
        """Creates a `Res` in an `Ok` state.

        Args:
            value (U): The value to be wrapped
            other_type (type[F]): An Exception type if it were `Err`

        Returns:
            Res[U, F]: The new `Res` in an `Ok` state
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.is_err
        False
        >>> ok.is_ok
        True

        """
        obj = object.__new__(cls)
        object.__setattr__(obj, '_inner', value)
        object.__setattr__(obj, '_is_err', False)
        return obj
    
    @classmethod
    def Err(cls, value: F, ok_type: type[U]) -> Res[U, F]:
        """Creates a `Res` in an `Err` state

        Args:
            value (F): The captured Exception to be wrapped
            other_type (type[U]): The type if it were `Ok`k

        Raises:
            TypeError: Raised if the value is not bound to `Exception`

        Returns:
            Res[U, F]: The new `Res` in an `Err` state
        
        ## Examples

        >>> err: Res[int, ValueError] = Res.Err(ValueError(), int)
        >>> err.is_err
        True
        >>> err.is_ok
        False
        >>> try:
        ...     Res.Err("Not an Exception", int)
        ... except TypeError as e:
        ...     e
        ...
        TypeError("Expected subclass of Exception but found str") 

        """
        obj = object.__new__(cls)
        if not isinstance(value, Exception):
            raise TypeError(f"Expected subclass of Exception but found {value}")
        object.__setattr__(obj, '_inner', value)
        object.__setattr__(obj, '_is_err', True)
        return obj
    
    @staticmethod
    def Some(value: U | None) -> Opt[U]:
        """Creates an `Opt[U]`, checking for None

        Args:
            value (U | None): Value that could be None

        Returns:
            Opt[U]: A new `Res` that has checked for None
        
        ## Examples

        >>> some: Opt[int] = Res.Some(10)
        >>> some.is_err
        False
        >>> some.is_ok
        True
        >>> nil = Res.Some(None)
        >>> nil.is_err
        True
        >>> nil.is_ok
        False
        """
        if value is None:
            return Res.Err(NoneError(), U)
        return Res.Ok(value, NoneError)
    
    @staticmethod
    def Nil(some_type: type[U], nil_message: str | None = None) -> Opt[U]:
        """Creates an `Opt[U]` in an Err state with Nil

        Args:
            some_type (type[U]): The type if it were something
            nil_message (str | None, optional): Message for Nil Exception. Defaults to None.

        Returns:
            Opt[T]: A new Opt
        
        ## Examples

        >>> nil: Opt[int] = Res.Nil(int, "Nothing was found")
        >>> nil.unwrap_err()
        NoneError("Nothing was found")

        """
        if nil_message is not None:
            return Res.Err(NoneError(nil_message), some_type)
        return Res.Err(NoneError(), some_type)
    
    def unpack(self) -> tuple[T | None, U | None]:
        """Unpacks the `Res` a la Go for quick checking if desired

        Returns:
            Tuple[T | None, U | None]: The results as a tuple
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> val, err = ok.unpack()
        >>> err is None
        True
        >>> val
        10

        """
        match self.is_err:
            case True:
                return None, self.inner
            case False:
                return self.inner, None
    
    def some(self) -> Opt[T]:
        """Converts the `Res` to an `Opt`, consuming the `E` value

        Returns:
            Opt[T]: The new `Opt`
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> some: Opt[int] = ok.some()
        >>> some.unwrap()
        10

        """
        if self.is_err or self.inner is None:
            return Res.Err(NoneError(), T)
        return Res.Ok(self.inner, E)
    
    @property
    def is_err(self) -> bool:
        """Indicates if the `Res` is in err state

        Returns:
            bool: True if in Err, False if Ok
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.is_err
        False
        >>> err: Res[int, Exception] = Res.Err(Exception(), int)
        >>> err.is_err
        True

        """
        return self._is_err
    
    @property
    def is_ok(self) -> bool:
        """Indicates if the `Res` is in Ok state

        Returns:
            bool: True if Ok, False if Err
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.is_ok
        True
        >>> err: Res[int, Exception] = Res.Err(Exception(), int)
        >>> err.is_ok
        False

        """
        return not self._is_err
    
    def is_err_and(self, predicate: Callable[[E], bool]) -> bool:
        """Runs the predicate on the wrapped value if Err

        Args:
            predicate (Callable[[E], bool]): Func taking `inner` and returns `bool`

        Returns:
            bool: If state is Err and predicate returns True then True

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.is_err_and(lambda e: e.message == "foo")
        False
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.is_err_and(lambda e: e.message == "foo")
        False

        """
        if self.is_err:
            return predicate(self._inner)
        return False

    def is_ok_and(self, predicate: Callable[[T], bool]) -> bool:
        """Runs the predicate on the wrapped value if Ok

        Args:
            predicate (Callable[[T], bool]): Func taking `inner` and returns `bool`

        Returns:
            bool: If state is Ok and predicate returns True then True

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.is_ok_and(lambda x: x > 1)
        True
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.is_ok_and(lambda x: x > 1)
        False

        """
        if self.is_ok:
            return predicate(self._inner)
        return False
    
    def unwrap(self) -> T:
        """Returns wrapped value, or panics if Err

        Raises:
            UnwrapError: Expected Ok state but found Err

        Returns:
            T: Returns wrapped value if Ok
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.unwrap()
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.unwrap()
        UnwrapError("Unwrapped while in an Err state")

        """
        if self.is_ok:
            return self.inner
        raise UnwrapError()
    
    def unwrap_err(self) -> E:
        """Returns wrapped Exception if Err, else panics

        Raises:
            UnwrapError: Expected Err state but found Ok

        Returns:
            E: Returns wrapped Exception if Err
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.unwrap_err()
        UnwrapError('Unwrapped Err while in Ok state')
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.unwrap_err()
        Exception('foo')
        
        """
        if self.is_err:
            return self.inner
        raise UnwrapError('Unwrapped Err while in Ok state')
    
    def unwrap_or(self, default: T) -> T:
        """Returns wrapped value or default

        Args:
            default (T): Default value for when Err

        Returns:
            T: Wrapped value if Ok else default

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.unwrap_or(0)
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.unwrap_or(0)
        0

        """
        if self.is_err:
            return default
        return self.inner
    
    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        """Returns wrapped value or runs default

        Args:
            default (Callable[[], T]): Default func for when Err

        Returns:
            T: Wrapped value if Ok else output from default
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.unwrap_or_else(lambda: 0)
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.unwrap_or_else(lambda: 0)
        0

        """
        if self.is_err:
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

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.expect("Failed")
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.expect("Failed")
        ExpectError("Failed")

        """
        if self.is_err:
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

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.expect_err("Expected Exception")
        ExpectError("Expected Exception")
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.unwrap_err()
        Exception("foo")

        """
        if self.is_err:
            return self.inner
        raise ExpectError(message)
    
    @overload
    def map(self: Res[T, NoneError], using: Callable[[T], U]) -> Opt[U]: ...

    @overload
    def map(self: Res[T, E], using: Callable[[T], U]) -> Res[U, E]: ...
    
    def map(self, using: Callable[[T], U]) -> Res[U, E]:
        """Changes inner if Ok with a function

        Args:
            using (Callable[[T], U]): Func taking `inner` and returns something else

        Returns:
            Res[U, E]: Transformed `Res` if Ok
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.map(lambda x: x + 5).unwrap()
        15
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.map(lambda x: x + 5).unwrap_err()
        Exception("foo")

        """
        if self.is_err:
            return Res.Err(self.inner, T)
        return Res.Ok(using(self.inner), E)
    
    @overload
    def map_or(self: Res[T, NoneError], using: Callable[[T], U], default: U) -> Opt[U]: ...

    @overload
    def map_or(self: Res[T, E], using: Callable[[T], U], default: U) -> Res[U, E]: ...
    
    def map_or(self, using: Callable[[T], U], default: U) -> Res[U, E]:
        """Changes inner if Ok or uses default if Err

        Args:
            using (Callable[[T], U]): Func taking `inner` and returns something else
            default (U): Matching default for if Err

        Returns:
            Res[U, E]: Transformed `Res` if Ok, or using default if Err

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.map_or(lambda x: x + 5, 20).unwrap()
        15
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.map_or(lambda x: x + 5, 20).unwrap()
        20

        """
        if self.is_err:
            return Res.Ok(default, E)
        return Res.Ok(using(self.inner), E)
    
    @overload
    def replace(self: Res[T, NoneError], new: U) -> Opt[U]: ...

    @overload
    def replace(self: Res[T, E], new: U) -> Res[U, E]: ...
    
    def replace(self, new: U) -> Res[U, E]:
        """Replaces the Ok value if Ok

        Args:
            new (U): The new value

        Returns:
            Res[U, E]: The updated Res
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.replace(20).unwrap()
        20
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> ok.replace(20).unwrap()
        Exception("foo")

        """
        return self.and_(Res.Ok(new, E))
    
    def replace_err(self, new: F) -> Res[T, F]:
        """Replaces the Err value with a new Exception if Err

        Args:
            new (F): The new Exception

        Returns:
            Res[T, F]: The updated Res
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.replace_err(ValueError("bar")).unwrap()
        20
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> ok.replace_err(ValueError("bar")).unwrap_err()
        ValueError('bar')

        """

        return self.or_(Res.Err(new, T))
    
    @overload
    def map_or_else(self: Res[T, NoneError], using: Callable[[T], U], default: Callable[[NoneError], U]) -> Opt[U]: ...

    @overload
    def map_or_else(self: Res[T, E], using: Callable[[T], U], default: Callable[[E], U]) -> Res[U, E]: ...
    
    def map_or_else(self, using: Callable[[T], U], default: Callable[[E], U]) -> Res[U, E]:
        """Changes inner if Ok or with default func if Err

        Args:
            using (Callable[[T], U]): Func taking `inner` and returns something else
            default (Callable[[E], U]): Func taking Exception and returns matching something

        Returns:
            Res[U, E]: Transformed `Res` if Ok, or else with default if Err

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.map_or_else(lambda x: x + 5, lambda e: 20).unwrap()
        15
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.map(lambda x: x + 5, lambda e: 20).unwrap()
        20

        """
        if self.is_err:
            return Res.Ok(default(self.inner), E)
        return Res.Ok(using(self.inner), E)
    
    def map_err(self, using: Callable[[E], F]) -> Res[T, F]:
        """Changes the inner Exception if Err

        Args:
            using (Callable[[E], F]): Func taking Exception and returns a new one

        Returns:
            Res[T, F]: Transformed `Res` if Err
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.map_err(lambda e: ValueError(str(e))).unwrap_err()
        UnwrapError("Expected Err but found Ok")
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.map_err(lambda e: ValueError(str(e))).unwrap_err()
        ValueError("foo")

        """
        if self.is_err:
            return Res.Err(using(self.inner), T)
        return Res.Ok(self.inner, F)
    
    def convert_err(self, err_type: type[F]) -> Res[T, F]:
        """Converts an Exception of one type to another if Err

        Args:
            err_type (type[F]): Exception class used to cast into

        Returns:
            Res[T, F]: A new Res with an updated Err value
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.convert_err(ValueError).unwrap()
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.convert_error(ValueError).unwrap_err()
        ValueError("foo")

        """
        if self.is_err:
            return Res.Err(err_type(str(self.inner)))
        return Res.Ok(self.inner, F)

    def and_then(self, using: Callable[[T], Res[U, F]]) -> Res[U, F]:
        """Returns a new Res using inner if Ok

        Args:
            using (Callable[[T], Res[U, E]]): Func taking inner and returns a new `Res`

        Returns:
            Res[U, E]: New `Res` using inner value
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.and_then(lambda x: Res.Ok(x + 10, Exception)).unwrap()
        20
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.and_then(lambda x: Res.Ok(x + 10, Exception)).unwrap_err()
        Exception("foo")

        """
        if self.is_err:
            return Res.Err(self.inner, U)
        return using(self.inner)
    
    def or_else(self, using: Callable[[E], Res[U, F]]) -> Res[U, F]:
        """Returns a new Res using inner Exception if Err

        Args:
            using (Callable[[E], Res[T, F]]): Func taking inner Exception returning a new `Res`

        Returns:
            Res[T, F]: New `Res` using inner Exception

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.or_else(lambda e: Res.Err(ValueError(str(e)), int)).unwrap()
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.or_else(lambda e: Res.Ok(20, ValueError(str(e)))).unwrap()
        20

        """
        if self.is_err:
            return using(self.inner)
        return Res.Ok(self.inner, F)
    
    def and_(self, res: Res[U, F]) -> Res[U, F]:
        """Replaces with a new `Res` if Ok

        Args:
            res (Res[U, F]): A new `Res`

        Returns:
            Res[U, F]: A new `Res` if Ok

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.and_(Res.Ok(20, ValueError)).unwrap()
        20
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.and_(Res.Ok(20, ValueError)).unwrap_err()
        Exception("foo")

        """
        if self.is_err:
            return Res.Err(self.inner, U)
        return res
    
    def or_(self, res: Res[U, F]) -> Res[U, F]:
        """Replaces with a new `Res` if `Err`

        Args:
            res (Res[U, F]): A new `Res`

        Returns:
            Res[U, F]: A new `Res` if Err

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.or_(Res.Ok(20, ValueError)).unwrap()
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.or_(Res.Ok(20, ValueError)).unwrap()
        20

        """
        if self.is_err:
            return res
        return Res.Ok(self.inner, F)
    
    @overload
    def do(self: Res[T, NoneError], using: Callable[[T], U]) -> Opt[T]: ...

    @overload
    def do(self: Res[T, E], using: Callable[[T], U]) -> Res[T, E]: ...
    
    def do(self, using: Callable[[T], U]) -> Res[T, E]:
        """Runs a function over inner if Ok, but stays the same

        Args:
            using (Callable[[T], U]): Function taking `inner` returning something else

        Returns:
            Res[T, E]: The same `Res`

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.do(lambda x: x + 10).unwrap()
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.do(lambda x: x + 10).unwrap()
        Exception("foo")

        """
        if self.is_err:
            return Res.Err(self.inner, T)
        using(self.inner)
        return Res.Ok(self.inner, E)
    
    @overload
    def do_err(self: Res[T, NoneError], using: Callable[[NoneError], U]) -> Opt[T]: ...

    @overload
    def do_err(self: Res[T, E], using: Callable[[E], U]) -> Res[T, E]: ...
    
    def do_err(self, using: Callable[[E], U]) -> Res[T, E]:
        """Runs a function over inner if Err, but stays the same

        Args:
            using (Callable[[E], U]): Function taking Exception returning something else

        Returns:
            Res[T, E]: The same `Res`

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.do_err(lambda e: str(e)).unwrap_err()
        UnwrapError("Expected Err state but found Ok")
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.do_err(str).unwrap_err()
        Exception("foo")

        """
        if self.is_err:
            using(self.inner)
            return Res.Err(self.inner, T)
        return Res.Ok(self.inner, E)
    
    @property
    def q(self) -> T:
        """Shorthand for unwrap
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.q
        10
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> err.q
        Exception("foo")

        """
        return self.unwrap()
    
    @property
    def u(self) -> tuple[T | None, E | None]:
        """Shorthand for unpack
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> val, err = ok.u
        >>> val
        10
        >>> err
        None
        >>> err: Res[int, Exception] = Res.Err(Exception("foo"), int)
        >>> val, err = err.u
        >>> val
        None
        >>> err
        Exception('foo')

        """
        return self.unpack()
    
Opt: TypeAlias = Res[T, NoneError]
"""Type alias for a `Res` that has checked for None. Uses the `Nil` Exception"""

def Ok(value: T, err_type: type[E]) -> Res[T, E]:
    """Creates a `Res` in an `Ok` state.

        Args:
            value (U): The value to be wrapped
            other_type (type[F]): An Exception type if it were `Err`

        Returns:
            Res[U, F]: The new `Res` in an `Ok` state
        
        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.is_err
        False
        >>> ok.is_ok
        True

    """
    return Res.Ok(value, err_type)

def Err(value: E, ok_type: type[T]) -> Res[T, E]:
    """Creates a `Res` in an `Err` state

        Args:
            value (F): The captured Exception to be wrapped
            other_type (type[U]): The type if it were `Ok`k

        Raises:
            TypeError: Raised if the value is not bound to `Exception`

        Returns:
            Res[U, F]: The new `Res` in an `Err` state
        
        ## Examples

        >>> err: Res[int, ValueError] = Res.Err(ValueError(), int)
        >>> err.is_err
        True
        >>> err.is_ok
        False
        >>> Res.Err("Not an Exception", int)
        TypeError("Expected subclass of Exception but found str") 

    """
    return Res.Err(value, ok_type)

def Some(value: T | None) -> Opt[T]:
    """Creates an `Opt[U]`, checking for None

        Args:
            value (U | None): Value that could be None

        Returns:
            Opt[U]: A new `Res` that has checked for None
        
        ## Examples

        >>> some: Opt[int] = Res.Some(10)
        >>> some.is_err
        False
        >>> some.is_ok
        True
        >>> nil = Res.Some(None)
        >>> nil.is_err
        True
        >>> nil.is_ok
        False
    """
    return Res.Some(value)

def Nil(some_type: type[T], nil_message: str | None = None) -> Opt[T]:
    """Creates an `Opt[U]` in an Err state with Nil

        Args:
            some_type (type[U]): The type if it were something
            nil_message (str | None, optional): Message for Nil Exception. Defaults to None.

        Returns:
            Opt[T]: A new Opt
        
    """
    return Res.Nil(some_type, nil_message)

def safe(*err_type: type[E]):
    """Decorator function to catch raised ``Exception`` and return ``Res[T, E]``

    ``T`` is the original return value and ``E`` is the combination of specified
    ``Exceptions``

    Note:
        Multiple ``Exception``s can be specified in the first call

    Args:
        *err_type* (type[E]): *Args tuple of ``Exception`` types to catch
        *using* ((P) -> U): Any function with typed arguments and return values

    Returns:
        *wrapped* ((P) -> Res[U, E]): Wrapped function that returns a result instead
        of its original result, catching the thrown errors if any.

    ## Examples

    >>> @safe(KeyError)
    ... def access(data: dict[str, str], key: str) -> str:
    ...     return data[key]
    ...
    >>> data: dict[str, str] = {'hello': 'world'}
    >>> element: Res[str, KeyError] = access(data, 'hello')
    >>> element.unwrap()
    'world'
    >>> bad_element: Res[str, KeyError] = access(data, 'hola')
    >>> bad_element.unwrap_err()
    KeyError('hola')

    """

    def inner(using: Callable[P, U]) -> Callable[P, Res[U, E]]:
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[U, E]:
            try:
                return Res.Ok(using(*args, **kwargs), E)
            except err_type as e:
                return Res.Err(e, U)

        return wrapper

    return inner


def null_safe(using: Callable[P, U | None]):
    """Captures returned ``None`` values, converting to ``Opt[U]``

    Args:
        *using* ((P) -> U | None): Function that could return None

    Returns:
        *wrapped* ((P) -> Opt[U]): Function that returns ``Opt[U]``

    Examples: ::

        >>> @null_safe
        ... def get(index: str, data: dict[str, str]) -> str | None:
        ...     return data.get(index)
        ...
        >>> data: dict[str, str] = {'hello': 'world'}
        >>> maybe: Opt[str] = get('hello', data)
        >>> maybe.unwrap()
        'world'

    """

    @wraps(using)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Opt[U]:
        return Res.Some(using(*args, **kwargs))

    return inner


def null_and_error_safe(*err_types: type[E]):
    """Captures errors like ``safe``, but also checks for ``None`` like ``null_safe``

    Args:
        *err_type* (type[E]): *Args tuple of ``Exception`` types to catch
        *using* ((P) -> T | None): Function that could fail, and could also return None

    Returns:
        *output* ((P) -> Opt[T]): Function that handles errors and Nones

    Examples: ::

        >>> @null_and_error_safe(KeyError)
        ... def get(index: str, data: dict[str, str]) -> str | None:
        ...     return data[index]
        ...
        >>> data: dict[str, str] = {'hello': 'world'}
        >>> maybe: Opt[str] = get('hello', data)
        >>> maybe.unwrap()
        'world'
    """

    def inner(using: Callable[P, T | None]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Opt[T]:
            try:
                return Res.Some(using(*args, **kwargs))
            except err_types as e:
                return Res.Err(e, T).some()

        return wrapper

    return inner


def combine_errors(to: F, inherit_message: bool = False):
    """Decorator to combine funcs that return Res to return one error instead of many

    Args:
        *to* (F: Exception): The exception that will replace the others
        *inherit_message* (bool = False): Whether to inherit the messages of errors
        *using* ((P) -> Res[T, E]): Function that could return Ok or Err

    Returns:
        *output* ((P) -> Res[T, F]): Function that returns ``Ok`` or ``Err`` with *to*
        as its potential error value

    Examples: ::

        >>> @combine_errors(Nil())
        >>> @safe(KeyError, IndexError)
        ... def get(index: str, data: dict[str, str]) -> str:
        ...     return data[index]
        ...
        >>> data: dict[str, str] = {'hello': 'world'}
        >>> element: Opt[str] = get('hola', data)
        >>> element.unwrap_err()
        Nil('Did not expect None')

    """

    def inner(using: Callable[P, Res[T, E]]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[T, F]:
            return using(*args, **kwargs).map_err(
                lambda e: to.__class__(str(e)) if inherit_message else to
            )

        return wrapper

    return inner
