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
from pythonix.internals.dict_utils import (
    filter_keys,
    filter_values,
    map_keys,
    map_values,
    merge,
    put,
    get,
)
