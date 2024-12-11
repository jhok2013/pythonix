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
    Res,
    Nil,
    UnwrapError,
    ExpectError,
    Nil,
    catch_all,
    convert_err,
    err_and,
    is_err,
    expect_err,
    expect,
    is_ok,
    unwrap_err,
    ok_and,
    null_and_error_safe,
    combine_errors,
    safe,
    null_safe,
)
