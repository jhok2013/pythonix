from __future__ import annotations
from typing import TypeVar, Generic, TypeAlias, cast, Callable, overload
from abc import ABC
from dataclasses import dataclass

L = TypeVar("L")
R = TypeVar("R")
U = TypeVar("U")
V = TypeVar("V")


class BaseEither(Generic[L], ABC):
    inner: L

@dataclass(init=False)
class Left(BaseEither, Generic[L]):
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
    __match_args__ = ("inner",)

    def __new__(cls, right_type: type[R]) -> Callable[[L], Either[L, R]]:

        def get_left(left: L) -> Either[L, R]:
            obj = object.__new__(cls)
            obj.inner = left
            return cast(Either[L, R], obj)

        return get_left

@dataclass(init=False)    
class Right(BaseEither, Generic[R]):
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
    __match_args__ = ("inner",)

    def __new__(cls, left_type: type[L]) -> Callable[[R], Either[L, R]]:

        def get_right(right: R) -> Either[L, R]:
            obj = object.__new__(cls)
            obj.inner = right
            return cast(Either[L, R], obj)

        return get_right

Either: TypeAlias = Left[L] | Right[R]

@overload
def map(
    side: type[Left],
) -> Callable[[Callable[[L], U]], Callable[[Either[L, R]], Either[U, R]]]:
    ...


@overload
def map(
    side: type[Right],
) -> Callable[[Callable[[R], U]], Callable[[Either[L, R]], Either[L, U]]]:
    ...


def map(side: type[Left] | type[Right]):
    """Runs a function on the desired side, returning a new Either with the result
    Will do nothing if you map alternate sides. For example, if the Either is Left,
    then mapping the right side will not change the value, only the signature.
    
    Args:
        side (type[Left] | type[Right]): The desired side to target
        op (Fn[L | R, U]): Function that takes the desired side and returns a new value
    
    Returns:
        if_left (Either[U, R]): New Either with a new Left value and same potential Right value
        if_right (Either[L, U]): New Either with a new Right value and same potential Left value
    
    ## Examples

    First choose a side to map ::

        >>> choice: Either[str, str] = Left(str)("Left choice")
        >>> new_choice: Either[int, str] = map(Left)(lambda _: 10)(choice)
        >>> new_choice.inner
        10
    
    If you map Left to Right then nothing happens except the signature changing to match
    """
    def get_op(op: Callable[[L | R], U]):
        def get_either(either: Either[L, R]) -> Either[L | U, R | U]:
            match side:
                case l if l is Left:
                    match either:
                        case Left(inner):
                            return Left(R)(op(inner))
                        case Right(inner):
                            return Right(U)(inner)
                        case _:
                            raise TypeError(f"Expected Either but found {type(either)}")
                case r if r is Right:
                    match either:
                        case Left(inner):
                            return Left(U)(inner)
                        case Right(inner):
                            return Right(L)(op(inner))
                        case _:
                            raise TypeError(f"Expected Either but found {type(either)}")
                case _:
                    raise TypeError(
                        f"Expected Left or Right type but found {type(either)}"
                    )

        return get_either

    return get_op


@overload
def unwrap(side: type[Left]) -> Callable[[Either[L, R]], L]:
    ...


@overload
def unwrap(side: type[Right]) -> Callable[[Either[L, R]], R]:
    ...


def unwrap(side: type[Left] | type[Right]):
    """Returns the value of the Either, or else raises an error
    
    ## Raises
        err (ValueError): Raised if the *side* and *either* are not the same

    Args:
        side (type[Left] | type[Right]): The expected side
        either (Either[L, R]): The Either object whose value will be returned
    
    
    Returns:
        if_left (L): If Either is Left, and expecting Left, then Left's value
        if_right (R): If Either is Right and expecting Right, then Right's value

    ## Example

    >>> either: Either[int, str] = Left(str)(10)
    >>> left: int = unwrap(Left)(either)
    >>> left
    10

    """

    def get_either(either: Either[L, R]) -> L | R:
        match side:
            case left if left is Left:
                match either:
                    case Left(inner):
                        return inner
                    case Right():
                        raise ValueError("Expected Left but found Right")
                    case _:
                        raise TypeError(f"Expected Either but found {type(either)}")
            case right if right is Right:
                match either:
                    case Left():
                        raise ValueError("Expected Right but found Left")
                    case Right(inner):
                        return inner
                    case _:
                        raise TypeError(f"Expected Either but found {type(either)}")
            case _:
                raise TypeError(f"Expected Left or Right type but found {type(either)}")

    return get_either


def unpack(either: Either[L, R]) -> tuple[L | None, R | None]:
    match either:
        case Left(left):
            return left, None
        case Right(right):
            return None, right
        case _:
            raise TypeError(f"Expected Either but found {type(either)}")
