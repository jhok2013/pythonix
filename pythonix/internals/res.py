"""Handle Exceptions and None values with `Res` type and decorators."""
from __future__ import annotations
from inspect import signature
from typing import (
    Iterable,
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
from pythonix.internals.traits import Ad, MapAlt, Unwrap, UnwrapAlt, Colladic

P = ParamSpec("P")
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
T_co = TypeVar("T_co", covariant=True)
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")
G = TypeVar("G", bound="Exception")
U = TypeVar("U")
C = TypeVar("C")

class UnwrapError(Exception):
    """Exception used for when a `Res` is unwrapped while in an unexpected state"""

    def __init__(self, message: str = "Unwrapped while in an unexpected state"):
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

    #### Examples ::

        >>> res_dict = Res.Some(10).to_dict()
        >>> res_dict['ok']
        10
        >>> res_dict['is_ok']
        True
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
class Res(Ad[T], MapAlt[E], Unwrap[T], UnwrapAlt[E]):
    """Best class ever made. Easy handling of errors as values like Go, Rust, or with custom operators.

    See the docstrings of the functions to learn more. features that don't use methods see below.

    ### Builtin Features

    #### Truthiness

        Use `bool` or simple comparison to see if in Ok or Err state. ::

        >>> if Res.Ok(10):
        ...     'Ok'
        'Ok'
        >>> if not Res.Err(Exception('foo')):
        ...     'Err'
        'Err'
    
    #### Iterate if Ok

    Iterate thru list, tuple, set, and normal values if OK ::
    
        >>> ok = Res.Ok([1, 2, 3])
        >>> data = [i for i in ok]
        >>> data
        [1, 2, 3]
        >>> ok = Res.Ok(1)
        >>> for val in res:
        ...     val
        1
    
    Will iterate over nothing if in Err ::

        >>> err = Res[int, Exception].Err(Exception("Oops"))
        >>> for val in err:
        ...     val
    
    #### Checking with `in` or `__contains__`

    You can check the `Ok` value with `in` ::

        >>> some = Res.Some(10)
        >>> 10 in some
        True
        >>> 9 in some
        False
        >>> some_list = Res.Some([1, 2, 3])
        >>> 1 in some_list
        True
        >>> 4 in some_list
        False
    
    Always returns `False` if in Err state

        >>> nil = Res[int, Nil].Nil()
        >>> 10 in nil
        False
        >>> nil = Res[list[int], Nil].Nil()
        >>> 10 in nil
        False

    
    """

    inner: T | E
    """The wrapped value, could be an Exception. Do NOT access this directly. Could have unexpected behavior."""
    _is_ok: bool
    """Indicates if the `Res` is in ok state"""

    def __nonzero__(self) -> bool:
        return self._is_ok

    def __bool__(self) -> bool:
        return self._is_ok

    def __str__(self) -> str:
        if not self:
            match self.unwrap_alt():
                case e:
                    return f"Err(inner={e.__class__.__name__}('{str(e)}'))"
        if isinstance(self.inner, str):
            return f"Ok(inner='{self.inner}')"
        return f"Ok(inner={self.inner})"

    def __contains__(self, item) -> bool:
        if not self:
            return False
        if hasattr(self.inner, "__iter__") or hasattr(self.inner, "__contains__"):
            return item in self.inner
        else:
            return item in [self.inner]


    @overload
    def __iter__(self: Res[tuple[U], E]) -> Iterator[U]: ...

    @overload
    def __iter__(self: Res[list[U], E]) -> Iterator[U]: ...

    @overload
    def __iter__(self: Res[set[U], E]) -> Iterator[U]: ...

    @overload
    def __iter__(self: Res[U, E]) -> Iterator[U]: ...

    def __iter__(self):

        match self:
            case Res(e, False) if isinstance(e, Exception):
                return iter([])
            case Res(t):
                val = cast(T, t)
                match val:
                    case Colladic():
                        return iter([val])
                    case list(data) | tuple(data) | set(data):
                        return iter(data)
                    case x:
                        return iter([x])

    @staticmethod
    def Ok(value: T) -> Res[T, E]:
        """Creates a `Res` in an `Ok` state. Cannot receive a child of `Exception`

        Args:
            value (T): The value to be wrapped

        Returns:
            Res[T, E]: The new `Res` in an `Ok` state

        #### Examples ::

            >>> ok = Res[int, Exception].Ok(10)
            >>> ok.is_err()
            False
            >>> ok.is_ok()
            True

        """
        if isinstance(value, Exception):
            raise TypeError(f"Cannot pass an Exception child to Ok")
        return Res[T, E](value, True)

    @staticmethod
    def Err(value: E) -> Res[T, E]:
        """Creates a `Res` in an `Err` state

        Args:
            value (E): The captured Exception to be wrapped

        Raises:
            TypeError: Raised if the value is not bound to `Exception`

        Returns:
            Res[T, E]: The new `Res` in an `Err` state

        #### Examples ::

            >>> err: Res[int, ValueError] = Res.Err(ValueError())
            >>> err.is_err()
            True
            >>> err.is_ok()
            False
            >>> try:
            ...     Res[int, Exception].Err("Not an Exception")
            ... except TypeError as e:
            ...     e
            ...
            TypeError('Expected subclass of Exception but found Not an Exception')

        """
        if not isinstance(value, Exception):
            raise TypeError(f"Expected subclass of Exception but found {value}")
        return Res[T, E](value, False)

    @staticmethod
    def Some(value: U | None) -> Res[U, Nil]:
        """Creates an `Res[U, Nil]`, checking for None

        Args:
            value (U | None): Value that could be None

        Returns:
            Res[U, Nil]: A new `Res` that has checked for None

        #### Examples ::

            >>> some: Res[int, Nil] = Res.Some(10)
            >>> some.is_err()
            False
            >>> some.is_ok()
            True
            >>> nil = Res.Some(None)
            >>> nil.is_err()
            True
            >>> nil.is_ok()
            False
        """
        if value is None:
            return Res.Err(Nil())
        return Res.Ok(value)

    @staticmethod
    def Nil(nil_message: str | None = None) -> Res[T, Nil]:
        """Creates an `Opt[T]` in an Err state with Nil

        Args:
            some_type (type[T]): The type if it were something
            nil_message (str | None, optional): Message for Nil Exception. Defaults to None.

        Returns:
            Res[T, Nil]: A new Res in Err state

        #### Examples ::

            >>> nil: Res[int, Nil] = Res.Nil("Nothing was found")
            >>> nil.unwrap_err()
            Nil(Nil(...), 'Nothing was found')

        """
        if nil_message is not None:
            return Res.Err(Nil(nil_message))
        return Res.Err(Nil())

    def unpack(self) -> tuple[T, None] | tuple[None, E]:
        """Unpacks the `Res` a la Go for quick checking if desired

        Returns:
            Tuple[T | None, U | None]: The results as a tuple

        #### Examples ::

            >>> ok: Res[int, Exception] = Res.Ok(10)
            >>> val, err = ok.unpack()
            >>> err is None
            True
            >>> val
            10

        """

        match self:
            case Res(e, False) if isinstance(e, Exception):
                return None, cast(E, e)
            case Res(t):
                return cast(T, t), None

    def ok_and(self, predicate: Callable[[T], bool]) -> bool:
        """Checks if `Res` is `Ok`, running optional function on wrapped value.

        Args:
            predicate (Callable[[T], bool]): Func to run over Ok value

        Returns:
            bool: `False` if Err, `True` if predicate returns `True`

        #### Example ::

            >>> res: Res[int, Exception] = Res.Ok(10)
            >>> res.is_ok()
            True
            >>> res.is_ok(lambda x: x % 2 == 0)
            True
            >>> res.is_ok(lambda x: x > 11)
            False

        """
        if not self:
            return False
        return predicate(cast(T, self.inner))

    def err_and(self, predicate: Callable[[E], bool]) -> bool:
        """Runs predicate on Err value if Err.

        Args:
            predicate (Callable[[E], bool]): Checker func to be ran over value if Err.

        Returns:
            bool: False if Ok, True if predicate returns True

        #### Example ::

            >>> res: Res[int, Exception] = Res.Err(Exception("Hello there"))
            >>> res.is_err()
            True
            >>> res.is_err(lambda e: str(e) == "Hello there")
            True
            >>> res.is_ok(lambda e: str(e) == "General Kenobi")
            False

        """
        if self:
            return False
        return predicate(cast(E, self.inner))

    def unwrap(self) -> T:
        """Returns wrapped Ok value if Ok, else panics with Err

        Raises:
            e: Wrapped Err value

        Returns:
            T: Wrapped Ok value

        #### Examples ::

            >>> res = Res.Some(10)
            >>> res.unwrap()
            10
            >>> err = Res.Nil()
            >>> err.unwrap()
            Nil(Nil(...), 'Found None while expecting something')
        """
        match self:
            case Res(t, True) if not isinstance(t, Exception):
                return t
            case Res(e) if isinstance(e, Exception):
                raise e
        raise ValueError("Unreachable")

    def unwrap_alt(self) -> E:
        """Returns wrapped Exception if Err, else panics

        Raises:
            UnwrapError: Expected Err state but found Ok

        Returns:
            E: Returns wrapped Exception if Err

        #### Examples ::

            >>> ok = Res.Ok(10)
            >>> ok.unwrap_err()
            Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            res.UnwrapError: (UnwrapError(...), 'Unwrapped Err while in Ok state')
            >>> err = Res.Err(Exception("foo"))
            >>> err.unwrap_err()
            Exception('foo')

        """
        if not self:
            return cast(E, self.inner)
        raise UnwrapError("Unwrapped Err while in Ok state")

    def expect(self, message: str) -> T:
        """Returns `inner` else raises ExpectError with custom message

        Args:
            message (str): Custom error message

        Raises:
            ExpectError: Raised if Err, but with custom error message

        Returns:
            T: Inner value if Ok

        #### Examples ::

            >>> ok: Res[int, Exception] = Res.Ok(10)
            >>> ok.expect("Failed")
            10
            >>> err: Res[int, Exception] = Res.Err(Exception("foo"))
            >>> err.expect("Failed")
            Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            res.ExpectError: (ExpectError(...), 'Failed')

        """
        if not self:
            raise ExpectError(message)
        return cast(T, self.inner)

    def expect_err(self, message: str) -> E:
        """Returns wrapped Exception if Err else panics with ExpectError

        Args:
            message (str): Custom error message for if it panics

        Raises:
            ExpectError: Raised if Ok with custom error message

        Returns:
            E: Exception if Err

        #### Examples ::

            >>> ok: Res[int, Exception] = Res.Ok(10)
            >>> ok.expect_err("Expected Exception")
            Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            res.ExpectError: (ExpectError(...), 'Expected Exception')
            >>> err: Res[int, Exception] = Res.Err(Exception("foo"))
            >>> err.unwrap_err()
            Exception('foo')

        """
        if not self:
            return cast(E, self.inner)
        raise ExpectError(message)

    @overload
    def __rshift__(self, using: Callable[[], Res[U, F]]) -> Res[U, E | F]: ...

    @overload
    def __rshift__(self, using: Callable[[T], Res[U, F]]) -> Res[U, E | F]: ...

    @overload
    def __rshift__(self, using: Callable[[], U]) -> Res[U, E]: ...

    @overload
    def __rshift__(self, using: Callable[[T], U]) -> Res[U, E]: ...

    def __rshift__(
        self,
        using: (
            Callable[[], Res[U, F]]
            | Callable[[], U]
            | Callable[[T], Res[U, F]]
            | Callable[[T], U]
        ),
    ) -> Res[U, E] | Res[U, E | F]:
        return self.map(using)

    @overload
    def __irshift__(self, using: Callable[[], Res[U, F]]) -> Res[U, E | F]: ...

    @overload
    def __irshift__(self, using: Callable[[T], Res[U, F]]) -> Res[U, E | F]: ...

    @overload
    def __irshift__(self, using: Callable[[], U]) -> Res[U, E]: ...

    @overload
    def __irshift__(self, using: Callable[[T], U]) -> Res[U, E]: ...

    def __irshift__(
        self,
        using: (
            Callable[[], Res[U, F]]
            | Callable[[], U]
            | Callable[[T], Res[U, F]]
            | Callable[[T], U]
        ),
    ) -> Res[U, E] | Res[U, E | F]:
        return self.map(using)

    @overload
    def map(self, using: Callable[[], Res[U, F]]) -> Res[U, E | F]: ...

    @overload
    def map(self, using: Callable[[T], Res[U, F]]) -> Res[U, E | F]: ...

    @overload
    def map(self, using: Callable[[], U]) -> Res[U, E]: ...

    @overload
    def map(self, using: Callable[[T], U]) -> Res[U, E]: ...

    def map(
        self,
        using: (
            Callable[[], Res[U, F]]
            | Callable[[], U]
            | Callable[[T], Res[U, F]]
            | Callable[[T], U]
        ),
    ) -> Res[U, E] | Res[U, E | F]:
        """Transforms Ok value, leaving Err untouched. Same as `>>` and `>>=`.


        Args:
            using ((T) -> U, () -> U, (T) -> Res[U, F], () -> [U, F]): Func with 0 or 1 arguments that returns a value or a new Res

        Raises:
            ValueError: Raised if func contains more than one argument

        Returns:
            Res[U, E] | Res[U, E | F]: Updated Res


        #### Examples ::

            >>> ok = Res.Some(10)
            >>> err = Res[int, Nil].Nil()
            >>> # Does not work if in err
            >>> err.map(lambda x: x + 10).unwrap()
            Nil(Nil(...), 'Nothing was found')
            >>> # Change Ok value with (T) -> U function
            >>> ok.map(lambda x: x + 10).unwrap()
            20
            >>> # Replace Ok value with () -> U function
            >>> ok.map(lambda: 30).unwrap()
            30
            >>> # Replace current Res with new one using wrapped value with (T) -> Res[U, F] function
            >>> ok.map(lambda x: Res.Some(x + 10)).unwrap()
            20
            >>> # Replace current Res with new one with () -> Res[U, F] function
            >>> ok.map(lambda: Res.Some(50)).unwrap()
            50
            >>> # Works with shorthand and inplace shorthand
            >>> ok >> lambda x: x + 10
            20
            >>> ok >>= lambda x: x + 10
            >>> ok <<= unwrap
            20
        """
        sig = signature(using)
        params = list(sig.parameters.keys())
        param_len = len(params)
        for ok in self:
            if param_len == 1:
                f = cast(Callable[[T], Res[U, F] | U], using)
                out = f(ok)
            elif param_len == 0:
                f = cast(Callable[[], Res[U, F] | U], using)
                out = f()
            else:
                raise ValueError(
                    "Invalid func type. Must only contain 1 or 0 parameters."
                )

            if not isinstance(out, Res):
                return Res.Ok(out)
            return cast(Res[U, E | F], out)
        return Res[U, E | F].Err(cast(E, self.inner))

    @overload
    def __xor__(self, using: Callable[[], Res[U, F]]) -> Res[T | U, F]: ...

    @overload
    def __xor__(self, using: Callable[[E], Res[U, F]]) -> Res[T | U, F]: ...

    @overload
    def __xor__(self, using: Callable[[], F]) -> Res[T, F]: ...

    @overload
    def __xor__(self, using: Callable[[E], F]) -> Res[T, F]: ...

    def __xor__(
        self,
        using: (
            Callable[[], Res[U, F]]
            | Callable[[E], Res[U, F]]
            | Callable[[], F]
            | Callable[[E], F]
        ),
    ) -> Res[T, F] | Res[U | T, F]:
        return self.map_alt(using)

    @overload
    def __ixor__(self, using: Callable[[], Res[U, F]]) -> Res[T | U, F]: ...

    @overload
    def __ixor__(self, using: Callable[[E], Res[U, F]]) -> Res[T | U, F]: ...

    @overload
    def __ixor__(self, using: Callable[[], F]) -> Res[T, F]: ...

    @overload
    def __ixor__(self, using: Callable[[E], F]) -> Res[T, F]: ...

    def __ixor__(
        self,
        using: (
            Callable[[], Res[U, F]]
            | Callable[[E], Res[U, F]]
            | Callable[[], F]
            | Callable[[E], F]
        ),
    ) -> Res[T, F] | Res[U | T, F]:
        return self.map_alt(using)

    @overload
    def map_alt(self, using: Callable[[], Res[U, F]]) -> Res[T | U, F]: ...

    @overload
    def map_alt(self, using: Callable[[E], Res[U, F]]) -> Res[T | U, F]: ...

    @overload
    def map_alt(self, using: Callable[[], F]) -> Res[T, F]: ...

    @overload
    def map_alt(self, using: Callable[[E], F]) -> Res[T, F]: ...

    def map_alt(
        self,
        using: (
            Callable[[], Res[U, F]]
            | Callable[[E], Res[U, F]]
            | Callable[[], F]
            | Callable[[E], F]
        ),
    ) -> Res[T, F] | Res[U | T, F]:
        """Transforms the Err value, leaving Ok untouched. Sames as `^` and `^=^

        Args:
            using ((E) -> F, () -> F, (E) -> Res[U, F], (E) -> Res[U, F]): Function that takes E or nothing, returning F or Res[U, F]

        Raises:
            ValueError: Raised if function has more than one parameter

        Returns:
            Res[T, F] | Res[U | T, F]: Updated Res

        #### Examples ::

            >>> err = Res[int, Nil].Nil()
            >>> ok = Res.Some(10)
            >>> # Doesn't work on Ok values
            >>> ok.map_err(lambda e: ValueError(e)).unwrap_err()
            UnwrapErr(UnwrapErr(...), 'Unwrapped while in unexpected state')
            >>> # Change Err value with (E) -> F
            >>> err.map_err(lambda e: ValueError(e)).unwrap_err()
            ValueError('Found None while expecting something')
            >>> # Replace Err with () -> F
            >>> err.map_err(lambda: ValueError('More accurate error')).unwrap_err()
            ValueError('More accurate error')
            >>> # Replace with new Res using E with (E) -> Res[U, F]
            >>> err.map_err(lambda e: Res.Some(10)).unwrap()
            10
            >>> err.map_err(lambda e: Res.Err(Exception(str(e)))).unwrap_err()
            Exception('None was found while expecting something')
            >>> # Replace with new Res if Err with () -> Res[U, F]
            >>> err.map_err(lambda: Res.Ok(10)).unwrap()
            10
            >>> err.map_err(lambda: Res.Err(Exception('New error'))).unwrap_err()
            Exception('New error')
            >>> # XOR ^ symbol is the same as map_err
            >>> (err ^ ValueError) << unwrap_err
            ValueError('Found None while expecting something')
            >>> # ^= can do it inplace
            >>> err ^= ValueError
            >>> err <<= unwrap_err
            >>> err
            ValueError('Found None while expecting something')

        """
        sig = signature(using)
        params = list(sig.parameters.keys())
        param_len = len(params)
        if not self:
            err = cast(E, self.inner)
            if param_len == 1:
                f = cast(Callable[[E], Res[U, F] | F], using)
                out = f(err)
            elif param_len == 0:
                f = cast(Callable[[], Res[U, F] | U], using)
                out = f()
            else:
                raise ValueError(
                    "Invalid func type. Must only contain 1 or 0 parameters."
                )

            if not isinstance(out, Res):
                return Res.Err(out)
            return cast(Res[T | U, F], out)

        ok = cast(T | U, self.inner)
        return Res[T | U, F].Ok(ok)

    def convert_err(self, err_type: type[F]) -> Res[T, F]:
        """Converts an Exception of one type to another if Err

        Args:
            err_type (type[F]): Exception class used to cast into

        Returns:
            Res[T, F]: A new Res with an updated Err value

        #### Examples ::

            >>> ok: Res[int, Exception] = Res.Ok(10)
            >>> ok.convert_err(ValueError).unwrap()
            10
            >>> err: Res[int, Exception] = Res.Err(Exception("foo"))
            >>> err.convert_err(ValueError).unwrap_err()
            ValueError('foo')

        """
        match self:
            case Res(e, False):
                return Res[T, F].Err(err_type(str(e)))
            case Res(t):
                return Res[T, F].Ok(cast(T, t))

    @overload
    def do(self, using: Callable[[T], U]) -> Res[T, E]: ...

    @overload
    def do(self, using: Callable[[], U]) -> Res[T, E]: ...

    def do(self, using: Callable[[T], U] | Callable[[], U]) -> Res[T, E]:
        """Runs a function over inner if Ok, but stays the same

        Args:
            using (Callable[[T], U]): Function taking `inner` returning something else

        Returns:
            Res[T, E]: The same `Res`

        #### Examples ::

            >>> ok: Res[int, Exception] = Res.Ok(10)
            >>> ok.do(lambda x: x + 10).unwrap()
            10
            >>> err: Res[int, Exception] = Res.Err(Exception("foo"))
            >>> err.do(lambda x: x + 10).unwrap()
            Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
            Exception: foo

        """

        self.map(using)
        return self

    @overload
    def do_err(self, using: Callable[[E], U]) -> Res[T, E]: ...

    @overload
    def do_err(self, using: Callable[[], U]) -> Res[T, E]: ...

    def do_err(self, using: Callable[[], U] | Callable[[E], U]) -> Res[T, E]:
        """Runs a function over inner if Err, but stays the same

        Args:
            using (Callable[[E], U]): Function taking Exception returning something else

        Returns:
            Res[T, E]: The same `Res`

        #### Examples ::

            >>> ok: Res[int, Exception] = Res.Ok(10)
            >>> ok.do_err(lambda e: str(e)).unwrap_err()
            Traceback (most recent call last):
            File "stdin", line 1, in <module>
            res.UnwrapError: (UnwrapError(...), 'Unwrapped Err while in Ok state')
            >>> err: Res[int, Exception] = Res.Err(Exception("foo"))
            >>> err.do_err(str).unwrap_err()
            Exception('foo')

        """

        match self:
            case Res(e, False):
                err = cast(E, e)
                f = cast(Callable[[E], U], using)
                try:
                    f(err)
                except TypeError as e:
                    f = cast(Callable[[], U], using)
                    f()
                finally:
                    return Res[T, E].Err(err)
            case Res(t):
                return Res[T, E].Ok(cast(T, t))

    @property
    def u(self) -> tuple[T | None, E | None]:
        """Shorthand for unpack

        #### Examples ::

            >>> ok: Res[int, Exception] = Res.Ok(10)
            >>> val, err = ok.u
            >>> val
            10
            >>> err is None
            True
            >>> err: Res[int, Exception] = Res.Err(Exception("foo"))
            >>> val, err = err.u
            >>> val is None
            True
            >>> err
            Exception('foo')

        """
        return self.unpack()

    def to_dict(self) -> ResDict[T, E]:
        """Converts to a typed dictionary with current data and type info

        Useful for when you need to pickle or serialize a Res

        Returns:
            ResDict[T, E]: The dictionary version of the Res

        #### Examples ::

            >>> ok: Res[int, Nil] = Res.Some(10)
            >>> res_dict: ResDict[int, Nil] = ok.to_dict()
            >>> res_dict["is_ok"]
            True
            >>> res_dict["ok"]
            10
            >>> res_dict["err"] is None
            True

        """
        if not self:
            return ResDict[T, E](ok=None, err=cast(E, self.inner), is_ok=False)
        return ResDict[T, E](ok=cast(T, self.inner), err=None, is_ok=True)

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

        #### Examples ::

            >>> res_dict: ResDict[int, Nil] = ResDict(ok=10, err=None, is_ok=True)
            >>> res_dict["is_ok"]
            True
            >>> res_dict["ok"]
            10
            >>> res_dict["err"] is None
            True
            >>> res: Res[int, Nil] = Res.from_dict(res_dict)
            >>> res.is_ok
            True
            >>> res.is_err
            False
            >>> res.unwrap()
            10

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


def catch_all(using: Callable[P, U]):
    """Decorator that catches all `Exception` bound errors and returns a `Res`

    Args:
        using (Callable[P, U]): Function that takes params and returns a value

    Returns:
        Callable[P, Res[U, Exception]]: A function that takes parameters and returns `Res[U, Exception]`
    """

    @safe(Exception)
    def inner(*args: P.args, **kwargs: P.kwargs) -> U:
        return using(*args, **kwargs)

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
            except err_types:
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

        >>> @combine_errors(Nil)
        ... @safe(KeyError, IndexError)
        ... def get(index: str, data: dict[str, str]) -> str:
        ...     return data[index]
        ...
        >>> data: dict[str, str] = {'hello': 'world'}
        >>> element: Opt[str] = get('hola', data)
        >>> element.unwrap_err()
        Nil(Nil(...), 'Found None while expecting something')

    """

    def inner(using: Callable[P, Res[T, E]]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[T, F]:
            return using(*args, **kwargs).map_alt(
                lambda e: to(str(e)) if inherit_message else to()
            )

        return wrapper

    return inner


def unwrap_err(subj: Res[T, E]) -> E:
    """Returns wrapped E if Err, else Panics with UnwrapError

    Args:
        subj (Res[T, E]): A Res

    Returns:
        E: Wrapped E value

    #### Examples ::

        >>> ok = Res.Ok(10)
        >>> ok << unwrap_err
        Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
        res.UnwrapError: (UnwrapError(...), 'Unwrapped Err while in Ok state')
        >>> err = Res.Err(Exception("foo"))
        >>> err << unwrap_err
        Exception('foo')
    """
    return subj.unwrap_alt()


def is_ok(subj: Res[T, E]) -> bool:
    """Indicates if Res is okay

    Args:
        subj (Res[T, E]): A Res

    Returns:
        bool: True if Ok else False

    #### Examples ::

        >>> ok = Res.Some(10)
        >>> ok << is_ok
        True
        >>> err = Res.Nil()
        >>> err << is_err
        False
    """
    return bool(subj)


def ok_and(predicate: Callable[[T], bool]):
    """Indicates if Ok and predicate returns True

    Args:
        predicate (Callable[[T], bool]): Function that takes Ok value and returns True or False

    Returns:
        (Res[T, E]) -> bool: Function that will test Res using predicate

    #### Examples ::

        >>> ok = Res.Some(10)
        >>> ok << ok_and(lambda t: t > 5)
        True
        >>> ok_and(lambda t: t > 20)(ok)
        False
        >>> err = Res.Nil()
        >>> is_true = err << ok_and(lambda t: t > 5)
        >>> is_true
        False
        >>> err <<= ok_and(lambda t: t > 20)
        >>> err
        False
    """

    def inner(subj: Res[T, E]) -> bool:

        if subj:
            return predicate(cast(T, subj.inner))
        return False

    return inner


def is_err(subj: Res[T, E]) -> bool:
    """Indicates if Err

    Args:
        subj (Res[T, E]): Res to check

    Returns:
        bool: True if Err, else False

    #### Examples ::

        >>> ok = Res.Some(10)
        >>> ok << is_err
        False
        >>> err = Res.Some(10)
        >>> err << is_err
        True
    """
    return not bool(subj)


def err_and(predicate: Callable[[E], bool]):
    """Checks predicate against Res if Err

    Args:
        predicate (Callable[[E], bool]): Condition to check the Err against

    Returns:
        (Res[T, E]) -> bool: Func that takes Res and returns bool

    #### Examples ::

        >>> ok = Res.Some(10)
        >>> is_nil = lambda e: isinstance(e, Nil)
        >>> ok << err_and(is_nil)
        False
        >>> err = Res.Nil()
        >>> err << err_and(is_nil)
        True
        >>> err = Res.Err(ValueError(""))
        >>> err << err_and(is_nil)
        False

    """

    def inner(subj: Res[T, E]) -> bool:

        if not subj:
            return predicate(cast(E, subj.inner))
        return False

    return inner


def expect(message: str):
    """Unwraps a Res, panicing with the message if Err

    Args:
        message (str): Message to be shown if it panics

    Raises:
        ExpectError: Error raised if Err with message inside

    Returns:
        ((Res[T, E])) -> T: Func that returns Ok val from Res

    #### Examples ::

        >>> ok = Res.Some(10)
        >>> ok << expect("Didn't expect the spanish inquisition")
        10
        >>> err = Res.Nil()
        >>> err << expect('Hello there')
        Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
        ExpectErrror(ExpectError(...), 'Hello there')
    """

    def inner(subj: Res[T, E]) -> T:

        return subj.expect(message)

    return inner


def expect_err(message: str):
    """Unwraps a Res, panicing with the message if Ok

    Args:
        message (str): Message to be shown if it panics

    Raises:
        ExpectError: Error raised if Ok with message inside

    Returns:
        ((Res[T, E])) -> T: Func that returns Ok val from Res

    #### Examples ::

        >>> err = Res.Nil()
        >>> err << expect_err("Didn't expect the spanish inquisition")
        10
        >>> ok = Res.Some(10)
        >>> ok << expect_err('Hello there')
        Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
        ExpectErrror(ExpectError(...), 'Hello there')
    """

    def inner(subj: Res[T, E]) -> E:

        return subj.expect_err(message)

    return inner


def convert_err(err_type: type[F]):
    """Changes Exceptions between types if possible

    Args:
        err_type (type[F]): Exception child that will inherit current Err value

    Returns:
        ((E) -> F): New Exception instance

    #### Examples ::

        >>> err = Res.Nil()
        >>> err ^= convert_err(ValueError)
        >>> err <<= unwrap_err
        ValueError('Found None while expecting something')
    """

    def inner(e: E) -> F:  # type: ignore
        return err_type(str(e))

    return inner

