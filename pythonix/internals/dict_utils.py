"""Utility functions for common operations on dictionaries like mapping over keys or values.

The functions allow for retrieval and insertion of data on dictionaries in a type safe and
unsurprising way. Retrieving value by key return results of *Ok[T] | Err[Nil]*. They can then
be handled using the res submodule or through pattern matching or unpacking. These functions
are curried with the subject as the last step, which makes them compliant for use with Bind, Do,
and Pipe.
"""
from typing import TypeVar, Dict, Callable, Mapping, Tuple
from pythonix.internals.op import item

V = TypeVar("V")
W = TypeVar("W")
K = TypeVar("K", str, int, float, tuple)
L = TypeVar("L", str, int, float, tuple)


def map_items(using: Callable[[K, V], Tuple[L, W]]):
    """Applies the provided function against the key-value pairs in a dictionary, returning
    a new dictionary from the results.

    Example:
        ```python
        func = lambda k, v: (k, v + ' boy')
        d = {'hello': 'joe'}
        d2 = dict_utils.map_items(foo)(d)
        assert d2['hello'] == 'joe boy'
        ```
    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[L, W]:
        return dict((using(k, v) for k, v in dict_obj.items()))

    return get_dict


def map_keys(using: Callable[[K], L]):
    """Runs the provided function over each key in a dictionary, returning a new
    dictionary with the updated keys and the same values

    Example:
        ```python
        data: dict[str, int] = {'First': 1, 'Second': 2}
        upper_dict: dict[str, int] = dict_utils.map_keys(str.upper)(data)
        upper_keys: tuple[str, ...] = tuple(upper_dict.keys())
        assert upper_keys == ('FIRST', 'SECOND')
        ```
    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[L, V]:
        return {using(k): v for k, v in dict_obj.items()}

    return get_dict


def map_values(using: Callable[[V], W]):
    """Runs the provided function over each value in a `dict`, returning a new
    `dict` with the updated values and the same keys

    Example:
        ```python
        import pythonix.dict_utils as dict_utils

        data: dict[str, int] = {'First': 1, 'Second': 2}
        str_values_dict: dict[str, str] = dict_utils.map_values(str)
        values: tuple[str, ...] = tuple(str_values_dict.values())
        assert values == ('1', '2')
        ```
    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[K, W]:
        return {k: using(v) for k, v in dict_obj.items()}

    return get_dict


def filter_keys(predicate: Callable[[K], bool]):
    """Runs the provided filter function over the keys in a `dict`, returning a new `dict`
    with only the `keys` that evaluated to `True`

    Example:
        ```python
        import pythonix.dict_utils as dict_utils

        data: dict[str, int] = {'First': 1, 'Second': 2}
        only_first: dict[str, int] = dict_utils.filter_keys(lambda key: key == 'First')
        assert tuple(only_first.items()) == ('First', 1)
        ```
    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[K, V]:
        return {k: v for k, v in dict_obj.items() if predicate(k)}

    return get_dict


def filter_values(predicate: Callable[[V], bool]):
    """Runs the provided filter function over the values in a `dict`, returning a new `dict`
    with only the values that evaluated to `True`

    Example:
        ```python
        import pythonix.dict_utils as dict_utils

        data: dict[str, int] = {'First': 1, 'Second': 2}
        evens_only: dict[str, int] = dict_utils.filter_values(lambda v: v % 2 == 0)
        assert tuple(evens_only.items()) == ('Second', 2)
        ```
    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[K, V]:
        return {k: v for k, v in dict_obj.items() if predicate(v)}

    return get_dict


def merge(new_dict: Dict[L, W]):
    """Merges two dictionaries together, with values in the `old_dict` overrinding the values from the `new_dict`

    Example:
        ```python
        old: dict[str, int] = {'foo': 0}
        new: dict[int, str] = {1: 'bar'}
        merged: dict[str | int, str | int] = merge(new)(old)
        ```
    """

    def get_old(old_dict: Dict[K, V]) -> Dict[K | L, V | W]:
        return old_dict | new_dict

    return get_old


def put(key: L):
    """Puts a new value into a `dict`.

    Example:
        ```python
        data: dict[str, int] = {'hello': 0}
        updated: dict[str, int] = put('joe')(1)(data)
        ```
    """

    def get_val(
        val: W,
    ) -> Callable[[Dict[K, V]], Dict[K | L, V | W]]:
        def get_dict(dict_obj: Dict[K, V]) -> Dict[K | L, V | W]:
            return merge(dict_obj)({key: val})

        return get_dict

    return get_val


def get(key: K):
    """Retrieves a value from a mapping, returning `Nil` on error

    Example:
        ```python
        d = {'foo': 'bar'}
        bar = get('foo')(d)
        assert bar == 'bar'
        ```
    """

    def get_data(mapping: Mapping[K, V]):
        return item(key)(mapping)

    return get_data
