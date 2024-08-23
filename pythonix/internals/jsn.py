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
from typing import overload, Callable, TypeVar, Any, TypedDict, Protocol, Generic, cast
from pythonix.res import Res, Ok, Err

T = TypeVar('T')

class SupportsWrite(Protocol, Generic[T]):

    def write(self): ...

class SupportsRead(Protocol, Generic[T]):

    def read(self): ...

class JSONError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


DecodableT = TypeVar("DecodableT", str, float, int, dict, list, bool, None)
"""All types that can be decoded from a JSON encoded object"""


class EncodeOpts(TypedDict):
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


class DecodeOpts(TypedDict):
    """Struct for options to decode an object from JSON"""

    cls: type[JSONDecoder] | None = None
    object_hook: Callable[[dict[Any, Any]], Any] | None = None
    parse_float: Callable[[str], Any] | None = None
    parse_int: Callable[[str], Any] | None = None
    parse_constant: Callable[[str], Any] | None = None
    object_pairs_hook: Callable[[list[tuple[Any, Any]]], Any] | None = None


def pretty(options: EncodeOpts = EncodeOpts()) -> EncodeOpts:
    """Sets an EncodeOpts dictionary to have an indent of 4"""
    options.update(EncodeOpts(indent=4))
    return options


def encode(**options):
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
        encodeable_obj: SupportsWrite[str] | Any,
    ) -> Res[SupportsWrite[str], JSONError] | Res[str, JSONError]:
        try:
            if writable := hasattr(encodeable_obj, "write"):
                dump(encodeable_obj, **options)
                return Ok(encodeable_obj)
            return Ok(dumps(encodeable_obj, **options))
        except (ValueError, TypeError) as e:
            if writable:
                return Err(JSONError(str(e)))
            return Err(JSONError(str(e)))

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
            case str() | bytes() | bytearray():
                method = loads
            case reader if hasattr(reader, "read"):
                method = load
            case _:
                raise TypeError(
                    "Invalid type. Expected deserializable type or one that supports read"
                )

        try:
            if not isinstance(
                decoded := method(decodable_json, **options), expected_type
            ):
                return Err(JSONError(f"Expected to decode {type(expected_type)} but found {type(decoded)}"))
            return Ok(decoded)
        except (ValueError, TypeError, JSONDecodeError) as e:
            return Err(JSONError(str(e)))

    return get_obj
