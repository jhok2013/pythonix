from typing import TypeVar, Callable, Any, NamedTuple, cast, TypeAlias
from json import JSONDecodeError, JSONDecoder, load, loads
from _typeshed import SupportsRead
from json import JSONDecoder

from pythonix.res import ok, err, Res, Ok, Err

DecodableT = TypeVar("DecodableT", str, float, int, dict, list, bool, None)
"""Any JSON decodable type including str, float, int, dict, list, bool, or None"""

Dynamic: TypeAlias = Any
"""Alias to Any. Meant to show decoded JSON data as undetermined"""


class DeError(Exception):
    """Error class meant to show issues within deserialization of JSON data"""

    def __init__(self, message: str = "An error occurred deserializing JSON"):
        return super().__init__(message)


class DeOpts(NamedTuple):
    """Default arguments for decoding JSON. Defaults can be overriden."""
    cls: type[JSONDecoder] | None = None
    object_hook: Callable[[dict[Any, Any]], Any] | None = None
    parse_float: Callable[[str], Any] | None = None
    parse_int: Callable[[str], Any] | None = None
    parse_constant: Callable[[str], Any] | None = None
    object_pairs_hook: Callable[[list[tuple[Any, Any]]], Any] | None = None


class DecodedJSON(NamedTuple):
    """Decoded JSON data, whose type has not been determined yet."""
    inner: Dynamic
    """Undetermined data from decoded JSON"""


class Deserializer(NamedTuple):
    """Inputs for reading JSON data to Python objects"""
    json_data: SupportsRead[str | bytes] | str | bytes | bytearray
    """raw json data from a file or readable type"""
    options: DeOpts
    """custom options for converting the json_data"""


def new(obj: SupportsRead[str | bytes] | str | bytes | bytearray) -> Deserializer:
    """Creates a Deserializer with default options"""
    return Deserializer(obj, DeOpts())


def with_opts(opts: DeOpts):
    """Updates options in Deserializer"""

    def inner(deserializer: Deserializer) -> Deserializer:
        base_opts = deserializer.options._asdict().copy()
        base_opts.update(opts._asdict())
        return Deserializer(deserializer.json_data, base_opts)

    return inner


def decode(deserializer: Deserializer) -> Res[DecodedJSON, DeError]:
    """Decodes JSON from Deserializer to DecodedJSON"""
    match deserializer:
        case Deserializer(obj, options):
            match obj:
                case str() | bytes() | bytearray():
                    try:
                        return ok(DeError)(DecodedJSON(loads(obj, **options)))
                    except (ValueError, TypeError, JSONDecodeError) as e:
                        return err(DecodedJSON)(DeError(str(e)))
                case reader if hasattr(reader, "read"):
                    try:
                        return ok(DeError)(DecodedJSON(load(obj, **options)))
                    except (ValueError, TypeError, JSONDecodeError) as e:
                        return err(DecodedJSON)(DeError(str(e)))
                case _:
                    raise TypeError("Invalid type. Expected deserializable type")
        case _:
            raise TypeError("Did not receive Deserializer")


def collect(expected_type: type[DecodableT]):
    """Enforces the expected type on DecodedJSON, returning expected type"""

    def inner(decoded: DecodedJSON) -> Res[DecodableT, DeError]:
        match decoded:
            case DecodedJSON(inner) if isinstance(inner, expected_type):
                return ok(DeError)(cast(DecodableT, inner))
            case DecodedJSON(inner):
                return err(DecodedJSON)(
                    DeError(
                        f"Cannot collect data. DecodedJSON value is {type(inner)} but expected {type(expected_type)}"
                    )
                )
            case _:
                raise TypeError(
                    f"Invalid type. Expected DecodedJSON and got {type(decoded)}"
                )

    return inner


def quick_decode(expected_type: type[DecodableT]):
    """Creates a Deserializer, decodes JSON, and collects to expected type"""

    def get_obj(obj: SupportsRead[str | bytes] | str | bytes | bytearray) -> Res[DecodableT, DeError]:

        match decode(new(obj)):
            case Ok(decoded):
                return collect(expected_type)(decoded)
            case Err(DeError(err)):
                return Err(DeError(err))
            case _:
                raise TypeError('Unexpected return value from decode')

    return get_obj
