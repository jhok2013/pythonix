from typing import Callable, TypeVar, overload, Tuple
from pythonix.internals.res import Res, Ok, Err, unpack as unpack_res, unwrap as unwrap_res
from pythonix.internals.either import Left, Right, Either, unpack as unpack_either, unwrap as unwrap_either
from pythonix.internals.trail import Trail, L as LogT, unpack as unpack_trail, unwrap as unwrap_trail
from pythonix.internals.pair import Pair, unpack as unpack_pair

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E', bound='Exception')
F = TypeVar('F', bound='Exception')
L = TypeVar('L')
R = TypeVar('R')



@overload
def unwrap(wrapped: Res[T, E]) -> T: ...

@overload
def unwrap(wrapped: Trail[T]) -> T: ...

@overload
def unwrap(wrapped: type[Left]) -> Callable[[Either[L, R]], L]: ...

@overload
def unwrap(wrapped: type[Right]) -> Callable[[Either[L, R]], R]: ...

def unwrap(
    wrapped: Res[T, E] | Trail[U] | type[Left] | type[Right]
) -> T | U | Callable[[Either[L, R]], L] | Callable[[Either[L, R]], R]:

    match wrapped:
        case Ok() | Err():
            return unwrap_res(wrapped)
        case Trail():
            return unwrap_trail(wrapped)
        case left if left is Left:
            return unwrap_either(Left)
        case right if right is Right:
            return unwrap_either(Right)
        case _:
            raise TypeError(f'No valid type found. Found {type(wrapped)}')

@overload
def unpack(packed: Res[T, E]) -> Tuple[T | None, E | None]: ...

@overload
def unpack(packed: Either[L, R]) -> Tuple[L | None, R | None]: ...

@overload
def unpack(packed: Trail[U]) -> Tuple[U, Tuple[LogT, ...]]: ...

@overload
def unpack(packed: Pair[T]) -> Tuple[str, T]: ...

def unpack(
    packed: Res[T, E] | Either[L, R] | Trail[U]
) -> Tuple[T | None, E | None] | Tuple[L | None, R | None] | Tuple[U, Tuple[LogT, ...]]:

    dispatches = {
        Ok: unpack_res,
        Err: unpack_res,
        Trail: unpack_trail,
        Left: unpack_either,
        Right: unpack_either,
        Pair: unpack_pair
    }
    if (dispatch := dispatches.get(type(packed))) is None:
        raise TypeError('No valid type found')
    return dispatch(packed)


q = unwrap
u = unpack
