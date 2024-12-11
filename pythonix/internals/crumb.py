"""Log accumulation wrapper types and decorator"""

from __future__ import annotations
from typing import (
    overload,
    Tuple,
    Callable,
    ParamSpec,
    TypeVar,
)
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pythonix.internals.traits import Unwrap, UnwrapAlt, Ad
from pythonix.internals.collections import Deq

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

    ## Examples ::

        >>> log = Info("Hello world")
        >>> message, dt = log.to_tuple()
        >>> message
        'Hello world'

    """

    __match_args__ = ("message", "created_dt")


class Debug(Log):
    """Log object at the DEBUG severity

    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples ::

        >>> log = Debug("Hello world")
        >>> message, dt = log.to_tuple()
        >>> message
        'Hello world'

    """

    __match_args__ = ("message", "created_dt")


class Warning(Log):
    """Log object at the WARNING severity

    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples ::

        >>> log = Warning("Easy there")
        >>> message, dt = log.to_tuple()
        >>> message
        'Easy there'

    """

    __match_args__ = ("message", "created_dt")


class Error(Log):
    """Log object at the ERROR severity

    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples ::

        >>> log = Error("Oops!")
        >>> message, dt = log.to_tuple()
        >>> message
        'Oops!'

    """

    __match_args__ = ("message", "created_dt")


class Critical(Log):
    """Log object at the CRITICAL severity

    Attributes:
        message (str): The wrapped message
        created_dt (datetime): The datetime for when the Log is created

    ## Examples ::

        >>> log = Critical("Oh no!")
        >>> message, dt = log.to_tuple()
        >>> message
        'Oh no!'

    """

    __match_args__ = ("message", "created_dt")


@dataclass
class Crumb(Ad[T], Unwrap[T], UnwrapAlt[Deq[Log]]):
    """Simple log accumulator. Values are wrapped with a collection of Log objects. Can accumulate more logs using `logs` attribute and `map`

    #### Examples ::

        >>> c = Crumb(10, Info('Started with 10'))
        >>> c >>= lambda x: Crumb(x + 10, Info('Added 10'))
        >>> c.unwrap()
        20
        >>> c.logs[-1]
        Info('Added 10')

    """

    inner: T
    """Value wrapped with a Listad of Log objects"""
    logs: Deq[Log] = field(repr=False, compare=False)
    """Collection of accumulated Log objects"""

    def __init__(self, inner: T, *logs: Log) -> None:
        self.inner = inner
        self.logs = Deq(logs)

    @overload
    def __rshift__(self, using: Callable[[T], Crumb[U]]) -> Crumb[U]: ...

    @overload
    def __rshift__(self, using: Callable[[T], U]) -> Crumb[U]: ...

    def __irshift__(
        self, using: Callable[[T], Crumb[U]] | Callable[[T], U]
    ) -> Crumb[U]:
        return self.map(using)  # type: ignore

    @overload
    def __rshift__(self, using: Callable[[T], Crumb[U]]) -> Crumb[U]: ...

    @overload
    def __rshift__(self, using: Callable[[T], U]) -> Crumb[U]: ...

    def __rshift__(self, using: Callable[[T], Crumb[U]] | Callable[[T], U]) -> Crumb[U]:
        return self.map(using)  # type: ignore

    @overload
    def map(self, using: Callable[[T], Crumb[U]]) -> Crumb[U]: ...

    @overload
    def map(self, using: Callable[[T], U]) -> Crumb[U]: ...

    def map(self, using: Callable[[T], Crumb[U]] | Callable[[T], U]) -> Crumb[U]:
        """Runs a function that returns Crumb over inner value, appending any Crumbs from the output.

        Args:
            using ((T) -> Crumb[U]): Function that takes inner value and returns a new Crumb

        Returns:
            Crumb[U]: A new Crumb with updated logs from previous Crumb

        #### Examples: ::

            >>> c = Crumb(10, Info("Started process with 10"))
            >>> c >>= lambda x: Crumb(x + 10, Info("Added 10"))
            >>> c.unwrap()
            20
            >>> c.logs[-1]
            Info('Added 10')
        """
        match val := using(self.unwrap()):
            case Crumb():
                val.logs = self.logs + val.logs
                return val
            case u:
                return Crumb(u, *self.logs)

    def unwrap_alt(self) -> Deq[Log]:
        """Returns the accumulated Logs

        Returns:
            Deq[Log]: The accumulated logs
        """
        return self.logs

    def unwrap(self) -> T:
        """Returns the wrapped value

        Returns:
            T: The wrapped value
        """
        return self.inner


def crumb(*logs: Log):
    """Decorator that changes the output of the function to be Crumb with the Listad of Logs."""

    def get_func(func: Callable[P, U]):

        def get_args(*args: P.args, **kwargs: P.kwargs) -> Crumb[U]:

            return Crumb(func(*args, **kwargs), *logs)

        return get_args

    return get_func
