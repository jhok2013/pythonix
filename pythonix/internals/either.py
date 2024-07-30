from dataclasses import dataclass
from typing import TypeVar, Generic, TypeAlias, cast, Callable, overload
from abc import ABC

from pythonix.curry import two

L = TypeVar("L")
R = TypeVar("R")
U = TypeVar("U")
V = TypeVar("V")


class BaseEither(Generic[L], ABC):
    inner: L


@dataclass(frozen=True)
class Left(BaseEither, Generic[L]):
    inner: L
    __match_args__ = ("inner",)


@dataclass(frozen=True)
class Right(BaseEither, Generic[R]):
    inner: R
    __match_args__ = ("inner",)


Either: TypeAlias = Left[L] | Right[R]


@two
def left(right_type: type[R], left_value: L) -> Either[L, R]:
    return cast(Either[L, R], Left(left_value))


@two
def right(left_type: type[L], right_value: R) -> Either[L, R]:
    return cast(Either[L, R], Right(right_value))


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
    def get_op(op: Callable[[L | R], U]):
        def get_either(either: Either[L, R]) -> Either[L | U, R | U]:
            match side:
                case Left():
                    match either:
                        case Left(inner):
                            return left(R)(op(inner))
                        case Right(inner):
                            return right(U)(inner)
                        case _:
                            raise TypeError(f"Expected Either but found {type(either)}")
                case Right():
                    match either:
                        case Left(inner):
                            return left(U)(inner)
                        case Right(inner):
                            return right(L)(op(inner))
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
    def get_either(either: Either[L, R]) -> L | R:
        match side:
            case Left():
                match either:
                    case Left(inner):
                        return inner
                    case Right():
                        raise ValueError("Expected Left but found Right")
                    case _:
                        raise TypeError(f"Expected Either but found {type(either)}")
            case Right():
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
