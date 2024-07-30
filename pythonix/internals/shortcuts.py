from typing import Callable, TypeVar, overload, Tuple
from pythonix.internals.res import Res, Ok, Err, unpack as unpack_res, unwrap as unwrap_res
from pythonix.internals.either import Left, Right, Either, unpack as unpack_either, unwrap as unwrap_either
from pythonix.internals.trail import Trail, LogT, unpack as unpack_trail, unwrap as unwrap_trail
from functools import singledispatch

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

    @singledispatch
    def dispatch(wrapped: Ok[T]) -> T:
        return unwrap_res(wrapped)
    
    @dispatch.register(Err)
    def _(wrapped: Err[E]):
        return unwrap_res(wrapped)
    
    @dispatch.register(Trail)
    def _(wrapped: Trail[U]) -> U:
        return unwrap_trail(wrapped)
    
    @dispatch.register(type[Left])
    def _(wrapped: type[Left]) -> Callable[[Either[L, R]], L]:
        return unwrap_either(wrapped)
    
    @dispatch.register(type[Right])
    def _(wrapped: type[Right]):
        return unwrap_either(wrapped)
    
    @dispatch
    def _(_):
        raise TypeError('No valid type found')
    
    return dispatch(wrapped)


@overload
def unpack(packed: Res[T, E]) -> Tuple[T | None, E | None]: ...

@overload
def unpack(packed: Either[L, R]) -> Tuple[L | None, R | None]: ...

@overload
def unpack(packed: Trail[U]) -> Tuple[U, Tuple[LogT, ...]]: ...

def unpack(
    packed: Res[T, E] | Either[L, R] | Trail[U]
) -> Tuple[T | None, E | None] | Tuple[L | None, R | None] | Tuple[U, Tuple[LogT, ...]]:

    @singledispatch
    def dispatch(packed: Ok[T]):
        return unpack_res(packed)
    
    @dispatch.register(Err)
    def _(packed: Err[E]):
        return unpack_res(packed)
    
    @dispatch.register(Left)
    def _(packed: Left[L]):
        return unpack_either(packed)
    
    @dispatch.register(Right)
    def _(packed: Right[R]):
        return unpack_either(packed)
    
    @dispatch.register(Trail)
    def _(packed: Trail[T]):
        return unpack_trail(packed)
    
    @singledispatch
    def _(_):
        raise TypeError('No valid type found')
    
    return dispatch(packed)


q = unwrap
u = unpack
