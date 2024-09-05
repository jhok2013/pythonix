"""Utility functions to encode and decode JSON values

To encode a value to JSON use `encode` ::

    >>> data: dict[str, str] = {"hello": "world"}
    >>> encoded_res = encode()(data)
    >>> encoded_res
    Ok(inner='{"hello": "world"}')

To decode a value from JSON use `decode` ::

    >>> decoded_res = decode(dict)('{"hello": "world"}')
    >>> decoded_res
    Ok(inner={'hello': 'world'})

"""
from pythonix.internals.jsn import (
    encode,
    decode,
    pretty,
    EncodeOpts,
    DecodeOpts,
    DecodableT,
)