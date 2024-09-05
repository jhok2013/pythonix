"""Gracefully handle Errors and None as result values. Catch them as values with decorators."""

from __future__ import annotations
from typing import (
    Generic,
    TypeVar,
    Callable,
    ParamSpec,
    cast,
    Iterator,
    overload,
)
from typing_extensions import TypedDict
from dataclasses import dataclass
from functools import wraps

P = ParamSpec("P")
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
T_co = TypeVar("T_co", covariant=True)
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")
U = TypeVar("U")


class UnwrapError(Exception):
    """Exception used for when a `Res` is unwrapped while in an error state"""

    def __init__(self, message: str = "Unwrapped while in an Err state"):
        super().__init__(self, message)


class ExpectError(Exception):
    """Exception used for when a `Res` is unwrapped with `expect`"""

    def __init__(self, message: str):
        super().__init__(self, message)


class Nil(Exception):
    """Exception used for when a `Res` is None while expecting something"""

    def __init__(self, message: str = "Found None while expecting something"):
        super().__init__(self, message)


class ResDict(Generic[T, E], TypedDict):
    """A dictionary version of a `Res`. Useful for when it needs to be pickled

    ## Examples

    >>> res_dict = Res.Some(10).to_dict()
    >>> res_dict['ok']
    10
    >>> res_dict['is_err']
    False
    >>> res = Res.from_dict(res_dict)
    >>> res.unwrap()
    10
    >>> res.is_err
    False

    """

    ok: T | None
    err: E | None
    is_ok: bool


@dataclass(frozen=True, eq=True, match_args=True, repr=True)
class Res(Generic[T, E]):
    """Container used for capturing the outcome of something that could fail.

    Use `Ok`, `Err`, `Some`, or `Nil` for construction instead of __init__. ::

        >>> ok: Res[int, Exception] = Res[int, Exception].Ok(10)
        >>> err: Res[int, Exception] = Res[int, Exception].Err(Exception("foo"))
        >>> some: Res[int, Nil] = Res.Some(10)

    Using `==` and `!=` is safe and will work between `Res` in different states. ::

        >>> ok == ok
        True
        >>> err != ok
        True
        >>> ok == Res[int, ValueError].Ok(11)
        False

    In can be used to check the value if Ok or check for its presence in an iterable::

        >>> 10 in ok
        True
        >>> 10 in Res[list[int], ValueError].Ok([0, 1, 2, 3])
        False
        >>> 10 in err
        False

    Comparisons can be made between same states, returning False for different states. ::

        >>> ok > Res[int, ValueError].Ok(9)
        True
        >>> ok > err
        False
        >>> ok >= ok
        True
        >>> ok <= ok
        True

    Iterating on `Res` is a way to perform operations if `Ok` or do nothing if `Err` ::

        >>> for val in ok:
        ...     val
        10
        ...
        >>> for val in err:
        ...     val
        ...
        >>> # Does nothing because it failed

    Will automatically iterate over Ok list, tuple, and set objects ::

        >>> iter_ok = Res[list[int], ValueError].Ok([10, 20])
        >>> total: int = 0
        >>> for val in iter_ok:
        ...     total += val
        >>> total
        30
    
    Can do pattern matching with a little help ::

        >>> match ok:
        ...     case Res(int(val)):
        ...         val
        ...     case Res(err):
        ...         pass
        10
    
    If it is Ok then it is also True, if Err it is also False ::

        >>> if ok:
        ...     True
        True
        >>> if not ok:
        ...     False
        False
    
    Unpack it like in Go using `unpack` or `u` for short

        >>> val, nil = ok.unpack()
        >>> if nil is not None:
        ...     pass # Do something here
        >>> val
        10
        >>> val, nil = err.u
        >>> val
        None

    """

    inner: T | E
    """The wrapped value, could be an Exception"""
    is_ok: bool
    """Indicates if the `Res` is in err state"""

    def __nonzero__(self) -> bool:
        return self.is_ok

    def __bool__(self) -> bool:
        return self.is_ok

    def __str__(self) -> str:
        if self.is_err:
            match self.unwrap_err():
                case e:
                    return f"Err(inner={e.__class__.__name__}('{str(e)}'))"
        if isinstance(self.inner, str):
            return f"Ok(inner='{self.inner}')"
        return f"Ok(inner={self.inner})"

    def __contains__(self, item) -> bool:
        if self.is_err:
            return False
        if hasattr(self.inner, "__iter__") or hasattr(self.inner, "__contains__"):
            return item in self.inner
        else:
            return item in [self.inner]

    @overload
    def __iter__(self: Res[tuple[U], E]) -> Iterator[U]:
        ...

    @overload
    def __iter__(self: Res[list[U], E]) -> Iterator[U]:
        ...

    @overload
    def __iter__(self: Res[set[U], E]) -> Iterator[U]:
        ...

    @overload
    def __iter__(self: Res[U, E]) -> Iterator[U]:
        ...

    def __iter__(self):
        if self.is_err:
            return iter([])
        match self.unwrap():
            case list(data) | tuple(data) | set(data):
                return iter(data)
            case x:
                return iter([x])

    def __lt__(self, other: object) -> bool:
        method_name: str = "__lt__"
        opposite_name: str = "__gt__"
        match other:
            case Res(inner, is_ok) if is_ok == self.is_ok:
                if hasattr(self.inner, method_name):
                    return self.inner < inner
                if hasattr(self.inner, opposite_name):
                    return not self.inner > inner
                raise TypeError(
                    f"No comparison possible between {type(self.inner)} and {type(inner)}"
                )
            case _:
                return False

    def __le__(self, other: object) -> bool:
        method_name: str = "__le__"
        opposite_name: str = "__ge__"
        match other:
            case Res(inner, is_ok) if is_ok == self.is_ok:
                if hasattr(self.inner, method_name):
                    return self.inner <= inner
                if hasattr(self.inner, opposite_name):
                    return not self.inner >= inner
                raise TypeError(
                    f"No comparison possible between {type(self.inner)} and {type(inner)}"
                )
            case _:
                return False

    def __ge__(self, other: object) -> bool:
        method_name: str = "__ge__"
        opposite_name: str = "__le__"
        match other:
            case Res(inner, is_ok) if is_ok == self.is_ok:
                if hasattr(self.inner, method_name):
                    return self.inner >= inner
                if hasattr(self.inner, opposite_name):
                    return not self.inner <= inner
                raise TypeError(
                    f"No comparison possible between {type(self.inner)} and {type(inner)}"
                )
            case _:
                return False

    def __gt__(self, other: object) -> bool:
        method_name: str = "__gt__"
        opposite_name: str = "__lt__"
        match other:
            case Res(inner, is_ok) if is_ok == self.is_ok:
                if hasattr(self.inner, method_name):
                    return self.inner > inner
                if hasattr(self.inner, opposite_name):
                    return not self.inner < inner
                raise TypeError(
                    f"No comparison possible between {type(self.inner)} and {type(inner)}"
                )
            case _:
                return False

    @staticmethod
    def Ok(value: T) -> Res[T, E]:
        """Creates a `Res` in an `Ok` state. Cannot receive a child of `Exception`

        Args:
            value (U): The value to be wrapped
            other_type (type[F]): An Exception type if it were `Err`

        Returns:
            Res[U, F]: The new `Res` in an `Ok` state

        ## Examples

        >>> ok = Res.Ok[int, Exception](10)
        >>> ok.is_err
        False
        >>> ok.is_ok
        True

        """
        if isinstance(value, Exception):
            raise TypeError(f"Cannot pass an Exception child to Ok")
        return Res[T, E](value, True)

    @staticmethod
    def Err(value: E) -> Res[T, E]:
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
        if not isinstance(value, Exception):
            raise TypeError(f"Expected subclass of Exception but found {value}")
        return Res[T, E](value, False)

    @staticmethod
    def Some(value: U | None) -> Res[U, Nil]:
        """Creates an `Opt[U]`, checking for None

        Args:
            value (U | None): Value that could be None

        Returns:
            Opt[U]: A new `Res` that has checked for None

        ## Examples

        >>> some: Res[int, NoneError] = Res.Some(10)
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
            return Res.Err(Nil())
        return Res.Ok(value)

    @staticmethod
    def Nil(nil_message: str | None = None) -> Res[T, Nil]:
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
            return Res.Err(Nil(nil_message))
        return Res.Err(Nil())

    def unpack(self) -> tuple[T, None] | tuple[None, E]:
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
                return None, self.unwrap_err()
            case False:
                return self.unwrap(), None

    @property
    def is_err(self) -> bool:
        """Indicates if the `Res` is in Err state

        Returns:
            bool: True if Err, False if Ok

        ## Examples

        >>> ok: Res[int, Exception] = Res.Ok(10, Exception)
        >>> ok.is_err
        False
        >>> err: Res[int, Exception] = Res.Err(Exception(), int)
        >>> err.is_err
        True

        """
        return not self.is_ok

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
            return predicate(self.unwrap_err())
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
            return predicate(self.unwrap())
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
            return cast(T, self.inner)
        else:
            raise self.unwrap_err()

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
            return cast(E, self.inner)
        raise UnwrapError("Unwrapped Err while in Ok state")

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
        return self.unwrap()

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
        return self.unwrap()

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
        return self.unwrap()

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
            return self.unwrap_err()
        raise ExpectError(message)

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
            return Res[U, E].Err(self.unwrap_err())
        return Res[U, E].Ok(using(self.unwrap()))

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
            return Res[U, E].Ok(default)
        return Res[U, E].Ok(using(self.q))

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
        return self.and_(Res[U, E].Ok(new))

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

        return self.or_(Res[T, F].Err(new))

    def map_or_else(
        self, using: Callable[[T], U], default: Callable[[E], U]
    ) -> Res[U, E]:
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
            return Res[U, E].Ok(default(self.unwrap_err()))
        return Res[U, E].Ok(using(self.unwrap()))

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
            return Res[T, F].Err(using(self.unwrap_err()))
        return Res[T, F].Ok(self.unwrap())

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
            return Res[T, F].Err(err_type(str(self.unwrap_err())))
        return Res[T, F].Ok(self.unwrap())

    def and_then(self, using: Callable[[T], Res[U, F]]) -> Res[U, E | F]:
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
            return Res[U, E | F].Err(self.unwrap_err())
        return cast(Res[U, E | F], using(self.unwrap()))

    def or_else(self, using: Callable[[E], Res[U, F]]) -> Res[T | U, F]:
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
            return cast(Res[T | U, F], using(self.unwrap_err()))
        return Res[T | U, F].Ok(self.unwrap())

    def and_(self, res: Res[U, F]) -> Res[U, E | F]:
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
            return Res[U, E | F].Err(self.unwrap_err())
        return cast(Res[U, E | F], res)

    def or_(self, res: Res[U, F]) -> Res[T | U, F]:
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
            return cast(Res[T | U, F], res)
        return Res[T | U, F].Ok(self.unwrap())

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
            return Res[T, E].Err(self.unwrap_err())
        using(self.unwrap())
        return Res[T, E].Ok(self.unwrap())

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
            using(self.unwrap_err())
            return Res[T, E].Err(self.unwrap_err())
        return Res[T, E].Ok(self.unwrap())

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

    def to_dict(self) -> ResDict[T, E]:
        """Converts to a typed dictionary with current data and type info

        Useful for when you need to pickle or serialize a Res

        Returns:
            ResDict[T, E]: The dictionary version of the Res

        ## Examples

        >>> ok: Res[int, Nil] = Res.Some(10)
        >>> res_dict: ResDict[int, Nil] = ok.to_dict()
        >>> res_dict["is_err"]
        False
        >>> res_dict["ok"]
        10
        >>> res_dict["err"]
        None

        """
        if self.is_err:
            return ResDict[T, E](ok=None, err=self.unwrap_err(), is_ok=False)
        else:
            return ResDict[T, E](ok=self.unwrap(), err=None, is_ok=True)

    @staticmethod
    def from_dict(res_dict: ResDict[U, F]) -> Res[U, F]:
        """Creates a Res from a ResDict or dictionary that follows the same schema

        Args:
            res_dict (ResDict[U, F]): A dict that follows the ResDict schema, or an actual ResDict

        Raises:
            Nil: Raised if is_err is True and err is None
            Nil: Raised if is_err is False and ok is None

        Returns:
            Res[U, F]: A Res with the same values as the dictionary

        ## Examples

        >>> res_dict: ResDict[int, Nil] = ResDict(ok=10, err=None, is_err=False)
        >>> ok: Res[int, Nil] = Res.from_dict(res_dict)
        >>> ok.unwrap()
        10
        >>> ok.is_err
        False

        """
        match res_dict["is_ok"]:
            case False:
                match res_dict["err"]:
                    case None:
                        raise Nil()
                    case err:
                        return Res[U, F].Err(err)
            case True:
                match res_dict["ok"]:
                    case None:
                        raise Nil()
                    case ok:
                        return Res[U, F].Ok(ok)


def safe(*err_type: type[E]):
    """Decorator function to catch raised ``Exception`` and return ``Res[T, E]``

    ``T`` is the original return value and ``E`` is the combination of specified
    ``Exceptions``

    Note:
        Multiple ``Exception``s can be specified in the first call

    Args:
        *err_type* (type[E]): Args tuple of ``Exception`` types to catch
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
                return Res[U, E].Ok(using(*args, **kwargs))
            except err_type as e:
                return Res[U, E].Err(e)

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
    def inner(*args: P.args, **kwargs: P.kwargs) -> Res[U, Nil]:
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
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[T, Nil]:
            try:
                return Res.Some(using(*args, **kwargs))
            except err_types as e:
                return Res[T, Nil](Nil(), False)

        return wrapper

    return inner


def combine_errors(to: type[F], inherit_message: bool = False):
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
                lambda e: to(str(e)) if inherit_message else to()
            )

        return wrapper

    return inner
