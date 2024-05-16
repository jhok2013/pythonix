from __future__ import annotations
from functools import wraps
from typing import NamedTuple, Tuple, Callable, ParamSpec, TypeVar, Generic, overload
from datetime import datetime, timezone

P = ParamSpec("P")
LogType = TypeVar("LogType", bound="Log")
Val = TypeVar("Val")
NewVal = TypeVar("NewVal")


class Log(NamedTuple):
    '''Immutable container for log messages.

    Note:
        Avoid creating this directly and use the `info`, `debug`, `warning`, `error`,
        or `critical` functions instead.
    '''
    created_dt: datetime
    '''datetime object for when the object was created'''
    message: str
    '''The log message'''

    def __str__(self) -> str:
        return f'{type(self).__name__}("{self.created_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}", "{self.message}")'


class Info(Log):
    '''Log object at the INFO severity'''
    ...


class Debug(Log):
    '''Log object at the DEBUG severity'''
    ...


class Warning(Log):
    '''Log object at the WARNING severity'''
    ...


class Error(Log):
    '''Log object at the ERROR severity'''
    ...


class Critical(Log):
    '''Log object at the CRITICAL severity'''
    ...


def log(log_type: type[LogType]):
    """
    Creates a function to create a Log
    """

    def inner(message: str) -> LogType:
        '''Create a Log with the message and type'''
        return log_type(datetime.now(timezone.utc), message)

    return inner


debug = log(Debug)
'''Severity: DEBUG'''
info = log(Info)
'''Severity: INFO'''
warning = log(Warning)
'''Severity: WARNING'''
error = log(Error)
'''Severity: ERROR'''
critical = log(Critical)
'''Severity: CRITICAL'''


class Trail(Generic[Val], NamedTuple):
    """Container type used to wrap a value with a series of Log type records
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
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Trail[NewVal]:
            return new(*logs)(func(*args, **kwargs))

        return wrapper

    return inner


class Blaze(Generic[Val]):
    """Bind container used to accumulate log messages.
    
    Example:
        ```python
        blaze: Blaze[int] = Blaze(5, info('Starting'))
        logs: tuple[Log, ...] = (
            blaze
            (lambda x: x + 1, info('Added one'))
            (lambda x: x / 2, info('Divided by two'), debug('Val is now float'))
            (lambda x: x,     info('Finished'))
        ).logs
        ```   
    """

    logs: Tuple[Log, ...] = tuple()
    '''The sequence of accumulated logs'''
    inner: Trail[Val]
    '''The wrapped `Trail` value'''

    def __init__(self, inner: Val | Trail[Val], *logs: Log):
        '''Initializes the Blaze object.
        
        Args:
            inner (Val | Trail[Val]): The wrapped value. Can be anything or a `Trail` of anything.
            *logs (Log): Optional series of logs to be accumulated to the Blaze 

        '''
        match inner:
            case Trail():
                self.inner = inner
                self.logs = logs + inner.logs
            case _:
                self.inner = new()(inner)
                self.logs = logs

    @overload
    def __call__(
        self, using: Callable[[Val], trail.Trail[NewVal]], *logs: Log
    ) -> Blaze[NewVal]:
        ...

    @overload
    def __call__(self, using: Callable[[Val], NewVal], *logs: Log) -> Blaze[NewVal]:
        ...

    def __call__(
        self, using: Callable[[Val], Trail[NewVal] | NewVal], *logs: Log
    ) -> Blaze[NewVal]:
        """Calls the provided function on the contained value while appending any attached logs

        Args:
            using ((Val) -> Trail[NewVal] | Newval): Function that takes the contained value
            and returns a new one wrapped in `Trail` or not.
            *logs (Log): A series of any Log subclassed objects to be attached with the function call
        
        Returns:
            _ (Blaze[NewVal]): A new instance of a `Blaze` with the updated logs from the `using` function
            and the `*logs` arguments appended.
        
        """
        return Blaze(using(self.inner.inner), *(self.logs + logs))
