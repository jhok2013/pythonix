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
from pythonix.internals.res import (
    and_res,
    and_then,
    err,
    flatten,
    is_err,
    is_err_and,
    is_ok,
    is_ok_and,
    map,
    map_err,
    map_or,
    unpack,
    map_or_else,
    null_safe,
    ok,
    or_else,
    safe,
    map_err,
    unwrap,
    some,
    Res,
    Opt,
    Nil,
    or_res,
    unwrap_err,
    unwrap_or,
    unwrap_or_else,
    Ok,
    Err,
    null_and_error_safe,
    q,
    qe,
)
