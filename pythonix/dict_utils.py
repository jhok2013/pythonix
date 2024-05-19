"""Utility functions for common operations on dictionaries like mapping over keys or values.

The functions allow for retrieval and insertion of data on dictionaries in a type safe and
unsurprising way. Retrieving value by key return results of *Ok[T] | Err[Nil]*. They can then
be handled using the res submodule or through pattern matching or unpacking. These functions
are curried with the subject as the last step, which makes them compliant for use with Bind, Do,
and Pipe.
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
