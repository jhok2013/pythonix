from dataclasses import dataclass
from typing import TypeVar, Generic, TypeAlias, cast
from abc import ABC

from pythonix.curry import two

T = TypeVar('T')
U = TypeVar('U')


class BaseEither(Generic[T], ABC):
    
    inner: T


@dataclass(frozen=True)
class Left(BaseEither, Generic[T]):

    inner: T
    __match_args__ = ("inner",)


@dataclass(frozen=True)
class Right(BaseEither, Generic[U]):

    inner: U
    __match_args__ = ("inner",)


Either: TypeAlias = Left[T] | Right[U]


@two
def left(right_type: type[U], left_value: T) -> Either[T, U]:
    return cast(Either[T, U], Left(left_value))


@two
def right(left_type: type[T], right_value: U) -> Either[T, U]:
    return cast(Either[T, U], Right(right_value))


def unpack(either: Either[T, U]) -> tuple[T | None, U | None]:
    match either:
        case Left(left):
            return left, None
        case Right(right):
            return None, right
        case _:
            raise TypeError('Invalid type presented. Must be Left or Right')

