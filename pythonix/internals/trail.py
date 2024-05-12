from typing import NamedTuple, Tuple, Callable, ParamSpec, TypeVar, Generic
from datetime import datetime, timezone

P = ParamSpec("P")
LogType = TypeVar("LogType", bound="Log")
Val = TypeVar("Val")
NewVal = TypeVar("NewVal")


class Log(NamedTuple):
    datetime: datetime
    message: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}("{self.datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}", "{self.message}")'


class Info(Log):
    ...


class Debug(Log):
    ...


class Warning(Log):
    ...


class Error(Log):
    ...


class Critical(Log):
    ...


def log(log_type: type[LogType]):
    """
    Creates a new `Log` instance with the specified message attached
    """

    def inner(message: str) -> LogType:
        """
        Attach a message to the log
        """
        return log_type(datetime.now(timezone.utc), message)

    return inner


debug = log(Debug)
info = log(Info)
warning = log(Warning)
error = log(Error)
critical = log(Critical)


class Trail(Generic[Val], NamedTuple):
    """
    Container type used to wrap a value with a series of `Log` type records
    """

    logs: Tuple[Log, ...]
    inner: Val


def new(*logs: LogType):
    """
    Create a new `Trail` object with the desired logs attached.
    """

    def get_inner(inner: Val) -> Trail[Val]:
        """
        Attach the wrapped value to the `Trail`
        """
        return Trail(logs, inner)

    return get_inner


def append(*logs: LogType):
    """
    Append a new series of logs to a `Trail`
    """

    def inner(trail: Trail[Val]) -> Trail[Val]:
        return new(*(trail.logs + logs))(trail.inner)

    return inner


def logs(trail: Trail[Val]) -> Tuple[LogType, ...]:
    """
    Convenience function to return the logs of a `Trail`
    """
    return trail.logs


def trail(*logs: LogType):
    """
    Decorator function used to wrap the output of a function with a default set of logs.
    This also changes the output of the function to return a `Trail` of the type returned
    by the function.
    """

    def inner(func: Callable[P, NewVal]):
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Trail[NewVal]:
            return new(*logs)(func(*args, **kwargs))

        return wrapper

    return inner
