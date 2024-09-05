"""Utility functions to encode and decode JSON values

To encode a value to JSON use `encode` ::

    >>> data: dict[str, str] = {"hello": "world"}
    >>> encoded_res: Res[str, JSONError] = encode()(data)
    >>> encoded_res
    Ok(inner='{"hello": "world"}')

To decode a value from JSON use `decode` ::

    >>> decoded_res: Res[dict, JSONError] = decode(dict)('{"hello": "world"}')
    >>> decoded_res
    Ok(inner={'hello': 'world'})

"""
from json import JSONDecodeError, JSONDecoder, JSONEncoder, load, loads, dump, dumps
from typing import (
    overload,
    Callable,
    TypeVar,
    Any,
    Protocol,
    Generic,
    runtime_checkable,
)
from dataclasses import dataclass, asdict
from pythonix.res import Res

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


@runtime_checkable
class SupportsWrite(Protocol, Generic[T_contra]):
    def write(self, s: T_contra, /) -> object:
        ...


@runtime_checkable
class SupportsRead(Protocol, Generic[T_co]):
    def read(self, length: int = ..., /) -> T_co:
        ...


class JSONError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


DecodableT = TypeVar("DecodableT", str, float, int, dict, list, bool, None)
"""All types that can be decoded from a JSON encoded object"""


@dataclass
class EncodeOpts:
    """Struct for options to encode an object to JSON"""

    skip_keys: bool = False
    ensure_ascii: bool = True
    check_circular: bool = True
    allow_nan: bool = True
    cls: type[JSONEncoder] | None = None
    indent: int | str | None = None
    separators: tuple[str, str] | None = None
    default: Callable[[Any], Any] | None = None
    sort_keys: bool = False


@dataclass
class DecodeOpts:
    """Struct for options to decode an object from JSON"""

    cls: type[JSONDecoder] | None = None
    object_hook: Callable[[dict[Any, Any]], Any] | None = None
    parse_float: Callable[[str], Any] | None = None
    parse_int: Callable[[str], Any] | None = None
    parse_constant: Callable[[str], Any] | None = None
    object_pairs_hook: Callable[[list[tuple[Any, Any]]], Any] | None = None


def pretty(options: EncodeOpts = EncodeOpts()) -> EncodeOpts:
    """Sets an EncodeOpts dictionary to have an indent of 4"""
    options.indent = 4
    return options


def encode(encode_opts: EncodeOpts):
    """Encode an object to JSON.

    Args:
        options (dict[str, Any]): kwargs argument. Should be unloaded from EncodeOpts
        encodeable_obj (SupportsWrite[str]): An object with a write method
        encodeable_obj (Any): An object that can be encoded to JSON

    Returns:
        write_result (Res[SupportsWrite[str], JSONError]): A result if encodeable_obj is SupportsWrite[str]
        result (Res[str, JSONError]): A result containing the encoded object as a str

    ## Examples ::

        >>> encodable: dict[str, str] = {"hello": "world"}
        >>> encoded_res: Res[str, JSONError] = encode()(encodable)
        >>> encoded_res
        Ok(inner='{"hello": "world"}')

    """

    @overload
    def get_obj(obj: SupportsWrite[str]) -> Res[SupportsWrite[str], JSONError]:
        ...

    @overload
    def get_obj(obj: Any) -> Res[str, JSONError]:
        ...

    def get_obj(
        obj: SupportsWrite[str] | Any,
    ) -> Res[SupportsWrite[str], JSONError] | Res[str, JSONError]:
        try:
            if writable := hasattr(obj, "write"):
                dump(obj, **asdict(encode_opts))
                return Res.Ok(obj)
            return Res[str, JSONError].Ok(dumps(obj, **asdict(encode_opts)))
        except (ValueError, TypeError) as e:
            if writable:
                return Res[SupportsWrite[str], JSONError].Err(JSONError(str(e)))
            return Res[str, JSONError].Err(JSONError(str(e)))

    return get_obj


def decode(expected_type: type[DecodableT] = dict, options: DecodeOpts = DecodeOpts()):
    """Decode an object from JSON

    Args:
        expected_type (type[DecodableT]): Default `dict`. The type to be expected when you decode
        options (DecodeOpts): Default `DecodeOpts()`. Options for decoding the JSON. Optional
        decodable_json (str | bytes | bytearray | SupportsRead[str]): JSON encoded data

    Returns:
        result (Res[DecodableT, JSONError]): Decoded JSON as your expected type. Or an Err.

    ## Examples

    >>> encoded: str = '{"hello": "world"}'
    >>> decoded: Res[dict, JSONError] = decode(dict)(encoded)
    >>> decoded
    Ok(inner={'hello': 'world'})

    """

    def get_obj(
        decodable_json: str | bytes | bytearray | SupportsRead[str],
    ) -> Res[DecodableT, JSONError]:
        match decodable_json:
            case str(d) | bytes(d) | bytearray(d):
                match loads(d, **asdict(options)):
                    case expected if isinstance(expected, expected_type):
                        return Res[DecodableT, JSONError].Ok(expected)
                    case unexpected_type:
                        return Res[DecodableT, JSONError].Err(
                            JSONError(
                                f"Expected a decodable type but found {type(unexpected_type)}"
                            )
                        )
            case supports_read if isinstance(supports_read, SupportsRead):
                match load(supports_read, **asdict(options)):
                    case expected if isinstance(expected, expected_type):
                        return Res[DecodableT, JSONError].Ok(expected)
                    case unexpected_type:
                        return Res[DecodableT, JSONError].Err(
                            JSONError(
                                f"Expected a decodable type but found {type(unexpected_type)}"
                            )
                        )
            case unexpected_type:
                return Res[DecodableT, JSONError].Err(
                    JSONError(
                        f"Expected a decodable type but found {type(unexpected_type)}"
                    )
                )

    return get_obj
