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
Val = TypeVar("Val")
NewVal = TypeVar("NewVal")
ErrVal = TypeVar("ErrVal", bound="Exception")
NewErrVal = TypeVar("NewErrVal", bound="Exception")


class Nil(Exception):
    """
    Error class used to represent an unexpected `None` value.
    """

    def __init__(self, message: str = "Did not expect None"):
        super().__init__(message)


class Ok(Generic[Val], NamedTuple):
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

    inner: Val

    def __iter__(self) -> Iterator[Val | None]:
        return iter((self.inner, None))


class Err(Generic[ErrVal], NamedTuple):
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

    inner: ErrVal

    def __iter__(self) -> Iterator[ErrVal | None]:
        return iter((None, self.inner))


Res: TypeAlias = Ok[Val] | Err[ErrVal]


def err(ok_type: type[Val]) -> Callable[[ErrVal], Res[Val, ErrVal]]:
    """
    Sets the `Ok` type of the `Res`
    #### Example
    ```python
    failure: Res[int, ValueError] = err(int)(ValueError())
    ```
    """

    def get_err(exception_object: ErrVal) -> Res[Val, ErrVal]:
        """
        Sets the value of the `Err` inner value of the `Res`
        """
        return Err(exception_object)

    return get_err


def ok(err_type: type[ErrVal]) -> Callable[[Val], Res[Val, ErrVal]]:
    """
    Sets the `Ok` inner value of the `Res`
    #### Example
    ```python
    success: Res[int, ValueError] = ok(5)(ValueError)
    ```
    """

    def get_err(ok_obj: Val) -> Res[Val, ErrVal]:
        """
        Sets the `Err` type of the `Res`
        """
        return cast(Res[Val, ErrVal], Ok(ok_obj))

    return get_err


def some(inner: Val | None) -> Ok[Val] | Err[Nil]:
    """
    Converts the passed in value `T | None` to `Err[Nil]` if None,
    else `Ok[T]`. Useful for checking for null values before they
    cause unexpected defects.
    """
    if inner is not None:
        return ok(Nil)(inner)
    return err(Val)(Nil())


def is_ok(res: Res[Val, ErrVal]) -> bool:
    """
    Return `True` if the `Res` is `Ok`.
    """
    match res:
        case Ok():
            return True
        case Err():
            return False


def is_err(res: Res[Val, ErrVal]) -> bool:
    """
    Return `True` if the `Res` is `Err`.
    """
    match res:
        case Ok():
            return False
        case Err():
            return True


def is_ok_and(predicate: Callable[[Val], bool]) -> Callable[[Res[Val, ErrVal]], bool]:
    """
    Return `True` if the `Res` is `Ok` and the `predicate` evaluates to `True`.
    """

    def inner(res: Res[Val, ErrVal]) -> bool:
        match res:
            case Ok(t):
                return predicate(t)
            case _:
                return False

    return inner


def is_err_and(
    predicate: Callable[[ErrVal], bool]
) -> Callable[[Res[Val, ErrVal]], bool]:
    """
    Return `True` if the `Res` is `Err` and the `predicate` evaluates to `True`
    """

    def inner(res: Res[Val, ErrVal]) -> bool:
        match res:
            case Err(e):
                return predicate(e)
            case _:
                return False

    return inner


def unwrap(result: Res[Val, ErrVal]) -> Val:
    """
    Return the `Ok` value or panic if `Err`
    """
    match result:
        case Ok(value):
            return cast(Val, value)
        case Err(e):
            raise e


def unwrap_or(default: Val) -> Callable[[Res[Val, ErrVal]], Val]:
    """
    Return the `Ok` value if `Ok`, else return the default
    """

    def inner(res: Res[Val, ErrVal]) -> Val:
        match res:
            case Ok(val):
                return val
            case _:
                return default

    return inner


def unwrap_or_else(on_err: Callable[[], Val]) -> Callable[[Res[Val, ErrVal]], Val]:
    """
    Return the `Ok` value if `Ok`, else run the `on_err` function that returns the same type.
    """

    def inner(res: Res[Val, ErrVal]) -> Val:
        match res:
            case Ok(val):
                return val
            case _:
                return on_err()

    return inner


def unwrap_err(result: Res[Val, ErrVal]) -> ErrVal:
    """
    Return the `Err`, else panic if `Ok`
    """
    match result:
        case Ok():
            raise UnwrapErr
        case Err(e):
            return e


def map(
    using: Callable[[Val], NewVal]
) -> Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]:
    """
    Run the function on the `Ok` if `Ok`, else return the current `Err`
    """

    def inner(res: Res[Val, ErrVal]) -> Res[NewVal, ErrVal]:
        match res:
            case Ok(t):
                return ok(ErrVal)(using(t))
            case _:
                return cast(Res[NewVal, ErrVal], res)

    return inner


def map_or(
    using: Callable[[Val], NewVal]
) -> Callable[[NewVal], Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]]:
    """
    Runs the function on the `Ok` or return the `default` if `Err`
    """

    def get_default(
        default: NewVal,
    ) -> Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]:
        def inner(res: Res[Val, ErrVal]) -> Res[NewVal, ErrVal]:
            match res:
                case Ok(t):
                    return ok(ErrVal)(using(t))
                case _:
                    return ok(ErrVal)(default)

        return inner

    return get_default


def map_err(
    using: Callable[[ErrVal], NewErrVal]
) -> Callable[[Res[Val, ErrVal]], Res[Val, NewErrVal]]:
    """
    Runs the function on the `ErrVal` if in `Err` or returns the current `Ok`
    """

    def inner(res: Res[Val, ErrVal]) -> Res[Val, ErrVal]:
        match res:
            case Err(e):
                return err(Val)(using(e))
            case _:
                return cast(Res[Val, NewErrVal], res)

    return inner


def map_catch(
    using: Callable[[Val], NewVal]
) -> Callable[[type[ErrVal]], Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]]:
    """
    Runs the function that could fail if `Ok`, else return the current `Err`
    """

    def get_catch(
        catch: type[ErrVal],
    ) -> Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]:
        def inner(res: Res[Val, ErrVal]) -> Res[NewVal, ErrVal]:
            match res:
                case Ok(t):
                    try:
                        return ok(ErrVal)(using(t))
                    except catch as e:
                        return err(NewVal)(e)
                case Err(e):
                    return cast(Res[NewVal, ErrVal], res)

        return inner

    return get_catch


def map_or_else(
    using: Callable[[Val], NewVal]
) -> Callable[
    [Callable[[], NewVal]], Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]
]:
    """
    Runs the provided function if `Ok`, or runs the default function if `Err`
    """

    def get_default(
        default: Callable[[], NewVal]
    ) -> Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]:
        def inner(res: Res[Val, ErrVal]) -> Res[NewVal, ErrVal]:
            match res:
                case Ok(t):
                    return ok(ErrVal)(using(t))
                case _:
                    return ok(ErrVal)(default())

        return inner

    return get_default


def and_then(
    using: Callable[[Val], Res[NewVal, ErrVal]]
) -> Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]:
    """
    Runs the function that returns a new `Res` if `Ok`, else return the current `Err`
    """

    def inner(res: Res[Val, ErrVal]) -> Res[NewVal, ErrVal]:
        match res:
            case Ok(t):
                return cast(Res[NewVal, ErrVal], using(t))
            case _:
                return cast(Res[NewVal, ErrVal], res)

    return inner


def or_else(
    using: Callable[[ErrVal], Res[NewVal, NewErrVal]]
) -> Callable[[Res[Val, ErrVal]], Res[Val, NewErrVal]]:
    """
    Runs the function that returns a new `Res` if in `Err`, else it will return the current `Ok`
    """

    def inner(res: Res[Val, ErrVal]) -> Res[Val, NewErrVal]:
        match res:
            case Err(e):
                return cast(Res[Val, NewErrVal], using(e))
            case _:
                return cast(Res[Val, NewErrVal], res)

    return inner


def and_then_catch(using: Callable[[Val], NewVal]):
    """
    Runs the function that could fail, catching the specified error and returning a new `Res`.
    Will only be ran if `Ok`, else it will return its current `Err`
    """

    def get_catch(
        catch: type[NewErrVal],
    ) -> Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal | NewErrVal]]:
        def inner(res: Res[Val, ErrVal]) -> Res[NewVal, ErrVal | NewErrVal]:
            match res:
                case Ok(t):
                    try:
                        return cast(
                            Res[NewVal, ErrVal | NewErrVal], ok(ErrVal)(using(t))
                        )
                    except catch as f:
                        return cast(Res[NewVal, ErrVal | NewErrVal], err(NewVal)(f))
                case Err(f):
                    return cast(Res[NewVal, ErrVal | NewErrVal], err(NewVal)(f))

        return inner

    return get_catch


def map_err(using: Callable[[ErrVal], NewErrVal]):
    """
    Changes the internal `Err` using the function if in an `Err` state. Otherwise it returns
    the `Ok`
    """

    def inner(res: Res[Val, ErrVal]) -> Res[Val, NewErrVal]:
        match res:
            case Err(e):
                return err(Val)(using(e))
            case _:
                return cast(Res[Val, NewErrVal], res)

    return inner


def and_res(
    new_res: Res[NewVal, ErrVal]
) -> Callable[[Res[Val, ErrVal]], Res[NewVal, ErrVal]]:
    """
    Returns the provided result if the old one is `Ok`
    """

    def inner(old_res: Res[Val, ErrVal]) -> Res[NewVal, ErrVal]:
        match old_res:
            case Ok():
                return new_res
            case Err():
                return cast(Res[NewVal, ErrVal], old_res)

    return inner


def or_res(
    new_res: Res[Val, NewErrVal]
) -> Callable[[Res[Val, ErrVal]], Res[Val, NewErrVal]]:
    """
    Returns the provided result if the current one is an `Err`
    """

    def inner(old_res: Res[Val, ErrVal]) -> Res[Val, NewErrVal]:
        match old_res:
            case Ok():
                return cast(Res[Val, NewErrVal], old_res)
            case Err():
                return new_res

    return inner


def flatten(res: Res[Res[Val, ErrVal], NewErrVal]) -> Res[Val, ErrVal | NewErrVal]:
    """
    Flattens a `Res` containing a `Res`
    """
    match res:
        case Ok(inner_res):
            return inner_res
        case Err():
            return res


def safe(*err_type: type[ErrVal]):
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

    def inner(using: Callable[P, NewVal]) -> Callable[P, Res[NewVal, ErrVal]]:
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[NewVal, ErrVal]:
            try:
                return cast(Res[NewVal, ErrVal], ok(ErrVal)(using(*args, **kwargs)))
            except err_type as e:
                return cast(Res[NewVal, ErrVal], err(NewVal)(e))

        return wrapper

    return inner


def null_safe(using: Callable[P, NewVal | None]):
    """
    Wraps the output of the function in a `Res[T, Nil]` object.
    """

    @wraps(using)
    def inner(*args: P.args, **kwargs: P.kwargs) -> Res[NewVal, Nil]:
        return some(using(*args, **kwargs))

    return inner


def null_and_error_safe(*err_types: type[ErrVal]):
    """
    Wraps the output in the `some` function and consumes the error if it is thrown, replacing it with `Nil`
    """

    def inner(using: Callable[P, Val]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[Val, Nil]:
            try:
                return some(using(*args, **kwargs))
            except err_types as e:
                return map_err(lambda f: Nil(str(f)))(err(Val)(e))

        return wrapper

    return inner


def combine_errors(to: NewErrVal, inherit_message: bool = False):
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
    def inner(using: Callable[P, Ok[Val] | Err[ErrVal]]):
        @wraps(using)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Res[Val, NewErrVal]:
            return map_err(lambda e: to.__class__(str(e)) if inherit_message else to)(
                using(*args, **kwargs)
            )

        return wrapper

    return inner


q = unwrap
qe = unwrap_err
