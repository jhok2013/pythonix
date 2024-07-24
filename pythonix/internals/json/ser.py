from json import JSONEncoder, dumps, dump
from typing import Any, NamedTuple, Callable, NamedTuple, TypeVar, Generic
from _typeshed import SupportsWrite
from dataclasses import dataclass

from pythonix.res import Res, err, ok


class SerError(Exception):
    """Error class for capturing issues in converting objects to JSON"""

    def __init__(self, message: str = "An error occurred encoding or decoding JSON"):
        super().__init__(message)


class SerOpts(NamedTuple):
    """Default options for converting objects to JSON"""
    skip_keys: bool = False
    ensure_ascii: bool = True
    check_circular: bool = True
    allow_nan: bool = True
    cls: type[JSONEncoder] | None = None
    indent: int | str | None = None
    separators: tuple[str, str] | None = None
    default: Callable[[Any], Any] | None = None
    sort_keys: bool = False


T = TypeVar('T')


@dataclass(frozen=True)
class Serializer(Generic[T]):
    """Keeps data and options used to convert objects to JSON"""
    obj: T
    """Object to be converted to JSON encoded data"""
    options: SerOpts
    """Custom options for the conversion"""


def new(obj: T) -> Serializer[T]:
    """Creates a new Serializer with default options"""
    return Serializer(options=SerOpts(), obj=obj)


def with_opts(opts: SerOpts):
    """Updates serializer options"""
    def inner(serializer: Serializer[T]) -> Serializer[T]:
        base_opts = serializer.options._asdict().copy()
        base_opts.update(opts._asdict().copy())
        return Serializer(options=SerOpts(**base_opts), obj=serializer.obj)

    return inner


def clear_opts(serializer: Serializer[T]) -> Serializer[T]:
    """Clears current opts on a Serializer"""
    return new(serializer.obj)


def to(destination: SupportsWrite[str]):
    """Writes the JSON from a Serializer to a writable destination"""

    def inner(serializer: Serializer[T]) -> Res[SupportsWrite[str], SerError]:

        try:
            dump(serializer.obj, destination, **serializer.options)
            return ok(SerError)(destination)
        except (ValueError, TypeError) as e:
            return err(SupportsWrite[str])(SerError(str(e)))

    return inner


def as_str(serializer: Serializer[T]) -> Res[str, SerError]:
    """Returns the JSON from a Serializer as a str"""
    try:
        return ok(SerError)(dumps(serializer.obj, **serializer.options))
    except (ValueError, TypeError) as e:
        return err(str)(SerError(str(e)))


def pretty(serializer: Serializer[T]) -> Serializer[T]:
    """Sets indent to 4"""
    return with_opts(SerOpts(indent=4))(serializer)


def plain(serializer: Serializer[T]) -> Serializer[T]:
    """Removes indentation"""
    return with_opts(SerOpts(indent=0))(serializer)


def plain_str(obj: T) -> Res[str, SerError]:
    """Outputs the obj as a JSON str"""
    return as_str(new(obj))

def pretty_str(obj: T) -> Res[str, SerError]:
    """Outputs the obj as a four indented JSON str"""
    return as_str(pretty(new(obj)))
