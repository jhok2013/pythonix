from __future__ import annotations
from functools import wraps
from typing import (
    TypeVar,
    Generic,
    NamedTuple,
    cast,
    ParamSpec,
    Callable,
    TypeAlias,
    Iterator,
)

P = ParamSpec("P")

UnwrapErr = ValueError("Attempted to retrieve an Err from an Ok")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
E = TypeVar("E", bound="Exception")
F = TypeVar("F", bound="Exception")
G = TypeVar("G", bound="Exception")


class Nil(Exception):
    """
    Error class used to represent an unexpected `None` value.
    """

    def __init__(self, message: str = "Did not expect None"):
        super().__init__(message)


class Ok(Generic[T], NamedTuple):
    """
    Represents a successful outcome of a function that could have failed.
    Useful for pattern matching on a function that returns `Ok[T] | Err[E]`
    ### Example
    ```python
    success: Res[int, ValueError] = ok(ValueError)(5)
    match success:
        case Ok(t):
            assert t == 5
        case Err(e):
            raise e
    ```
    """

    inner: T

    def __iter__(self) -> Iterator[T | None]:
        return iter((self.inner, None))


class Err(Generic[E], NamedTuple):
    """
    Represents a successful outcome of a function that could have failed.
    Useful for pattern matching on a function that returns `Ok[T] | Err[E]`
    ### Example
    ```python
    failure: Res[int, ValueError] = err(int)(ValueError("Failed to do a thing"))
    match failure:
        case Ok():
            ...
        case Err(e):
            raise e
    ```
    """

    inner: E

    def __iter__(self) -> Iterator[E | None]:
        return iter((None, self.inner))


Res: TypeAlias = Ok[T] | Err[E]


def err(ok_type: type[T]) -> Callable[[E], Res[T, E]]:
    """
    Sets the `Ok` type of the `Res`
    #### Example
    ```python
    failure: Res[int, ValueError] = err(int)(ValueError())
    ```
    """

    def get_err(exception_object: E) -> Res[T, E]:
        """
        Sets the value of the `Err` inner value of the `Res`
        """
        return Err(exception_object)

    return get_err


def ok(err_type: type[E]) -> Callable[[T], Res[T, E]]:
    """
    Sets the `Ok` inner value of the `Res`
    #### Example
    ```python
    success: Res[int, ValueError] = ok(5)(ValueError)
    ```
    """

    def get_err(ok_obj: T) -> Res[T, E]:
        """
        Sets the `Err` type of the `Res`
        """
        return cast(Res[T, E], Ok(ok_obj))

    return get_err


def some(inner: T | None) -> Ok[T] | Err[Nil]:
    """
    Converts the passed in value `T | None` to `Err[Nil]` if None,
    else `Ok[T]`. Useful for checking for null values before they
    cause unexpected defects.
    """
    if inner is not None:
        return ok(Nil)(inner)
    return err(T)(Nil())


def is_ok(res: Res[T, E]) -> bool:
    """
    Return `True` if the `Res` is `Ok`.
    """
    match res:
        case Ok():
            return True
        case Err():
            return False


def is_err(res: Res[T, E]) -> bool:
    """
    Return `True` if the `Res` is `Err`.
    """
    match res:
        case Ok():
            return False
        case Err():
            return True


def is_ok_and(predicate: Callable[[T], bool]) -> Callable[[Res[T, E]], bool]:
    """
    Return `True` if the `Res` is `Ok` and the `predicate` evaluates to `True`.
    """

    def inner(res: Res[T, E]) -> bool:
        match res:
            case Ok(t):
                return predicate(t)
            case _:
                return False

    return inner


def is_err_and(predicate: Callable[[E], bool]) -> Callable[[Res[T, E]], bool]:
    """
    Return `True` if the `Res` is `Err` and the `predicate` evaluates to `True`
    """

    def inner(res: Res[T, E]) -> bool:
        match res:
            case Err(e):
                return predicate(e)
            case _:
                return False

    return inner


def unwrap(result: Res[T, E]) -> T:
    """
    Return the `Ok` value or panic if `Err`
    """
    match result:
        case Ok(value):
            return cast(T, value)
        case Err(e):
            raise e


def unwrap_or(default: T) -> Callable[[Res[T, E]], T]:
    """
    Return the `Ok` value if `Ok`, else return the default
    """

    def inner(res: Res[T, E]) -> T:
        match res:
            case Ok(val):
                return val
            case _:
                return default

    return inner


def unwrap_or_else(on_err: Callable[[], T]) -> Callable[[Res[T, E]], T]:
    """
    Return the `Ok` value if `Ok`, else run the `on_err` function that returns the same type.
    """

    def inner(res: Res[T, E]) -> T:
        match res:
            case Ok(val):
                return val
            case _:
                return on_err()

    return inner


def unwrap_err(result: Res[T, E]) -> E:
    """
    Return the `Err`, else panic if `Ok`
    """
    match result:
        case Ok():
            raise UnwrapErr
        case Err(e):
            return e


def map(using: Callable[[T], U]) -> Callable[[Res[T, E]], Res[U, E]]:
    """
    Run the function on the `Ok` if `Ok`, else return the current `Err`
    """

    def inner(res: Res[T, E]) -> Res[U, E]:
        match res:
            case Ok(t):
                return ok(E)(using(t))
            case _:
                return cast(Res[U, E], res)

    return inner


def map_or(using: Callable[[T], U]) -> Callable[[U], Callable[[Res[T, E]], Res[U, E]]]:
    """
    Runs the function on the `Ok` or return the `default` if `Err`
    """

    def get_default(
        default: U,
    ) -> Callable[[Res[T, E]], Res[U, E]]:
        def inner(res: Res[T, E]) -> Res[U, E]:
            match res:
                case Ok(t):
                    return ok(E)(using(t))
                case _:
                    return ok(E)(default)

        return inner

    return get_default


def map_err(using: Callable[[E], F]) -> Callable[[Res[T, E]], Res[T, F]]:
    """
    Runs the function on the `ErrVal` if in `Err` or returns the current `Ok`
    """

    def inner(res: Res[T, E]) -> Res[T, E]:
        match res:
            case Err(e):
                return err(T)(using(e))
            case _:
                return cast(Res[T, F], res)

    return inner


def map_catch(
    using: Callable[[T], U]
) -> Callable[[type[E]], Callable[[Res[T, E]], Res[U, E]]]:
    """
    Runs the function that could fail if `Ok`, else return the current `Err`
    """

    def get_catch(
        catch: type[E],
    ) -> Callable[[Res[T, E]], Res[U, E]]:
        def inner(res: Res[T, E]) -> Res[U, E]:
            match res:
                case Ok(t):
                    try:
                        return ok(E)(using(t))
                    except catch as e:
                        return err(U)(e)
                case Err(e):
                    return cast(Res[U, E], res)

        return inner

    return get_catch


def map_or_else(
    using: Callable[[T], U]
) -> Callable[[Callable[[], U]], Callable[[Res[T, E]], Res[U, E]]]:
    """
    Runs the provided function if `Ok`, or runs the default function if `Err`
    """

    def get_default(default: Callable[[], U]) -> Callable[[Res[T, E]], Res[U, E]]:
        def inner(res: Res[T, E]) -> Res[U, E]:
            match res:
                case Ok(t):
                    return ok(E)(using(t))
                case _:
                    return ok(E)(default())

        return inner

    return get_default


def and_then(using: Callable[[T], Res[U, E]]) -> Callable[[Res[T, E]], Res[U, E]]:
    """
    Runs the function that returns a new `Res` if `Ok`, else return the current `Err`
    """

    def inner(res: Res[T, E]) -> Res[U, E]:
        match res:
            case Ok(t):
                return cast(Res[U, E], using(t))
            case _:
                return cast(Res[U, E], res)

    return inner


def or_else(using: Callable[[E], Res[U, F]]) -> Callable[[Res[T, E]], Res[T, F]]:
    """
    Runs the function that returns a new `Res` if in `Err`, else it will return the current `Ok`
    """

    def inner(res: Res[T, E]) -> Res[T, F]:
        match res:
            case Err(e):
                return cast(Res[T, F], using(e))
            case _:
                return cast(Res[T, F], res)

    return inner


def and_then_catch(using: Callable[[T], U]):
    """
    Runs the function that could fail, catching the specified error and returning a new `Res`.
    Will only be ran if `Ok`, else it will return its current `Err`
    """

    def get_catch(
        catch: type[F],
    ) -> Callable[[Res[T, E]], Res[U, E | F]]:
        def inner(res: Res[T, E]) -> Res[U, E | F]:
            match res:
                case Ok(t):
                    try:
                        return cast(Res[U, E | F], ok(E)(using(t)))
                    except catch as f:
                        return cast(Res[U, E | F], err(U)(f))
                case Err(f):
                    return cast(Res[U, E | F], err(U)(f))

        return inner

    return get_catch


def map_err(using: Callable[[E], F]):
    """
    Changes the internal `Err` using the function if in an `Err` state. Otherwise it returns
    the `Ok`
    """

    def inner(res: Res[T, E]) -> Res[T, F]:
        match res:
            case Err(e):
                return err(T)(using(e))
            case _:
                return cast(Res[T, F], res)

    return inner


def and_res(new_res: Res[U, E]) -> Callable[[Res[T, E]], Res[U, E]]:
    """
    Returns the provided result if the old one is `Ok`
    """

    def inner(old_res: Res[T, E]) -> Res[U, E]:
        match old_res:
            case Ok():
                return new_res
            case Err():
                return cast(Res[U, E], old_res)

    return inner


def or_res(new_res: Res[T, F]) -> Callable[[Res[T, E]], Res[T, F]]:
    """
    Returns the provided result if the current one is an `Err`
    """

    def inner(old_res: Res[T, E]) -> Res[T, F]:
        match old_res:
            case Ok():
                return cast(Res[T, F], old_res)
            case Err():
                return new_res

    return inner


def flatten(res: Res[Res[T, E], F]) -> Res[T, E | F]:
    """
    Flattens a `Res` containing a `Res`
    """
    match res:
        case Ok(inner_res):
            return inner_res
        case Err():
            return res


def do(using: Callable[[U], V]):
    def inner(res: Res[T, E]) -> Res[T, E]:
        match res:
            case Ok(val):
                using(val)
                return res
            case Err():
                return res

    return inner


def do_err(using: Callable[[F], G]):
    def inner(res: Res[T, E]) -> Res[T, E]:
        match res:
            case Ok():
                return res
            case Err(e):
                using(e)
                return res

    return inner


def safe(*err_type: type[E]):
    """
    Decorator function used to capture the specified errors and convert them to
    a `Res[Val, ErrVal]` type. Can capture multiple error types at once and preserves
    type hints for the `Res`.
    #### Example
    ```python
    # The two functions are equivalent
    @safe(ValueError, TypeError)
    def func_1():
        return 'success'

    def func_2():
        try:
            return ok('success')(ValueError | TypeError)
        except (ValueError, TypeError) as e:
            return err(str)(e)
    ```
    """

    def inner(using: Callable[P, U]) -> Callable[P, Res[U, E]]:
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[U, E]:
            try:
                return cast(Res[U, E], ok(E)(using(*args, **kwargs)))
            except err_type as e:
                return cast(Res[U, E], err(U)(e))

        return wrapper

    return inner


def null_safe(using: Callable[P, U | None]):
    """
    Wraps the output of the function in a `Res[T, Nil]` object.
    """

    @wraps(using)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Res[U, Nil]:
        return some(using(*args, **kwargs))

    return inner


def null_and_error_safe(*err_types: type[E]):
    """
    Wraps the output in the `some` function and consumes the error if it is thrown, replacing it with `Nil`
    """

    def inner(using: Callable[P, T]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[T, Nil]:
            try:
                return some(using(*args, **kwargs))
            except err_types as e:
                return map_err(lambda f: Nil(str(f)))(err(T)(e))

        return wrapper

    return inner


def combine_errors(to: F, inherit_message: bool = False):
    """
    Decorator function used to convert function that return a `Res[Val, ErrVal]` to `Res[Val, NewErrVal]`, consuming
    the references to the original captured errors. Useful for when a function could throw a lot of errors and you
    need to convert them into one error instead.
    #### Example
    ```python
    @combine_errors(CustomError)
    @safe(TypeError, ValueError)
    def do_thing(s: str) -> str:
        if not isinstance(s, str):
            raise TypeError('Must be str')
        return s
    done: Res[str, CustomError] = do_thing('ok')
    ```
    """

    def inner(using: Callable[P, Ok[T] | Err[E]]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[T, F]:
            return map_err(lambda e: to.__class__(str(e)) if inherit_message else to)(
                using(*args, **kwargs)
            )

        return wrapper

    return inner


q = unwrap
qe = unwrap_err
