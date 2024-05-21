"""Additional functions to supplement working with dicts

Includes functions for getting, putting, and mapping over dictionaries.

Examples: ::
        
    >>> data: dict[str, int] = {'First': 1, 'Second': 2}
    >>> upper_dict: dict[str, int] = map_keys(str.upper)(data)
    >>> upper_keys: tuple[str, ...] = tuple(upper_dict.keys())
    >>> upper_keys == ('FIRST', 'SECOND')
    True
    >>> data: dict[str, int] = {'First': 1, 'Second': 2}
    >>> str_values_dict: dict[str, str] = map_values(str)(data)
    >>> tuple(str_values_dict.values())
    ('1', '2')

"""
from typing import TypeVar, Dict, Callable, Mapping, Tuple
from pythonix.internals.op import item
from pythonix.internals.res import Opt

V = TypeVar("V")
W = TypeVar("W")
K = TypeVar("K", str, int, float, tuple)
L = TypeVar("L", str, int, float, tuple)


def map_items(using: Callable[[K, V], Tuple[L, W]]):
    """Applies *using* with dict items to return a new dict with the results

    Example: ::

        >>> func = lambda k, v: (k, v + ' boy')
        >>> d = {'hello': 'joe'}
        >>> d2 = map_items(func)(d)
        >>> d2['hello']
        'joe boy'

    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[L, W]:
        return dict((using(k, v) for k, v in dict_obj.items()))

    return get_dict


def map_keys(using: Callable[[K], L]):
    """Applies *using* over dict keys to return a new dict with the results

    Example: ::
        
        >>> data: dict[str, int] = {'First': 1, 'Second': 2}
        >>> upper_dict: dict[str, int] = map_keys(str.upper)(data)
        >>> upper_keys: tuple[str, ...] = tuple(upper_dict.keys())
        >>> upper_keys == ('FIRST', 'SECOND')
        True

    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[L, V]:
        return {using(k): v for k, v in dict_obj.items()}

    return get_dict


def map_values(using: Callable[[V], W]):
    """Applies *using* over dict values to return a new dict with the results

    Example: ::

        >>> data: dict[str, int] = {'First': 1, 'Second': 2}
        >>> str_values_dict: dict[str, str] = map_values(str)(data)
        >>> tuple(str_values_dict.values())
        ('1', '2')

    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[K, W]:
        return {k: using(v) for k, v in dict_obj.items()}

    return get_dict


def filter_keys(predicate: Callable[[K], bool]):
    """Applies *predicate* over keys, keeping only those that evaluate to True

    Example : ::

        >>> data: dict[str, int] = {'First': 1, 'Second': 2}
        >>> only_first: dict[str, int] = filter_keys(lambda key: key == 'First')(data)
        >>> tuple(only_first.values())
        (1,)

    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[K, V]:
        return {k: v for k, v in dict_obj.items() if predicate(k)}

    return get_dict


def filter_values(predicate: Callable[[V], bool]):
    """Applies *predicate* over values, keeping only those that evaluate to True

    Example: ::

        >>> data: dict[str, int] = {'First': 1, 'Second': 2}
        >>> evens_only: dict[str, int] = filter_values(lambda v: v % 2 == 0)(data)
        >>> tuple(*evens_only.items())
        ('Second', 2)

    """

    def get_dict(dict_obj: Dict[K, V]) -> Dict[K, V]:
        return {k: v for k, v in dict_obj.items() if predicate(v)}

    return get_dict


def merge(new_dict: Dict[L, W]):
    """Merges two dictionaries together, overriding the first with the second

    Example: ::
        
        >>> old: dict[str, int] = {'foo': 0}
        >>> new: dict[int, str] = {1: 'bar'}
        >>> merge(new)(old)
        {'foo': 0, 1: 'bar'}

    """

    def get_old(old_dict: Dict[K, V]) -> Dict[K | L, V | W]:
        return old_dict | new_dict

    return get_old


def put(key: L):
    """Puts a new value into a `dict`.

    Example: ::

        >>> data: dict[str, int] = {'hello': 0}
        >>> put('joe')(1)(data)
        {'joe': 1, 'hello': 0}

    """

    def get_val(
        val: W,
    ) -> Callable[[Dict[K, V]], Dict[K | L, V | W]]:
        def get_dict(dict_obj: Dict[K, V]) -> Dict[K | L, V | W]:
            return merge(dict_obj)({key: val})

        return get_dict

    return get_val


def get(key: K):
    """Gets value from dict as Ok[T], or Err[Nil] if not found

    Example: ::

        >>> d = {'foo': 'bar'}
        >>> bar = get('foo')(d)
        >>> val, err = bar
        >>> val
        'bar'

    """

    def get_data(mapping: Mapping[K, V]) -> Opt[V]:
        return item(key)(mapping)

    return get_data
