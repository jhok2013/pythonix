"""Immutable types and functions to catch and handle nulls and Exceptions

Inspired by Rust and Gleam.

Features utilities like mapping, unwrapping, decorators for catching None
values and Exceptions.

Examples:

    Automatic Error Catching: ::

        >>> @safe(KeyError)
        ... def get_foo(data: dict[str, str]) -> str:
        ...     return data['foo']
        ...
        >>> @null_safe
        ... def get_bar(data: dict[str, str]) -> str | None:
        ...     return data.get('bar')
        ...
        >>> @null_and_error_safe(KeyError)
        ... def get_far(data: dict[str, str]) -> str | None:
        ...     return data['far']
        ...

    Error Combining: ::

        >>> @combine_errors(Nil())
        ... @safe(KeyError, IndexError)
        ... def get_baz(data: dict[str, str]) -> str:
        ...     return data['baz']
        ...

And much, much more. Everything has its own documentation so check it out.
    
"""
from functools import wraps
from dataclasses import dataclass
from abc import ABC
from typing import (
    Tuple,
    TypeVar,
    Generic,
    cast,
    ParamSpec,
    Callable,
    TypeAlias,
)

P = ParamSpec("P")

NotResError = TypeError("Must pass in an Ok or Err")
UnwrapErr = ValueError("Attempted to retrieve an Err from an Ok")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")
G = TypeVar("G", bound="Exception")


class BaseRes(Generic[T], ABC):
    """Base class for use by Ok and Err"""

    inner: T


class Nil(Exception):
    """Error class used to represent an unexpected `None` value.

    Using ``Ok[T] | Err[Nil]`` replaces using ``T | None`` to represent potential
    null values.

    """

    def __init__(self, message: str = "Did not expect None"):
        super().__init__(message)

@dataclass(frozen=True)
class Ok(BaseRes, Generic[T]):
    """Represents a successful outcome of a function that could have failed.

    Useful for pattern matching on a function that returns `Ok[T] | Err[E]`.
    Inner values can be unpacked like a tuple.

    Note:
        The preferred constructor is ``ok`` as it will preserve type information

    Examples: ::

        >>> match ok(ValueError)(5):
        ...     case Ok(val):
        ...         val
        ...     case Err(e):
        ...         raise e
        ...
        5

    """
    inner: T
    __match_args__ = ('inner',)


@dataclass(frozen=True)
class Err(BaseRes, Generic[E]):
    """Represents a successful outcome of a function that could have failed.

    Useful for pattern matching on a function that returns `Ok[T] | Err[E]`.
    Contained value must be a subclass of ``Exception``.

    Note:
        The preferred constructor is ``err``, as it preserves type information

    Example: ::

        >>> match err(int)(ValueError("foo")):
        ...     case Ok(val):
        ...         val
        ...     case Err(e):
        ...         str(e)
        'foo'

    """
    __match_args__ = ('inner',)
    inner: E

Res: TypeAlias = Ok[T] | Err[E]
"""Convenient type alias for a value that could be Ok or Err"""

def unpack(res: Res[T, E]) -> Tuple[T | None, E | None]:
    """Unpack a reuslt in a Go like way to make error handling simple
    
    Examples: ::

        >>> val, err = unpack(ok(ValueError)(10))
        >>> val
        10
        >>> err is None
        True
    
    """
    match res:
        case Ok(t):
            return t, None
        case Err(e):
            return None, e
        case _:
            raise NotResError

Opt: TypeAlias = Res[T, Nil]
"""Type alias for ``Res[T, Nil]``. Useful for quick annotations and types.

Example: ::

    >>> maybe_int: Opt[int] = some(10)

"""


def err(ok_type: type[T]) -> Callable[[E], Res[T, E]]:
    """Creates an ``Err[E]`` while also providing type information for ``Ok[T]``

    Use this rather than manually instantiating ``Ok`` or ``Err``.
    Contained value must be a subclass of ``Exception``.

    Example: ::

        >>> match err(int)(ValueError("foo")):
        ...     case Ok(val):
        ...         val
        ...     case Err(e):
        ...         str(e)
        'foo'

    """

    def get_err(err_obj: E) -> Res[T, E]:
        return cast(Res[T, E], Err(err_obj))

    return get_err


def ok(err_type: type[E]) -> Callable[[T], Res[T, E]]:
    """Creates an ``Ok[T]`` while also providing type information for ``Err[E]``

    Use this rather than manually instantiating ``Ok`` or ``Err``.

    Example: ::

        >>> match ok(ValueError)(5):
        ...     case Ok(val):
        ...         val
        ...     case Err(e):
        ...         raise e
        ...
        5

    """

    def get_err(ok_obj: T) -> Res[T, E]:
        """
        Sets the `Err` type of the `Res`
        """
        return cast(Res[T, E], Ok(ok_obj))

    return get_err


def some(inner: T | None) -> Opt[T]:
    """Converts a potentially None value to a result Res[T, Nil]

    Use this to put potentially null values into the ``res`` ecosystem
    for easy and pragmatic handling.

    Examples: ::

        >>> d = {"hello": "world"}
        >>> some_val = some(d.get("hello"))
        >>> match some_val:
        ...     case Ok(val):
        ...         val
        ...     case Err(Nil()):
        ...         ...
        ...
        'world'

    """
    if inner is not None:
        return Ok(inner)
    return Err(Nil())


def is_ok(res: Res[T, E]) -> bool:
    """Return `True` if the `Res` is `Ok`, else ``False``

    Another easy way to see if a result is ``Ok`` or ``Err``

    Args:
        *res* (Res[T, E]): Any result, ``Ok`` or ``Err``

    Returns:
        *output* (bool): True if ``Ok``, else ``False``

    Examples: ::

        >>> outcome: Res[int, ValueError] = ok(ValueError)(10)
        >>> is_ok(outcome)
        True

    """
    match res:
        case Ok():
            return True
        case Err():
            return False
        case _:
            raise NotResError


def is_err(res: Res[T, E]) -> bool:
    """Return ``True`` if the ``Res`` is ``Err``, else ``True``

    Another easy way to see if a result is ``Err`` or ``Ok``

    Args:
        *res* (Res[T, E]): Any result, ``Ok`` or ``Err``

    Returns:
        *output* (bool): ``True`` if ``Err``, else ``False``

    Example: ::

        >>> outcome: Res[int, ValueError] = err(int)(ValueError())
        >>> is_err(outcome)
        True

    """
    match res:
        case Ok():
            return False
        case Err():
            return True
        case _:
            raise NotResError


def is_ok_and(predicate: Callable[[T], bool]) -> Callable[[Res[T, E]], bool]:
    """Return `True` if the `Res` is `Ok` and the `predicate` evaluates to `True`

    Args:
        *predicate* ((T) -> bool): Func to be evaluated against inner
        *res* (Res[T, E]): Result of ``Ok`` or ``Err``

    Returns:
        *output* (bool): ``True`` if ``Ok`` and *predicate* evaluates to ``True``

    Example: ::

        >>> outcome: Res[int, ValueError] = ok(ValueError)(10)
        >>> is_ok_and(lambda x: x > 2)(outcome)
        True

    """

    def inner(res: Res[T, E]) -> bool:
        match res:
            case Ok(t):
                return predicate(t)
            case Err():
                return False
            case _:
                raise NotResError

    return inner


def is_err_and(predicate: Callable[[E], bool]) -> Callable[[Res[T, E]], bool]:
    """Return `True` if the `Res` is `Err` and the *predicate* evaluates to `True`

    Args:
        *predicate* ((E) -> bool): Func to be evaluated against inner
        *res* (Res[T, E]): Result of ``Ok`` or ``Err``

    Returns:
        *output* (bool): ``True`` if ``Err`` and *predicate* evaluates to ``True``

    Example: ::

        >>> outcome: Res[int, ValueError] = err(int)(ValueError('foo'))
        >>> is_err_and(lambda e: str(e) == 'foo')(outcome)
        True

    """

    def inner(res: Res[T, E]) -> bool:
        match res:
            case Ok():
                return False
            case Err(e):
                return predicate(e)
            case _:
                raise NotResError

    return inner


def unwrap(res: Res[T, E]) -> T:
    """Returns the wrapped value if ``Ok``, or will raise the exception if ``Err``.

    Avoid using this if possible unless wrapped in ``safe`` decorator with a
    matching Exception being caught, or unless you know the output is ``Ok`` with
    ``is_ok`` or ``is_err``.

    Args:
        *res* (Res[T, E]): ``Ok`` or ``Err`` to be unwrapped

    Returns:
        *output* (T): Contained value from ``Ok``

    Example:

        If Ok: ::

            >>> res: Res[int, ValueError] = ok(ValueError)(10)
            >>> unwrap(res)
            10

        If Err: ::

            >>> res: Res[int, ValueError] = err(int)(ValueError())
            >>> unwrap(res)
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
                raise e
            ValueError
    """
    match res:
        case Ok(value):
            return cast(T, value)
        case Err(e):
            raise e
        case _:
            return False


def unwrap_or(default: T) -> Callable[[Res[T, E]], T]:
    """Return the `Ok` value if `Ok`, else return the default

    Args:
        *default* (T): The value to be returned if ``Err``
        *res* (Res[T, E]): The ``Ok`` or ``Err``

    Returns:
        *output* (T): The default, or value from the ``Ok``

    Example: ::

        >>> _ok_res: Res[int, ValueError] = ok(ValueError)(10)
        >>> unwrap_or(0)(_ok_res)
        10
        >>> _err_res: Res[int, ValueError] = err(int)(ValueError())
        >>> unwrap_or(0)(_err_res)
        0

    """

    def inner(res: Res[T, E]) -> T:
        match res:
            case Ok(val):
                return val
            case Err():
                return default
            case _:
                raise NotResError

    return inner


def unwrap_or_else(on_err: Callable[[], T]) -> Callable[[Res[T, E]], T]:
    """Return the `Ok` value if `Ok`, else run the `on_err` function
    that returns the same type.

    Args:
        *on_err* (() -> T): Callback func for if ``Err``
        *res* (Res[T, E]): Result of ``Ok`` or ``Err``

    Returns:
        *output* (T): The wrapped value, or default value of the same type

    Examples: ::

        >>> ok_outcome: Res[int, ValueError] = ok(ValueError)(10)
        >>> on_err = lambda: 0
        >>> unwrap_or_else(on_err)(ok_outcome)
        10
        >>> err_outcome: Res[int, ValueError] = err(int)(ValueError('foo'))
        >>> unwrap_or_else(on_err)(err_outcome)
        0

    """

    def inner(res: Res[T, E]) -> T:
        match res:
            case Ok(val):
                return val
            case Err():
                return on_err()
            case _:
                raise NotResError

    return inner


def unwrap_err(result: Res[T, E]) -> E:
    """Returns the wrapped Exception if ``Err``, or panice if ``Ok``.

    Avoid using this if possible unless wrapped in ``safe`` decorator with a
    matching Exception being caught, or unless you know the output is ``Ok`` with
    ``is_ok`` or ``is_err``.

    Args:
        *res* (Res[T, E]): ``Ok`` or ``Err`` to be unwrapped

    Returns:
        *output* (T): Contained value from ``Ok``

    Examples:

        If Ok: ::

            >>> res: Res[int, ValueError] = ok(ValueError)(10)
            >>> unwrap_err(res)
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
                raise e
            ValueError: Attempted to retrieve an Err from an Ok

        If Err: ::

            >>> res: Res[int, ValueError] = err(int)(ValueError())
            >>> unwrap_err(res)
            ValueError()

    """
    match result:
        case Ok():
            raise UnwrapErr
        case Err(e):
            return e
        case _:
            raise NotResError


def map(using: Callable[[T], U]) -> Callable[[Res[T, E]], Res[U, E]]:
    """Run the function on the `Ok` if `Ok`, else return the current `Err`

    Useful for conditionally transforming ``Res`` values, independent of their
    state.

    Note:
        This will only transform the ``Ok``, not the ``Err`` value

    Args:
        *using* ((T) -> U): Function to be ran on the ``Ok`` inner value if ``Ok``
        *res* (Res[T, E]): An ``Ok[T]`` or ``Err[E]``, a.k.a ``Res[T, E]``

    Returns:
        *output* (Res[U, E]): A new result with the updated ``Ok`` value

    Examples: ::

        >>> ok_outcome: Res[int, ValueError] = ok(ValueError)(10)
        >>> mapped_ok: Res[str, ValueError] = map(str)(ok_outcome)
        >>> unwrap(mapped_ok)
        '10'
        >>> err_outcome: Res[int, ValueError] = err(int)(ValueError())
        >>> mapped_err: Res[str, ValueError] = map(str)(err_outcome)
        >>> unwrap(mapped_err)
        Traceback (most recent call last):
            unwrap(mapped_err)
            raise e
        ValueError

    """

    def inner(res: Res[T, E]) -> Res[U, E]:
        match res:
            case Ok(t):
                return Ok(using(t))
            case Err(e):
                return Err(e)
            case _:
                raise NotResError

    return inner


def map_or(using: Callable[[T], U]) -> Callable[[U], Callable[[Res[T, E]], Res[U, E]]]:
    """Runs the function on the `Ok` or return the `default` if `Err`

    Args:
        *using* ((T) -> U): Function that takes the wrapped ``Ok`` value, and returns another
        *default* (U): Default value that is the same type as what *using* would return

    Returns:
        *output* (Res[U, E]): Updated ``Ok`` value, or ``Err``

    Examples: ::

        >>> ok_outcome: Res[int, ValueError] = ok(ValueError)(10)
        >>> err_outcome: Res[int, ValueError] = err(int)(ValueError())
        >>> unwrap_or(0)(ok_outcome)
        10
        >>> unwrap_or(0)(err_outcome)
        0

    """

    def get_default(
        default: U,
    ) -> Callable[[Res[T, E]], Res[U, E]]:
        def inner(res: Res[T, E]) -> Res[U, E]:
            match res:
                case Ok(t):
                    return Ok(using(t))
                case Err():
                    return Ok(default)
                case _:
                    raise NotResError

        return inner

    return get_default


def map_err(using: Callable[[E], F]) -> Callable[[Res[T, E]], Res[T, F]]:
    """Runs the function on the `ErrVal` if in `Err` or returns the current `Ok`

    Useful for converting Exceptions from one type to another.

    Args:
        *using* ((E) -> F): Function that takes an Exception and returns an Exception
        *res* (Res[T, E]): An ``Ok`` or ``Err``

    Returns:
        *output* (Res[T, F]): Result with an updated ``Err`` value

    Examples: ::

        >>> err_outcome: Res[int, ValueError] = err(int)(ValueError())
        >>> to_type_error = lambda e: TypeError(str(e))
        >>> mapped_err: Res[int, TypeError] = map_err(to_type_error)(err_outcome)
        >>> unwrap_err(mapped_err)
        TypeError('')

    """

    def inner(res: Res[T, E]) -> Res[T, F]:
        match res:
            case Err(e):
                return Err(using(e))
            case Ok(t):
                return Ok(t)
            case _:
                raise NotResError

    return inner


def map_or_else(
    using: Callable[[T], U]
) -> Callable[[Callable[[], U]], Callable[[Res[T, E]], Res[U, E]]]:
    """Runs the provided function if `Ok`, or runs the default function if `Err`

    Args:
        *using* ((T) -> U): Func that takes and returns a value
        *default* (() -> U): Func that returns a default value of the same type
        *res* (Res[T, E]): A result of ``Ok`` or ``Err``

    Returns:
        *output* (Res[U, E]): New result with updated ``Ok``

    Examples: ::

        >>> ok_outcome: Res[int, Nil] = some(10)
        >>> default = lambda: '0'
        >>> mapped_ok: Res[str, Nil] = map_or_else(str)(default)(ok_outcome)
        >>> unwrap(mapped_ok)
        '10'
        >>> err_outcome: Res[int, Nil] = err(int)(Nil())
        >>> mapped_err: Res[str, Nil] = map_or_else(str)(default)(err_outcome)
        >>> unwrap(mapped_err)
        '0'

    """

    def get_default(default: Callable[[], U]) -> Callable[[Res[T, E]], Res[U, E]]:
        def inner(res: Res[T, E]) -> Res[U, E]:
            match res:
                case Ok(t):
                    return Ok(using(t))
                case Err():
                    return Ok(default())
                case _:
                    raise NotResError

        return inner

    return get_default


def and_then(using: Callable[[T], Res[U, E]]) -> Callable[[Res[T, E]], Res[U, E]]:
    """Replaces *res* with new result from *using*s output if Ok

    This is useful when you need to run functions that also return a result.

    Note:
        Preserve type hints by making sure that the `E` values are the same

    Args:
        *using* ((T) -> Res[U, E]): Func that takes a value and returns a ``Res``
        *res* (Res[T, E]): ``Res`` that provides input for *using* if ``Ok``

    Returns:
        *output* (Res[U, E]): Output of *using* if *res* is ``Ok``

    Examples: ::

        >>> succeeds = lambda x: some(str(x))
        >>> ok_outcome: Opt[int] = some(10)
        >>> err_outcome: Opt[int] = err(int)(Nil())
        >>> new_ok: Opt[str] = and_then(succeeds)(ok_outcome)
        >>> unwrap(new_ok)
        '10'
        >>> new_err: Opt[str] = and_then(succeeds)(err_outcome)
        >>> unwrap_err(new_err)
        Nil('Did not expect None')

    """

    def inner(res: Res[T, E]) -> Res[U, E]:
        match res:
            case Ok(t):
                return using(t)
            case Err(e):
                return Err(e)
            case _:
                raise TypeError('*res* must be an Ok or Err')

    return inner


def or_else(using: Callable[[E], Res[T, F]]) -> Callable[[Res[T, E]], Res[T, F]]:
    """Runs *using* to replace current state if ``Err``, else returns current state.

    Useful for aligning err values for future calls, or for running a separate
    process on failure.

    Args:
        *using* ((E) -> Res[T, F]): Func that takes ``E`` and returns a new ``Res``
        *res* (Res[T, E]): ``Res`` whose ``E`` will be used as input if ``Err``

    Returns:
        *output* (Res[T, F]): ``Res`` with updated ``Err`` value, or same ``Ok``

    Examples: ::

        >>> err_outcome: Res[int, ValueError] = err(int)(ValueError())
        >>> on_fail = lambda _: Err(Nil())
        >>> new_err: Res[int, Nil] = or_else(on_fail)(err_outcome)
        >>> unwrap_err(new_err)
        Nil('Did not expect None')

    """

    def inner(res: Res[T, E]) -> Res[T, F]:
        match res:
            case Err(e):
                return using(e)
            case Ok(t):
                return Ok(t)
            case _:
                raise TypeError('*res* must be an Ok or Err')

    return inner


def and_res(new_res: Res[U, E]) -> Callable[[Res[T, E]], Res[U, E]]:
    """Returns the provided result if the old one is `Ok`

    Args:
        *new_res* (Res[U, E]): Replacement ``Res``. Must match on ``E``
        *old_res* (Res[T, E]): Original ``Res``. Must match on ``E``

    Returns:
        *output* (Res[U, E]): Resolved ``Res`` with expected values

    Examples: ::

        >>> old: Opt[int] = some(10)
        >>> new: Opt[str] = some('hello')
        >>> resolved: Opt[str] = and_res(new)(old)
        >>> unwrap(resolved)
        'hello'

    """

    def inner(old_res: Res[T, E]) -> Res[U, E]:
        match old_res:
            case Ok():
                match new_res:
                    case Ok(u):
                        return Ok(u)
                    case Err(e):
                        return Err(e)
                    case _:
                        raise NotResError
            case Err(e):
                return Err(e)
            case _:
                raise NotResError

    return inner


def or_res(new_res: Res[T, F]) -> Callable[[Res[T, E]], Res[T, F]]:
    """Returns the provided result if the current one is an `Err`

    Args:
        *new_res*: (Res[T, F]): Becomes the new result if old one is ``Err``
        *old_res*: (Res[T, E]): Original result

    Returns:
        *output* (Res[T, F]): New result, or original if it was ``Ok``

    Examples: ::

        >>> new: Res[int, ValueError] = err(int)(ValueError())
        >>> old: Res[int, TypeError] = err(int)(TypeError())
        >>> resolved: Res[int, ValueError] = or_res(new)(old)
        >>> unwrap_err(resolved)
        ValueError()

    """

    def inner(old_res: Res[T, E]) -> Res[T, F]:
        match old_res:
            case Ok(t):
                return Ok(t)
            case Err():
                match new_res:
                    case Ok(t):
                        return Ok(t)
                    case Err(f):
                        return Err(f)
                    case _:
                        raise NotResError
            case _:
                raise NotResError

    return inner


def flatten(res: Res[Res[T, E], F]) -> Res[T, E | F]:
    """Flattens a `Res` containing a `Res`. Not recursive.

    Args:
        *res* (Res[Res[T, E], F]): A ``Res``, whose ``Ok`` is also a ``Res``

    Returns:
        *output* (Res[T, E | F]): A new ``Res``, whose ``Err`` could be either of
        the contained error values

    Examples: ::

        >>> nested = ok(ValueError)(ok(TypeError)(10))
        >>> flat: Res[int, ValueError | TypeError] = flatten(nested)
        >>> unwrap(flat)
        10

    """
    match res:
        case Ok(inner):
            match inner:
                case Ok(t):
                    return Ok(t)
                case Err(f):
                    return Err(f)
                case _:
                    raise NotResError
        case Err(e):
            return Err(e)
        case _:
            raise NotResError


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
                return Ok(using(*args, **kwargs))
            except err_type as e:
                return Err(e)

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
        return some(using(*args, **kwargs))

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
                return some(using(*args, **kwargs))
            except err_types as e:
                return Err(Nil(str(e)))

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
            return map_err(lambda e: to.__class__(str(e)) if inherit_message else to)(
                using(*args, **kwargs)
            )

        return wrapper

    return inner



q = unwrap
qe = unwrap_err
