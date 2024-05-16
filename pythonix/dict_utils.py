"""
Functions used to shore up some of the deficiencies in the base `dict` implementation.
Allows for the mapping and filtering of keys and values for `dict` objects. Also provides
safe methods for assigning and retrieving items to a `dict`.
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
