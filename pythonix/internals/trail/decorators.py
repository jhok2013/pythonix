from typing import TypeVar, Callable, ParamSpec
from pythonix.internals.trail.trail import Trail, Log, Info

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E", bound="Exception")
L = TypeVar("L", bound="Log")


def start(*logs: Log):
    """Wraps the function in a Trail with any number of Logs attached.
    If composing functions with Trail, you want to start with this one and
    then use the `then` themed decorators. If using `Res`, make sure that the
    `Trail` is wrapped in `Ok`, instead of having the `Trail` wrap `Ok`.

    ## Example

    >>> def hello() -> str:
    ...     return 'Hello world!'
    ...
    >>> hello = start(Info("Starting"))(hello)
    >>> hello = then_log(Info("Ending"))(hello)
    >>> greeting: Trail[str] = hello()
    >>> greeting.logs.pop().message
    'Ending'

    """

    def inner(func: Callable[P, U]) -> Callable[P, Trail[U]]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Trail[U]:
            return Trail(func(*args, **kwargs), logs)

        return wrapper

    return inner


def then_log_top(*logs: Log):
    def inner(func: Callable[P, Trail[U]]):
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Trail[U]:
            trail = func(*args, **kwargs)
            trail.logs.extendleft(logs)
            return trail

        return wrapper

    return inner


def then_log(*logs: Log):
    def inner(func: Callable[P, Trail[U]]):
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Trail[U]:
            trail = func(*args, **kwargs)
            trail.logs.extend(logs)
            return trail

        return wrapper

    return inner