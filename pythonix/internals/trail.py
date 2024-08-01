"""Wrap operations and values with logs that can be used at runtime.

Includes functions for wrapping values with logs, creating logs,
decorating functions to include logs, and running operations
over values that include or do not include logs.

Example: ::

        >>> add_ten = lambda x: x + 10
        >>> t = new(Info('Initial 10'))(10)
        >>> t = blaze(add_ten, Info('Added another ten'))(t)
        >>> val, logs = unpack(t)
        >>> message, dt = logs[-1]
        >>> message
        'Added another ten'
        >>> val
        20

    You can also use functions that return a Trail, and blaze will handle
    the log concatenation. ::

        >>> add_ten_trailer = on_start(Info('Adding ten with trail'))(add_ten)
        >>> t = blaze(add_ten_trailer)(t)
        >>> val, logs = unpack(t)
        >>> message, dt = logs[-1]
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
)
from datetime import datetime, timezone
from dataclasses import dataclass

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")


class Log(NamedTuple):
    """Parent immutable class for Log messages. Use its children.

    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    """
    message: str
    """The log message"""
    created_dt: datetime = datetime.now(timezone.utc)
    """The datetime in UTC when the Log is created"""

    def __str__(self) -> str:
        return f'{type(self).__name__}("{self.created_dt.strftime("%Y-%m-%dT%H:%M:%SZ")}", "{self.message}")'

class Info(Log):
    """Log object at the INFO severity
    
    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created
    
    ## Examples

    >>> log = Info("Hello world")
    >>> message, dt = log
    >>> message
    'Hello world'

    """
    ...

class Debug(Log):
    """Log object at the DEBUG severity
    
    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples

    >>> log = Debug("Hello world")
    >>> message, dt = log
    >>> message
    'Hello world'

    """
    ...


class Warning(Log):
    """Log object at the WARNING severity
    
    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples

    >>> log = Warning("Easy there")
    >>> message, dt = log
    >>> message
    'Easy there'

    """
    ...

class Error(Log):
    """Log object at the ERROR severity
    
    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples

    >>> log = Error("Oops!")
    >>> message, dt = log
    >>> message
    'Oops!'

    """
    ...

class Critical(Log):
    """Log object at the CRITICAL severity
    
    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples

    >>> log = Critical("Oh no!")
    >>> message, dt = log
    >>> message
    'Oh no!'

    """
    ...


L = TypeVar("L", bound="Log")
"""Generic bound to all subclasses of Log, like Info, Debug, Error, Warning, and Critical"""

@dataclass(frozen=True)
class Trail(Generic[T]):
    """Container type used to wrap a value with a series of Log type records

    Attributes:
        inner (T): The wrapped value
        logs (Tuple[L, ...]): A tuple full of Log messages

    ## Examples

    >>> trailed: Trail[int] = Trail(10, (Info('Starting'),))
    >>> val, logs = unpack(trailed)
    >>> val
    10
    >>> log, *_ = logs
    >>> message, dt = log
    >>> message
    'Starting'

    """

    inner: T
    """The wrapped value inside the Trail"""
    logs: Tuple[L, ...]
    """The logs attached to the value"""
    __match_args__ = ('inner', 'logs')


def new(*logs: L):
    """Optional function used to create a Trail object

    Args:
        logs (Tuple[L, ...]): Args of any number of Log type objects 
        inner (T): The wrapped value
    
    Returns:
        trail (Trail[T]): A new Trail object with the wrapped value and logs
    
    ## Example

    >>> trail: Trail[int] = new(Info("Starting process"), Debug("Starting process with value 10"))(10)
    >>> inner, logs = unpack(trail)
    >>> inner
    10
    >>> message, dt = logs[0]
    >>> message
    'Starting process'
    
    """

    def get_inner(inner: T) -> Trail[T]:

        return Trail(inner, logs)
    
    return get_inner


def unwrap(trail: Trail[T]) -> T:
    return trail.inner

def unpack(trail: Trail[T]) -> Tuple[T, Tuple[L, ...]]:
    return trail.inner, trail.logs

def append(*logs: L):
    """Append a new series of logs to a `Trail`

    Args:
        logs (Tuple[L, ...]): New logs to be appended to the Trail
        trail (Trail[T]): Trail to receive the new logs
    
    Returns:
        trail Trail[T]: The Trail with new logs attached
    
    ## Example

    >>> t = Trail(10, (Info("starting"),))
    >>> t = append(Info('ending'))(t)
    >>> val, logs = unpack(t)
    >>> len(logs)
    2

    """

    def inner(trail: Trail[T]) -> Trail[T]:
        
        match trail:
            case Trail(inner, old_logs):
                return Trail(inner, old_logs + logs)
            case _:
                raise TypeError(f'Expected Trail. Found {type(trail)}')

    return inner

def on_start(*logs: L):
    """Decorator to always attach certain logs to a Trail of the output

    Example: ::

        >>> @on_start(Info('Starting'))
        ... def add_ten(x: int) -> int:
        ...     return x + 10
        ...
        >>> val, logs = unpack(add_ten(10))
        >>> val
        20
        >>> message, dt = logs[0]
        >>> message
        'Starting'

    """

    def inner(func: Callable[P, U]):
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Trail[U]:
            return Trail(func(*args, **kwargs), logs)

        return wrapper

    return inner


@overload
def blaze(
    using: Callable[[T], Trail[U]], *logs: L
) -> Callable[[Trail[T]], Trail[U]]:
    ...


@overload
def blaze(using: Callable[[T], U], *logs: L) -> Callable[[Trail[T]], Trail[U]]:
    ...


def blaze(
    using: Callable[[T], Trail[U] | U], *logs: L
) -> Callable[[Trail[T]], Trail[U]]:
    """Mapper to accumulate logs while running

    Can use functions that already return a Trail, or that simply return a value.
    Add in logs with blaze in addition to any logs already being added by
    the function.

    ## Example 

    >>> add_ten = lambda x: x + 10
    >>> t = Trail(10, Info('Initial'))
    >>> t = blaze(add_ten, Info('Added another ten'))(t)
    >>> val, logs = unpack(t)
    >>> message, dt = logs[-1]
    >>> message
    'Added another ten'
    >>> val
    20

    You can also use functions that return a Trail, and blaze will handle
    the log concatenation.

    >>> add_ten_trailer = on_start(Info('Adding ten with trail'))(add_ten)
    >>> t = blaze(add_ten_trailer)(t)
    >>> val, logs = unpack(t)
    >>> message, dt = logs[-1]
    >>> message
    'Adding ten with trail'
    >>> val
    30

    """

    def get_val(val: Trail[T]) -> Trail[U]:
        inner: T = val.inner
        previous_logs: Tuple[L, ...] = val.logs
        out: U | Trail[U] = using(inner)

        match out:
            case Trail(new_inner, new_logs):
                match (previous_logs, new_logs, logs):
                    case (tuple(old), tuple(new), tuple(blaze_logs)):
                        return Trail(new_inner, (old + blaze_logs + new))
                    case _:
                        raise TypeError(f'Invalid logs. Types are: {type(previous_logs)}, {type(new_logs)}, {type(logs)}')
            case out_val:
                return Trail(out_val, (previous_logs + logs))

    return get_val
