"""Function decorators for automatic currying of declared functions

Examples: ::

    >>> @two
    ... def add(x: int, y: int) -> int:
    ...     return x + y
    ...
    >>> add(10)(10)
    20
    >>> add_10 = add(10)
    >>> add_10(20)
    30

You can even use it in place to modify functions.

    >>> def join(delimiter: str, iterable: list[str]) -> str:
    ...     return delimiter.join(iterable)
    ...
    >>> join_curry = two(join)
    >>> join_curry(', ')(['hello', 'world'])
    'hello, world'

"""
from pythonix.internals.curry import two, three, four, five, six, seven, eight, nine, to_end_two
