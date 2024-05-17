"""Functions used to operate over data structures.

Comparable to the filter, map, reduce, getitem, getattr, setitem, and setattr functions.
Can be used easily with the Bind, Pipe, and Do wrapper types. All functions are as
error proof as possible.

Examples:
    List:
        ```python
        from pythonix.prelude import *

        (
            Bind([1, 2, 3])
            (op.item(0))(q)
            (op.filterx(lambda x: x % 2 == 0))
            (op.mapx(lambda x: x + 1))
            (list)
            (op.item(0))(q)
            (prove.equals(3))(q)
        )
        ```
    Dict:
        ```python
        from pythonix.prelude import *

        (
            Bind({'hello': 'world'})
            (op.item(1))(q)
            (op.item('hello'))(q)
            (prove.equals('world))(q)
        )
        ```

    Object:
        ```python
        from pythonix.prelude import *

        (
            Bind(object.__new__(object))
            (op.item(2))(q)
            (op.assign('foo')('bar'))(q)
            (op.attr('foo'))(q)
            (prove.equals('bar'))(q)
        )
        ```

    Arg Application:
    ```python
        (
            (lambda x: x + 1)
            |P| op.arg(10)
            |P| prove.equals(11)
            |P| q
        )
    ```
"""
from pythonix.internals.op import filterx, mapx, fold, attr, item, arg, assign
