from __future__ import annotations
from typing_extensions import override
from typing import (
    ParamSpec,
    TypeVar,
    Generic,
    TypeAlias,
    cast,
    Callable,
    NoReturn,
    overload,
)
from functools import wraps
from abc import ABC, abstractmethod
from dataclasses import dataclass

P = ParamSpec("P")
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")
L = TypeVar("L")
M = TypeVar("M")
R = TypeVar("R")
S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class UnwrapError(ValueError):
    def __init__(
        self,
        message: str = "Attempted to unwrap a value that did not have the expected state",
    ):
        super().__init__(message)


class ExpectError(ValueError):
    def __init__(
        self,
        message: str = "Attempted to unwrap a value that did not have the expected state",
    ):
        super().__init__(message)


class Nil(Exception):
    """Error class used to represent an unexpected `None` value.

    Using ``Ok[T] | Err[Nil]`` replaces using ``T | None`` to represent potential
    null values.

    """

    def __init__(self, message: str = "Did not expect None"):
        super().__init__(message)


@dataclass(
    frozen=True,
    match_args=True,
    init=True,
    repr=True,
    slots=True,
    eq=True,
    order=True,
    unsafe_hash=True,
)
class BaseChoice(Generic[L], ABC):
    inner: L

    @staticmethod
    @abstractmethod
    def new(val: U):
        ...

    @staticmethod
    @abstractmethod
    def new_pair(val: U, opposite_type: type[V]):
        ...

    @abstractmethod
    def swap(self):
        ...

    @abstractmethod
    def unwrap(self):
        ...

    @abstractmethod
    def unwrap_or(self, default: L):
        ...

    @abstractmethod
    def unwrap_or_else(self, on_err: Callable[[R], L]):
        ...

    @abstractmethod
    def unwrap_other(self):
        ...

    @abstractmethod
    def map(self, op: Callable[[L], U]):
        ...

    @abstractmethod
    def map_or(self, op: Callable[[L], U], default: U):
        ...

    @abstractmethod
    def map_other(self, op: Callable[[R], U]):
        ...

    @abstractmethod
    def map_or_else(self, op: Callable[[L], U], default: Callable[[], U]):
        ...

    @abstractmethod
    def and_then(self, op: Callable[[L], Either[U, R]]):
        ...

    @abstractmethod
    def or_else(self, op: Callable[[R], Either[L, S]]):
        ...

    @abstractmethod
    def and_(self, res: Either[U, R]):
        ...

    @abstractmethod
    def or_(self, res: Either[L, U]):
        ...

    @abstractmethod
    def expect(self, message: str):
        ...

    @abstractmethod
    def expect_other(self, message: str):
        ...

    @abstractmethod
    def is_not_other(self) -> bool:
        ...

    @abstractmethod
    def is_other(self) -> bool:
        ...

    @abstractmethod
    def is_not_other_and(self, predicate: Callable[[L], bool]) -> bool:
        return predicate(self._inner)

    @abstractmethod
    def is_other_and(self, predicate: Callable[[R], bool]) -> bool:
        return False

    @abstractmethod
    def do(self, op: Callable[[L], U]):
        ...

    @abstractmethod
    def do_other(self, op: Callable[[R], S]):
        ...

    @property
    @abstractmethod
    def q(self):
        ...


class Left(BaseChoice[L]):
    """Container for the left value

    Attributes:
        inner (L): The wrapped value

    ## Example

    >>> match Left(str)(10):
    ...     case Left(inner):
    ...         inner
    10

    """

    inner: L

    @staticmethod
    def new(val: M) -> Left[M]:
        return Left(val)

    @staticmethod
    def new_pair(val: U, opposite_type: type[R]) -> Either[U, R]:
        return cast(Either[U, R], Left(val))

    def swap(self):
        return Right.new(self.inner)

    def unwrap(self):
        return self.inner

    def unwrap_or(self, default: L):
        return self.inner

    def unwrap_or_else(self, on_err: Callable[[R], L]):
        return self.inner

    def unwrap_other(self):
        raise UnwrapError(f"Attempted to unwrap expecting Right, but found {self}")

    def map(self, op: Callable[[L], M]):
        return self.new(op(self.inner))

    def map_or(self, op: Callable[[L], M], default: M):
        return self.map(op)

    def map_or_else(self, op: Callable[[L], M], default: Callable[[], M]):
        return self.map(op)

    def map_other(self, op: Callable[[R], S]):
        return self.new(self.inner)

    def and_(self, new_val: Either[M, R]) -> Left[M]:
        return new_val

    def and_then(self, op: Callable[[L], Either[M, R]]) -> Left[M]:
        return op(self.inner)

    def or_(self, new_val: Left[L] | Right[S]):
        return self.new(self.inner)

    def or_else(self, op: Callable[[R], Either[L, S]]):
        return self.new(self.inner)

    def expect(self, message: str) -> L:
        return self.inner

    def expect_other(self, message: str) -> NoReturn:
        raise ExpectError(message)

    def is_not_other(self) -> bool:
        return True

    def is_other(self) -> bool:
        return False

    def is_not_other_and(self, predicate: Callable[[L], bool]) -> bool:
        return predicate(self.inner)

    def is_other_and(self, predicate: Callable[[R], bool]) -> bool:
        return False

    def do(self, op: Callable[[L], M]):
        op(self.inner)
        return self.new(self.inner)

    def do_other(self, op: Callable[[R], S]):
        return self.new(self.inner)

    @property
    def q(self) -> L:
        return self.unwrap()


class Right(BaseChoice[R]):
    """Container for the right value

    Attributes:
        inner (R): The wrapped value

    ## Example

    >>> match Right(str)(10):
    ...     case Right(inner):
    ...         inner
    10

    """

    inner: R

    @staticmethod
    def new(val: S) -> Right[S]:
        return Right(val)

    @staticmethod
    def new_pair(val: S, opposite_type: type[L]) -> Either[L, S]:
        return cast(Either[L, S], Right(val))

    def swap(self):
        return Left(self.inner)

    def unwrap(self):
        raise UnwrapError(f"Unwrapped a {self} while expecting Left")

    def unwrap_or(self, default: L):
        return default

    def unwrap_or_else(self, on_err: Callable[[R], L]) -> L:
        return on_err(self.inner)

    def unwrap_other(self) -> R:
        return self.inner

    def expect(self, message: str) -> NoReturn:
        raise ExpectError(message)

    def expect_other(self, message: str) -> R:
        return self.inner

    def map(self, op: Callable[[L], M]):
        return self.new(self.inner)

    def map_or(self, op: Callable[[L], M], default: M):
        return Left(default)

    def map_or_else(self, op: Callable[[L], M], default: Callable[[], M]):
        return Left(default())

    def map_other(self, op: Callable[[R], S]):
        return self.new(op(self.inner))

    def and_then(self, op: Callable[[L], Either[M, R]]):
        return self.new(self.inner)

    def and_(self, new_val: Left[M] | Right[R]):
        return self.new(self.inner)

    def or_(self, new_val: Left[L] | Right[S]) -> Right[S]:
        return new_val

    def or_else(self, op: Callable[[R], Left[L] | Right[S]]) -> Right[S]:
        return op(self.inner)

    def is_not_other(self) -> bool:
        return False

    def is_other(self) -> bool:
        return True

    def is_not_other_and(self, predicate: Callable[[L], bool]) -> bool:
        return False

    def is_other_and(self, predicate: Callable[[R], bool]) -> bool:
        return predicate(self.inner)

    def do(self, op: Callable[[L], U]):
        return self.new(self.inner)

    def do_other(self, op: Callable[[R], S]):
        op(self.inner)
        return self.new(self.inner)

    @property
    def q(self) -> NoReturn:
        return self.unwrap()


Either: TypeAlias = Left[L] | Right[R]


class Ok(Left[T]):
    inner: T

    @staticmethod
    def new(val: U) -> Ok[U]:
        return Ok(val)

    @staticmethod
    def new_pair(val: U, opposite_type: type[E]) -> Ok[U] | Err[E]:
        return cast(Ok[U] | Err[E], Ok(val))

    def swap(self):
        return Err(Nil(f"{self} was swapped for Err[Nil]"))

    def some(self) -> Opt[T]:
        if self.inner is not None:
            return self.new(self.inner)
        return Err(Nil())
    
    @override
    def map(self, op: Callable[[T], U]) -> Ok[U]:
        return super().map(op)
    
    @override
    def map_or(self, op: Callable[[T], U], default: U) -> Ok[U]:
        return super().map_or(op, default)

    @override
    def map_or_else(self, op: Callable[[T], U], default: Callable[[], U]) -> Ok[U]:
        return super().map_or_else(op, default)

    @override
    def map_other(self, op: Callable[[E], F]) -> Ok[T]:
        return super().map_other(op)

    @override
    def and_(self, new_val: Res[U, E]) -> Ok[U]:
        return super().and_(new_val)

    @override
    def and_then(self, op: Callable[[T], Res[U, E]]) -> Ok[U]:
        return super().and_then(op)

    @override
    def or_(self, new_val: Res[T, F]) -> Ok[T]:
        return super().or_(new_val)

    @override
    def or_else(self, op: Callable[[F], Res[T, F]]) -> Ok[T]:
        return super().or_else(op)

    @override
    def do(self, op: Callable[[T], U]) -> Ok[T]:
        return super().do(op)

    @override
    def do_other(self, op: Callable[[E], U]) -> Ok[T]:
        return super().do_other(op)
    

class Err(Right[E]):
    inner: E

    def __post_init__(self, inner: E) -> None:
        if not isinstance(inner, Exception):
            raise TypeError(
                f"Expected value to inherit from Exception but found {inner}"
            )

    @staticmethod
    def new(val: F) -> Err[F]:
        return Err(val)

    @staticmethod
    def new_pair(val: F, opposite_type: type[T]) -> Ok[T] | Err[F]:
        return cast(Ok[T] | Err[F], Err(val))

    def swap(self):
        return Ok(self.inner)

    def some(self):
        return Err(Nil())

    @override
    def map(self, op: Callable[[T], U]) -> Err[E]:
        return super().map(op)

    @override
    def map_or(self, op: Callable[[T], U], default: U) -> Ok[U]:
        return super().map_or(op, default)

    @override
    def map_or_else(self, op: Callable[[T], U], default: Callable[[], U]) -> Ok[U]:
        return super().map_or_else(op, default)

    @override
    def map_other(self, op: Callable[[E], F]) -> Err[F]:
        return super().map_other(op)

    @override
    def and_(self, new_val: Res[U, E]) -> Err[E]:
        return super().and_(new_val)

    @override
    def and_then(self, op: Callable[[T], Res[U, E]]) -> Err[E]:
        return super().and_then(op)

    @override
    def or_(self, new_val: Res[T, F]) -> Err[F]:
        return super().or_(new_val)

    @override
    def or_else(self, op: Callable[[E], Res[T, F]]) -> Err[F]:
        return super().or_else(op)

    @override
    def do(self, op: Callable[[T], U]) -> Err[E]:
        return super().do(op)

    @override
    def do_other(self, op: Callable[[E], U]) -> Err[E]:
        return super().do_other(op)


Res: TypeAlias = Ok[L] | Err[R]
"""Convenient type alias for a value that could be Ok or Err"""

Opt: TypeAlias = Res[T, Nil]
"""Type alias for ``Res[T, Nil]``. Useful for quick annotations and types.

Example: ::

    >>> maybe_int: Opt[int] = some(10)

"""


@overload
def unpack(value: Either[L, R]) -> tuple[L | None, R | None]:
    ...


@overload
def unpack(value: Res[T, E]) -> tuple[T | None, R | None]:
    ...


def unpack(value: Either[L, R] | Res[T, E]):
    match value:
        case Left(left):
            return left, None
        case Right(right):
            return None, right
        case Ok(ok):
            return ok, None
        case Err(err):
            return None, err
        case _:
            raise ValueError(f"Expected a child of BaseChoice but found {value}")


def left(func: Callable[P, U]):
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        return Left(func(*args, **kwargs))

    return wrapper


def right(func: Callable[P, U]):
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        return Right(func(*args, **kwargs))

    return wrapper


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

    Examples: ::

        >>> @safe(KeyError)
        ... def access(data: dict[str, str], key: str) -> str:
        ...     return data[key]
        ...
        >>> data: dict[str, str] = {'hello': 'world'}
        >>> element: Res[str, KeyError] = access(data, 'hello')
        >>> unwrap(element)
        'world'
        >>> bad_element: Res[str, KeyError] = access(data, 'hola')
        >>> unwrap_err(bad_element)
        KeyError('hola')

    """

    def inner(using: Callable[P, U]) -> Callable[P, Res[U, E]]:
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[U, E]:
            try:
                return Ok.new_pair(using(*args, **kwargs), E)
            except err_type as e:
                return Err.new_pair(e, U)

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
        >>> unwrap(maybe)
        'world'

    """

    @wraps(using)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Opt[U]:
        return Ok(using(*args, **kwargs)).some()

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
        >>> unwrap(maybe)
        'world'
    """

    def inner(using: Callable[P, T | None]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Opt[T]:
            try:
                return Ok(using(*args, **kwargs)).some()
            except err_types as e:
                return Err.new_pair(Nil(str(e)), T)

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
        ... @safe(KeyError, IndexError)
        ... def get(index: str, data: dict[str, str]) -> str:
        ...     return data[index]
        ...
        >>> data: dict[str, str] = {'hello': 'world'}
        >>> element: Opt[str] = get('hola', data)
        >>> unwrap_err(element)
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

