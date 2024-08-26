from __future__ import annotations
from collections import deque
from typing import (
    Tuple,
    Callable,
    ParamSpec,
    TypeVar,
    Generic,
    Iterable,
)
from dataclasses import dataclass, field, InitVar
from datetime import datetime, timezone

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound="Exception")

@dataclass(
    frozen=True,
    init=True,
    repr=True,
)
class Log(object):
    """Parent immutable class for Log messages. Use its children.

    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    """
    message: str
    """The log message"""
    created_dt: datetime = field(init=False, default=datetime.now(timezone.utc))
    """The datetime in UTC when the Log is created"""

    __match_args__ = ("message", "created_dt")

    def to_tuple(self) -> Tuple[str, datetime]:
        return self.message, self.created_dt

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
    __match_args__ = ("message", "created_dt")

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
    __match_args__ = ("message", "created_dt")


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
    __match_args__ = ("message", "created_dt")


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
    __match_args__ = ("message", "created_dt")

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
    __match_args__ = ("message", "created_dt")


L = TypeVar("L", bound="Log")
"""Generic bound to all subclasses of Log, like Info, Debug, Error, Warning, and Critical"""

@dataclass(repr=True)
class Trail(Generic[T]):

    inner: T
    """The wrapped value inside the Trail"""
    iterable: InitVar[Iterable[L]]
    logs: deque[L] = field(init=False)
    """The logs attached to the value"""

    __match_args__ = ("inner", "logs")

    def __post_init__(self, iterable: Iterable[L]) -> None:
        self.logs = deque(iterable)

    def to_tuple(self) -> Tuple[T, list[L]]: 
        """Convenience method to pack inner and logs to tuple

        Returns:
            Tuple[T, list[L]]: Data packed as a tuple
        """
        return self.inner, self.logs
    
    def map(self, op: Callable[[T], U], *logs: L) -> Trail[U]:
        """Runs a function over the wrapped value, attaching new logs

        Args:
            op (Callable[[T], U]): The function to run over

        Returns:
            Trail[U]: A reference to the new Trail
        """
        self.logs.extend(logs)
        return Trail(op(self.inner), self.logs.copy())
    
    def and_then(self, op: Callable[[T], Trail[U]], *logs: L) -> Trail[U]:
        """Handles logs for running functions over the value that return Trail

        Args:
            op (Callable[[T], Trail[U]]): A function that takes the wrapped value and returns Trail

        Returns:
            Trail[U]: Updated version of the Trail
        """
        new = op(self.inner)
        self.logs.extend(new.logs)
        self.logs.extend(logs)
        return Trail(new.inner, self.logs.copy())
