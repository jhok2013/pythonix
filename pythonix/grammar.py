"""Tools simulating prefix, infix, and suffix applications.

Includes decorator classes for creating new grammar functions, a ``P`` instance
for performing arbitrary piping of values on the left to functions on the right,
and the ``Piper`` class for chaining function binds, applies, and dos on
values sequentially using >>, |, and >.

Examples:

    Piper: ::

        >>> with_operators: str = Piper(5) >> (lambda x: x + 10) | print > str
        15
        >>> with_methods: str = Piper(5).bind(lambda x: x + 10).do(print).apply(str)
        15

    Pipe (P): ::

        >>> sum([5, 5]) == 10
        True
        >>> [5, 5] |P| sum == 10
        True

    Prefix: ::

        >>> @PipePrefix
        ... def add_ten(x: int) -> int:
        ...     return x + 10
        ...
        >>> add_ten(10)
        20
        >>> add_ten | 10
        20

    Infix: ::

        >>> from functools import reduce
        >>> @PipeInfix
        ... def fold(func, iterable):
        ...     return reduce(func, iterable)
        ...
        >>> add = lambda x, y: x + y
        >>> add | fold | [1, 2, 3, 4]
        10
        >>> fold(add, [1, 2, 3, 4])
        10

    Suffix: ::

        >>> @PipeSuffix
        ... def add_ten(x: int) -> int:
        ...     return x + 10
        ...
        >>> 10 | add_ten
        20
        >>> add_ten(10)
        20

"""
from pythonix.internals.grammar import (
    PipeSuffix,
    PipeInfix,
    PipePrefix,
    PipeApplyInfix,
    PipeApplyPrefix,
    PipeApplySuffix,
    Piper,
    p,
    x,
    FnPipe,
    PipeFn,
    InfixPipe,
    ShiftApplyInfix,
    ShiftApplyPrefix,
    AndApplyPrefix,
    ShiftApplySuffix
)
