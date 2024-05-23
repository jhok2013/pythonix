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
from typing import TypeVar, Callable
from functools import wraps, WRAPPER_ASSIGNMENTS

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")
U = TypeVar("U")

assignments = list(WRAPPER_ASSIGNMENTS)
assignments.remove("__annotations__")
updated_assignments = WRAPPER_ASSIGNMENTS
# updated_assignments = tuple(assignments)


def to_end_two(func: Callable[[T1, T2], U]) -> Callable[[T2, T1], U]:
    """Moves the first arg of a two function argument to be the last instead

    Examples: ::

        >>> @to_end_two
        ... def join(iterable: list[str], delimiter: str) -> str:
        ...     return delimiter.join(iterable)
        ...
        >>> join(', ', ['hello', 'world'])
        'hello, world'

    """

    @wraps(func)
    def wrapped(t2: T2, t1: T1) -> U:
        return func(t1, t2)

    return wrapped


def two(func: Callable[[T1, T2], U]) -> Callable[[T1], Callable[[T2], U]]:
    """Turns a function of two args to a curried one with the same return type

    Example: ::

        >>> @two
        ... def add(x: int, y: int) -> int:
        ...     return x + y
        ...
        >>> add(10)(10)
        20
        >>> add_10 = add(10)
        >>> add_10(20)
        30

    """

    @wraps(func, assigned=updated_assignments)
    def in1(t1: T1) -> Callable[[T2], U]:
        def in2(t2: T2) -> U:
            return func(t1, t2)

        return in2

    return in1


def three(
    func: Callable[[T1, T2, T3], U]
) -> Callable[[T1], Callable[[T2], Callable[[T3], U]]]:
    """Same as ``two``, but handles three arguments"""

    @wraps(func, assigned=updated_assignments)
    def in1(t1: T1) -> Callable[[T2], Callable[[T3], U]]:
        def in2(t2: T2) -> Callable[[T3], U]:
            def in3(t3: T3) -> U:
                return func(t1, t2, t3)

            return in3

        return in2

    return in1


def four(
    func: Callable[[T1, T2, T3, T4], U]
) -> Callable[[T1], Callable[[T2], Callable[[T3], Callable[[T4], U]]]]:
    """Same as ``two``, but handles four arguments"""

    @wraps(four)
    def in1(t1: T1) -> Callable[[T2], Callable[[T3], Callable[[T4], U]]]:
        def in2(t2: T2) -> Callable[[T3], Callable[[T4], U]]:
            def in3(t3: T3) -> Callable[[T4], U]:
                def in4(t4: T4) -> U:
                    return func(t1, t2, t3, t4)

                return in4

            return in3

        return in2

    return in1


def five(
    func: Callable[[T1, T2, T3, T4, T5], U]
) -> Callable[[T1], Callable[[T2], Callable[[T3], Callable[[T4], Callable[[T5], U]]]]]:
    """Same as ``two``, but handles five arguments"""

    @wraps(func, assigned=updated_assignments)
    def in1(
        t1: T1,
    ) -> Callable[[T2], Callable[[T3], Callable[[T4], Callable[[T5], U]]]]:
        def in2(t2: T2) -> Callable[[T3], Callable[[T4], Callable[[T5], U]]]:
            def in3(t3: T3) -> Callable[[T4], Callable[[T5], U]]:
                def in4(t4: T4) -> Callable[[T5], U]:
                    def in5(t5: T5) -> U:
                        return func(t1, t2, t3, t4, t5)

                    return in5

                return in4

            return in3

        return in2

    return in1


def six(
    func: Callable[[T1, T2, T3, T4, T5, T6], U]
) -> Callable[
    [T1],
    Callable[[T2], Callable[[T3], Callable[[T4], Callable[[T5], Callable[[T6], U]]]]],
]:
    """Same as ``two``, but handles six arguments"""

    @wraps(func, assigned=updated_assignments)
    def in1(
        t1: T1,
    ) -> Callable[
        [T2], Callable[[T3], Callable[[T4], Callable[[T5], Callable[[T6], U]]]]
    ]:
        def in2(
            t2: T2,
        ) -> Callable[[T3], Callable[[T4], Callable[[T5], Callable[[T6], U]]]]:
            def in3(t3: T3) -> Callable[[T4], Callable[[T5], Callable[[T6], U]]]:
                def in4(t4: T4) -> Callable[[T5], Callable[[T6], U]]:
                    def in5(t5: T5) -> Callable[[T6], U]:
                        def in6(t6: T6) -> U:
                            return func(t1, t2, t3, t4, t5, t6)

                        return in6

                    return in5

                return in4

            return in3

        return in2

    return in1


def seven(
    func: Callable[[T1, T2, T3, T4, T5, T6, T7], U]
) -> Callable[
    [T1],
    Callable[
        [T2],
        Callable[
            [T3], Callable[[T4], Callable[[T5], Callable[[T6], Callable[[T7], U]]]]
        ],
    ],
]:
    """Same as ``two``, but handles seven arguments"""

    @wraps(func, assigned=updated_assignments)
    def in1(
        t1: T1,
    ) -> Callable[
        [T2],
        Callable[
            [T3], Callable[[T4], Callable[[T5], Callable[[T6], Callable[[T7], U]]]]
        ],
    ]:
        def in2(
            t2: T2,
        ) -> Callable[
            [T3], Callable[[T4], Callable[[T5], Callable[[T6], Callable[[T7], U]]]]
        ]:
            def in3(
                t3: T3,
            ) -> Callable[[T4], Callable[[T5], Callable[[T6], Callable[[T7], U]]]]:
                def in4(t4: T4) -> Callable[[T5], Callable[[T6], Callable[[T7], U]]]:
                    def in5(t5: T5) -> Callable[[T6], Callable[[T7], U]]:
                        def in6(t6: T6) -> Callable[[T7], U]:
                            def in7(t7: T7) -> U:
                                return func(t1, t2, t3, t4, t5, t6, t7)

                            return in7

                        return in6

                    return in5

                return in4

            return in3

        return in2

    return in1


def eight(
    func: Callable[[T1, T2, T3, T4, T5, T6, T7, T8], U]
) -> Callable[
    [T1],
    Callable[
        [T2],
        Callable[
            [T3],
            Callable[
                [T4], Callable[[T5], Callable[[T6], Callable[[T7], Callable[[T8], U]]]]
            ],
        ],
    ],
]:
    """Same as ``two``, but handles eight arguments"""

    @wraps(func, assigned=updated_assignments)
    def in1(
        t1: T1,
    ) -> Callable[
        [T2],
        Callable[
            [T3],
            Callable[
                [T4], Callable[[T5], Callable[[T6], Callable[[T7], Callable[[T8], U]]]]
            ],
        ],
    ]:
        def in2(
            t2: T2,
        ) -> Callable[
            [T3],
            Callable[
                [T4], Callable[[T5], Callable[[T6], Callable[[T7], Callable[[T8], U]]]]
            ],
        ]:
            def in3(
                t3: T3,
            ) -> Callable[
                [T4], Callable[[T5], Callable[[T6], Callable[[T7], Callable[[T8], U]]]]
            ]:
                def in4(
                    t4: T4,
                ) -> Callable[[T5], Callable[[T6], Callable[[T7], Callable[[T8], U]]]]:
                    def in5(
                        t5: T5,
                    ) -> Callable[[T6], Callable[[T7], Callable[[T8], U]]]:
                        def in6(t6: T6) -> Callable[[T7], Callable[[T8], U]]:
                            def in7(t7: T7) -> Callable[[T8], U]:
                                def in8(t8: T8) -> U:
                                    return func(t1, t2, t3, t4, t5, t6, t7, t8)

                                return in8

                            return in7

                        return in6

                    return in5

                return in4

            return in3

        return in2

    return in1


def nine(
    func: Callable[[T1, T2, T3, T4, T5, T6, T7, T8, T9], U]
) -> Callable[
    [T1],
    Callable[
        [T2],
        Callable[
            [T3],
            Callable[
                [T4],
                Callable[
                    [T5],
                    Callable[[T6], Callable[[T7], Callable[[T8], Callable[[T9], U]]]],
                ],
            ],
        ],
    ],
]:
    """Same as ``two``, but handles nine arguments"""

    @wraps(func, assigned=updated_assignments)
    def in1(
        t1: T1,
    ) -> Callable[
        [T2],
        Callable[
            [T3],
            Callable[
                [T4],
                Callable[
                    [T5],
                    Callable[[T6], Callable[[T7], Callable[[T8], Callable[[T9], U]]]],
                ],
            ],
        ],
    ]:
        def in2(
            t2: T2,
        ) -> Callable[
            [T3],
            Callable[
                [T4],
                Callable[
                    [T5],
                    Callable[[T6], Callable[[T7], Callable[[T8], Callable[[T9], U]]]],
                ],
            ],
        ]:
            def in3(
                t3: T3,
            ) -> Callable[
                [T4],
                Callable[
                    [T5],
                    Callable[[T6], Callable[[T7], Callable[[T8], Callable[[T9], U]]]],
                ],
            ]:
                def in4(
                    t4: T4,
                ) -> Callable[
                    [T5],
                    Callable[[T6], Callable[[T7], Callable[[T8], Callable[[T9], U]]]],
                ]:
                    def in5(
                        t5: T5,
                    ) -> Callable[
                        [T6], Callable[[T7], Callable[[T8], Callable[[T9], U]]]
                    ]:
                        def in6(
                            t6: T6,
                        ) -> Callable[[T7], Callable[[T8], Callable[[T9], U]]]:
                            def in7(t7: T7) -> Callable[[T8], Callable[[T9], U]]:
                                def in8(t8: T8) -> Callable[[T9], U]:
                                    def in9(t9: T9) -> U:
                                        return func(t1, t2, t3, t4, t5, t6, t7, t8, t9)

                                    return in9

                                return in8

                            return in7

                        return in6

                    return in5

                return in4

            return in3

        return in2

    return in1
