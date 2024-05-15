from typing import NamedTuple, ParamSpec, Callable, Tuple, TypeVar
from pythonix.op import mapx
from pythonix.pipe import Bind
from pythonix.res import Res
import pythonix.pair as pair
from functools import singledispatch
from requests import (
    get as _get,
    post as _post,
    put as _put,
    delete as _delete,
    Response as OGResponse,
    HTTPError,
)
from pythonix.internals.pair import Pair, Pairs
from pythonix.internals.pipe import Bind
from pythonix import res

P = ParamSpec("P")


class Response(NamedTuple):
    """
    Parsed response from an HTTP request.
    """

    url: str
    body: bytes
    status: int


def parse_response(response: OGResponse) -> Response:
    """
    Converts a response from a `requests` library HTTP request to a `pythonix` response
    """
    return Response(response.url, response.content, response.status_code)


@res.safe(HTTPError)
def check_status(response: OGResponse) -> OGResponse:
    """
    Captures an `HTTPError` from a `requests` HTTP response in `Result`
    """
    response.raise_for_status()
    return response


class Request(NamedTuple):
    """
    Request type to be sent via an HTTP method
    """

    url: str
    headers: Pairs[bytes]
    params: Pairs[bytes]
    data: Pairs[bytes]


RequestType = TypeVar("RequestType", bound="Request")


class Get(Request):
    """
    An HTTP request set as a `GET`
    """

    method: Callable[P, Response] = _get


class Post(Request):
    """
    An HTTP request set as a `POST`
    """

    method: Callable[P, Response] = _post


class Put(Request):
    """
    An HTTP request set as a `PUT`
    """

    method: Callable[P, Response] = _put


class Delete(Request):
    """
    An HTTP request set as a `DELETE`
    """

    method: Callable[P, Response] = _delete

R = TypeVar('R', bound='Request')

@singledispatch
def to_bytes(value: int) -> bytes:
    return bytes(value)


@to_bytes.register(str)
def _(value: str) -> bytes:
    return bytes(value, "utf-8")


def set_value_to_bytes(keyvalue: Pair[str | int]) -> Pair[bytes]:
    Bind(keyvalue)(pair.map(to_bytes)).inner


def get(url: str):
    """
    Set the URL for the request type
    """

    def get_headers(*headers: Pair[str | int]):
        """
        Add key value pairs to represent headers
        #### Example
        ```python
        new(Get)('https://helloworld.com')(
            pair.new('Authorization')('Bearer asdfasdfads'),
            pair.new('Content-Type')('application/json'),
        )
        ```
        """

        def get_params(*params: Pair[str | int]):
            """
            Add key value pairs to represent params. Same methodology as for headers.
            """
            return Get(
                url,
                tuple(mapx(set_value_to_bytes)(headers)),
                tuple(mapx(set_value_to_bytes)(params)),
                tuple(),
            )

        return get_params

    return get_headers


def post(url: str):
    """
    Set the URL for the request type
    """

    def get_headers(*headers: Pair[str | int]):
        """
        Add key value pairs to represent headers
        #### Example
        ```python
        new(Get)('https://helloworld.com')(
            pair.new('Authorization')('Bearer asdfasdfads'),
            pair.new('Content-Type')('application/json'),
        )
        ```
        """

        def get_params(*params: Pair[str | int]):
            """
            Add key value pairs to represent params. Same methodology as for headers.
            """

            def get_data(*data: Pair[str | int]):
                """
                Add key value pairs to represent data for the request
                """
                return Post(
                    url,
                    tuple(mapx(set_value_to_bytes)(headers)),
                    tuple(mapx(set_value_to_bytes)(params)),
                    tuple(mapx(set_value_to_bytes)(data)),
                )

            return get_data

        return get_params

    return get_headers


def put(url: str):
    """
    Set the URL for the request type
    """

    def get_headers(*headers: Pair[str | int]):
        """
        Add key value pairs to represent headers
        #### Example
        ```python
        new(Get)('https://helloworld.com')(
            pair.new('Authorization')('Bearer asdfasdfads'),
            pair.new('Content-Type')('application/json'),
        )
        ```
        """

        def get_params(*params: Pair[str | int]):
            """
            Add key value pairs to represent params. Same methodology as for headers.
            """

            def get_data(*data: Pair[str | int]):
                """
                Add key value pairs to represent data for the request
                """
                return Put(
                    url,
                    tuple(mapx(set_value_to_bytes)(headers)),
                    tuple(mapx(set_value_to_bytes)(params)),
                    tuple(mapx(set_value_to_bytes)(data)),
                )

            return get_data

        return get_params

    return get_headers


def delete(url: str):
    """
    Set the URL for the request type
    """

    def get_headers(*headers: Pair[str | int]):
        """
        Add key value pairs to represent headers
        #### Example
        ```python
        new(Get)('https://helloworld.com')(
            pair.new('Authorization')('Bearer asdfasdfads'),
            pair.new('Content-Type')('application/json'),
        )
        ```
        """
        return Post(url, tuple(mapx(set_value_to_bytes)(headers)), tuple(), tuple())

    return get_headers


def set_url(url: str):
    """
    Recreates the given request type with a new URL
    """

    def get_content(content: R) -> R:
        return content.__class__(url, content.headers, content.params, content.data)

    return get_content


def set_headers(*headers: Pair[str | int]):
    """
    Recreates the given request types with a new set of headers
    """

    def get_content(content: R) -> R:
        return content.__class__(content.url, headers, content.params, content.data)

    return get_content


def set_params(*params: Pair[str | int]):
    """
    Recreates the given request type with a new set of headers
    """

    def get_content(content: R) -> R:
        return content.__class__(content.url, content.headers, params, content.data)

    return get_content


def set_data(*data: Pair[str | int]):
    """
    Recreates the given request type with a new set of data
    """

    def get_content(content: R) -> R:
        return content.__class__(content.url, content.headers, content.params, data)

    return get_content


def body(content: RequestType) -> Tuple[Pair[bytes], ...]:
    """
    Combines the headers, params, and content of `Request`
    """
    return content.headers + content.params + content.data


def send(request: RequestType) -> Res[Response, HTTPError]:
    """
    Sends the provided `Request` and then parses its response, capturing any errors that occur.
    """
    return Bind(request)(body)(
        lambda body: {"url": request.url} | {k: v for k, v in body}
    )(lambda kwargs: request.method(**kwargs))(check_status)(
        res.map(parse_response)
    ).inner
