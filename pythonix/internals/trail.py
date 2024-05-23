"""Wrap operations and values with logs that can be used at runtime.

Includes functions for wrapping values with logs, creating logs,
decorating functions to include logs, and running operations
over values that include or do not include logs.

Example: ::

        >>> add_ten = lambda x: x + 10
        >>> t = new(info('Initial 10'))(10)
        >>> t = blaze(add_ten, info('Added another ten'))(t)
        >>> logs, val = t
        >>> dt, message = logs[-1]
        >>> message
        'Added another ten'
        >>> val
        20

    You can also use functions that return a Trail, and blaze will handle
    the log concatenation. ::

        >>> add_ten_trailer = trail(info('Adding ten with trail'))(add_ten)
        >>> t = blaze(add_ten_trailer)(t)
        >>> logs, val = t
        >>> dt, message = logs[-1]
        >>> message
        'Adding ten with trail'
        >>> val
        30

"""
from functools import wraps
from typing import (
    NamedTuple,
    Tuple,
    Callable,
    ParamSpec,
    TypeVar,
    Generic,
    overload,
    TypeAlias,
)
from datetime import datetime, timezone

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


class Log(NamedTuple):
    """Immutable container for log messages.

    Note:
        Avoid creating this directly and use the `info`, `debug`, `warning`, `error`,
        or `critical` functions instead.
    """

    created_dt: datetime
    """datetime object for when the object was created"""

    message: str
    """The log message"""

    def __str__(self) -> str:
        return f'{type(self).__name__}("{self.created_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}", "{self.message}")'


class Info(Log):
    """Log object at the INFO severity"""

    ...


class Debug(Log):
    """Log object at the DEBUG severity"""

    ...


class Warning(Log):
    """Log object at the WARNING severity"""

    ...


class Error(Log):
    """Log object at the ERROR severity"""

    ...


class Critical(Log):
    """Log object at the CRITICAL severity"""

    ...


L = TypeVar("L", bound="Log")
LogT: TypeAlias = Info | Debug | Warning | Error | Critical


def log(log_type: type[L]):
    """Creates a function to create a Log

    Examples: ::

        >>> log_info = log(Info)
        >>> info_message = log_info('Hello world')
        >>> time, message = info_message
        >>> message
        'Hello world'

    """

    def inner(message: str) -> L:
        """Create a Log with the message and type"""
        return log_type(datetime.now(timezone.utc), message)

    return inner


debug = log(Debug)
"""Severity: DEBUG"""
info = log(Info)
"""Severity: INFO"""
warning = log(Warning)
"""Severity: WARNING"""
error = log(Error)
"""Severity: ERROR"""
critical = log(Critical)
"""Severity: CRITICAL"""


class Trail(Generic[T], NamedTuple):
    """Container type used to wrap a value with a series of Log type records

    Note:
        Create this object with the ``new`` function.

    Examples: ::

        >>> trailed: Trail[int] = new(info('starting'))(10)
        >>> logs, val = trailed
        >>> val
        10
        >>> log, *rest = logs
        >>> dt, message = log
        >>> message
        'starting'

    """

    logs: Tuple[LogT, ...]
    inner: T


def new(*logs: LogT):
    """Create a new `Trail` object with the desired logs attached.

    Example: ::

        >>> trailed: Trail[int] = new(info('starting'))(10)
        >>> logs, val = trailed
        >>> val
        10
        >>> log, *rest = logs
        >>> dt, message = log
        >>> message
        'starting'

    """

    def get_inner(inner: T) -> Trail[T]:
        """
        Attach the wrapped value to the `Trail`
        """
        return Trail(logs, inner)

    return get_inner


def append(*logs: LogT):
    """Append a new series of logs to a `Trail`

    Example: ::

        >>> t = new(info('starting'))(10)
        >>> t = append(info('ending'))(t)
        >>> logs, val = t
        >>> len(logs)
        2

    """

    def inner(trail: Trail[T]) -> Trail[T]:
        return new(*(trail.logs + logs))(trail.inner)

    return inner


def get_logs(trail: Trail[T]) -> Tuple[LogT, ...]:
    """Convenience function to return the logs of a `Trail`

    Example: ::

        >>> t = new(info('hello'))(10)
        >>> logs = get_logs(t)
        >>> dt, message = logs[0]
        >>> message
        'hello'

    """
    return trail.logs


def trail(*logs: LogT):
    """Decorator to always attach certain logs to a Trail of the output

    Example: ::

        >>> @trail(info('Starting'))
        ... def add_ten(x: int) -> int:
        ...     return x + 10
        ...
        >>> logs, val = add_ten(10)
        >>> val
        20
        >>> dt, message = logs[0]
        >>> message
        'Starting'

    """

    def inner(func: Callable[P, U]):
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Trail[U]:
            return new(*logs)(func(*args, **kwargs))

        return wrapper

    return inner


@overload
def blaze(
    using: Callable[[T], Trail[U]], *logs: LogT
) -> Callable[[Trail[T]], Trail[U]]:
    ...


@overload
def blaze(using: Callable[[T], U], *logs: LogT) -> Callable[[Trail[T]], Trail[U]]:
    ...


def blaze(
    using: Callable[[T], Trail[U] | U], *logs: LogT
) -> Callable[[Trail[T]], Trail[U]]:
    """Mapper to accumulate logs while running

    Can use functions that already return a Trail, or that simply return a value.
    Add in logs with blaze in addition to any logs already being added by
    the function.

    Example: ::

        >>> add_ten = lambda x: x + 10
        >>> t = new(info('Initial 10'))(10)
        >>> t = blaze(add_ten, info('Added another ten'))(t)
        >>> logs, val = t
        >>> dt, message = logs[-1]
        >>> message
        'Added another ten'
        >>> val
        20

    You can also use functions that return a Trail, and blaze will handle
    the log concatenation. ::

        >>> add_ten_trailer = trail(info('Adding ten with trail'))(add_ten)
        >>> t = blaze(add_ten_trailer)(t)
        >>> logs, val = t
        >>> dt, message = logs[-1]
        >>> message
        'Adding ten with trail'
        >>> val
        30

    """

    def get_val(val: Trail[T]) -> Trail[U]:
        previous_logs, inner = val
        out: U | Trail[U] = using(inner)

        match out:
            case Trail(new_logs, new_inner):
                return new(*previous_logs + new_logs + logs)(new_inner)
            case out_val:
                return new(*previous_logs + logs)(out_val)

    return get_val
