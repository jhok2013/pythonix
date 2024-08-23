# from typing import NamedTuple, ParamSpec, Callable, TypeVar, overload
# from pythonix.internals.res import Res, safe, map as rmap
# from pythonix.internals.pair import Pair, Pairs
# from requests import (
#     get as _get,
#     post as _post,
#     put as _put,
#     delete as _delete,
#     Response as OGResponse,
#     HTTPError,
# )

# P = ParamSpec("P")


# class Response(NamedTuple):
#     """
#     Parsed response from an HTTP request.
#     """

#     url: str
#     body: bytes
#     status: int


# def parse_response(response: OGResponse) -> Response:
#     """
#     Converts a response from a `requests` library HTTP request to a `pythonix` response
#     """
#     return Response(response.url, response.content, response.status_code)


# @safe(HTTPError)
# def check_status(response: OGResponse) -> OGResponse:
#     """
#     Captures an `HTTPError` from a `requests` HTTP response in `Result`
#     """
#     response.raise_for_status()
#     return response


# class Request(NamedTuple):
#     """
#     Request type to be sent via an HTTP method
#     """

#     url: str
#     headers: Pairs[bytes] = tuple()
#     params: Pairs[bytes] = tuple()
#     data: Pairs[bytes] = tuple()


# class Get(Request):
#     """An HTTP request set as a `GET`"""

#     method: Callable[P, Response] = _get


# class Post(Request):
#     """An HTTP request set as a `POST`"""

#     method: Callable[P, Response] = _post


# class Put(Request):
#     """An HTTP request set as a `PUT`"""

#     method: Callable[P, Response] = _put


# class Delete(Request):
#     """An HTTP request set as a `DELETE`"""

#     method: Callable[P, Response] = _delete


# RequestT = TypeVar("RequestT", Get, Put, Post, Delete)
# """Generic type constrained to Get, Put, Post, or Delete"""


# @overload
# def to_bytes(value: int) -> bytes:
#     ...


# @overload
# def to_bytes(value: str) -> bytes:
#     ...


# @overload
# def to_bytes(value: Pair[str | int]) -> Pair[bytes]:
#     ...


# def to_bytes(value: str | int | Pair[str | int]) -> bytes | Pair[bytes]:
#     """Converts a value to bytes or Pair[bytes] if possible"""

#     match value:
#         case str(inner):
#             return bytes(inner, encoding="utf-8")
#         case int(inner):
#             return bytes(inner)
#         case Pair(key, str(inner)):
#             return Pair(key, bytes(inner, encoding="utf-8"))
#         case Pair(key, int(inner)):
#             return Pair(key, bytes(inner))
#         case _:
#             raise TypeError("Invalid type. Must be str, int, or a Pair[str | int]")


# @overload
# def url(value: str) -> Callable[[RequestT], RequestT]:
#     ...


# @overload
# def url(value: RequestT) -> str:
#     ...


# def url(value: str | RequestT):
#     """Sets or retrieves the url from a Request"""
#     match value:
#         case str(inner):

#             def get_request(request: RequestT) -> RequestT:
#                 match request:
#                     case Get(_, headers, params, data):
#                         return Get(inner, headers, params, data)
#                     case Post(_, headers, params, data):
#                         return Post(inner, headers, params, data)
#                     case Put(_, headers, params, data):
#                         return Put(inner, headers, params, data)
#                     case Delete(_, headers, params, data):
#                         return Delete(inner, headers, params, data)
#                     case _:
#                         raise TypeError(
#                             "Invalid request type provided. Expected Get, Post, Put, or Delete"
#                         )

#             return get_request

#         case Get(url) | Post(url) | Put(url) | Delete(url):
#             return url
#         case _:
#             raise TypeError(
#                 "Invalid argument. Expected a str for a new url or a Request subtype"
#             )


# @overload
# def headers(*values: Pair[str | int]) -> Callable[[RequestT], RequestT]:
#     ...


# @overload
# def headers(values: RequestT) -> Pairs[bytes]:
#     ...


# def headers(*values: Pair[str | int] | RequestT):
#     """Sets or retrieves the headers of a Request"""

#     first, *rest = values

#     match first:
#         case Get(_, headers) | Post(_, headers) | Put(_, headers) | Delete(_, headers):
#             return headers
#         case Pair(key, str(value)) | Pair(key, int(value)):
#             pairs: tuple[Pair[str | int], ...] = (first,) + tuple(rest)

#             def get_request(request: RequestT) -> RequestT:
#                 new_headers: Pairs[bytes] = tuple((to_bytes(pair) for pair in pairs))

#                 match request:
#                     case Get(url, _, params, data):
#                         return Get(url, new_headers, params, data)

#                     case Post(url, _, params, data):
#                         return Post(url, new_headers, params, data)

#                     case Put(url, _, params, data):
#                         return Put(url, new_headers, params, data)

#                     case Delete(url, _, params, data):
#                         return Delete(url, new_headers, params, data)
#                     case _:
#                         raise TypeError(
#                             "Invalid argument. Must be a subclass of Request"
#                         )

#             return get_request
#         case Pair():
#             raise TypeError("Invalid Pair. Pair value must be str or int")
#         case _:
#             raise TypeError("Invalid argument. Must be Pair or a Request subclass")


# @overload
# def params(*values: Pair[str | int]) -> Callable[[RequestT], RequestT]:
#     ...


# @overload
# def params(values: RequestT) -> Pairs[bytes]:
#     ...


# def params(
#     *values: Pair[str | int] | RequestT,
# ) -> Callable[[RequestT], RequestT] | Pairs[bytes]:
#     """Sets or retrieves the params of a Request"""

#     first, *rest = values

#     match first:
#         case Get(_, headers) | Post(_, headers) | Put(_, headers) | Delete(_, headers):
#             return headers
#         case Pair(_, str(_)) | Pair(_, int(_)):
#             pairs: tuple[Pair[str | int], ...] = (first,) + tuple(rest)

#             def get_request(request: RequestT) -> RequestT:
#                 new_params: Pairs[bytes] = tuple((to_bytes(pair) for pair in pairs))

#                 match request:
#                     case Get(url, headers, _, data):
#                         return Get(url, headers, new_params, data)

#                     case Post(url, headers, _, data):
#                         return Post(url, headers, new_params, data)

#                     case Put(url, headers, _, data):
#                         return Put(url, headers, new_params, data)

#                     case Delete(url, headers, _, data):
#                         return Delete(url, headers, new_params, data)
#                     case _:
#                         raise TypeError(
#                             "Invalid argument. Must be a subclass of Request"
#                         )

#             return get_request
#         case Pair():
#             raise TypeError("Invalid Pair. Pair value must be str or int")
#         case _:
#             raise TypeError("Invalid argument. Must be Pair or a Request subclass")


# @overload
# def data(*values: Pair[str | int]) -> Callable[[RequestT], RequestT]:
#     ...


# @overload
# def data(values: RequestT) -> Pairs[bytes]:
#     ...


# def data(
#     *values: Pair[str | int] | RequestT,
# ) -> Callable[[RequestT], RequestT] | Pairs[bytes]:
#     """Sets or retrieves the data of a Request"""
#     first, *rest = values

#     match first:
#         case Get(_, headers) | Post(_, headers) | Put(_, headers) | Delete(_, headers):
#             return headers
#         case Pair(_, str(_)) | Pair(_, int(_)):
#             pairs: tuple[Pair[str | int], ...] = (first,) + tuple(rest)

#             def get_request(request: RequestT) -> RequestT:
#                 new_data: Pairs[bytes] = tuple((to_bytes(pair) for pair in pairs))

#                 match request:
#                     case Get(url, headers, params, _):
#                         return Get(url, headers, params, new_data)

#                     case Post(url, headers, params, _):
#                         return Post(url, headers, params, new_data)

#                     case Put(url, headers, params, _):
#                         return Put(url, headers, params, new_data)

#                     case Delete(url, headers, params, data):
#                         return Delete(url, headers, params, new_data)
#                     case _:
#                         raise TypeError(
#                             "Invalid argument. Must be a subclass of Request"
#                         )

#             return get_request
#         case Pair():
#             raise TypeError("Invalid Pair. Pair value must be str or int")
#         case _:
#             raise TypeError("Invalid argument. Must be Pair or a Request subclass")


# def body(content: RequestT) -> Pairs[bytes]:
#     """
#     Combines the headers, params, and content of `Request`
#     """
#     return content.headers + content.params + content.data


# def send(request: RequestT) -> Res[Response, HTTPError]:
#     """
#     Sends the provided `Request` and then parses its response, capturing any errors that occur.
#     """
#     og_response = request.method(
#         url=request.url,
#         headers=request.headers,
#         params=request.params,
#         data=request.data,
#     )
#     return rmap(parse_response)(check_status(og_response))
