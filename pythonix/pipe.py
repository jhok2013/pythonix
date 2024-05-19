"""Essential classes for chaining function calls over values in a concise way

The module contains classes for repeatedly binding, piping, or doing things to values
sequentially and concisely.

For when you want to chain function calls that change the internal state, use Bind.
For when you want to test side effects without changing the internal state, use Do.

Examples:

    Normal Flow:
        ```python
        import logging

        foo_list: list[int] = [0, 1, 3, 4]
        first: int = foo_list[0] 
        
        assert first == 0
            
        ```
    
    With Bind and Do:
        ```python
        import logging
        from pythonix.prelude import *

        (
            Bind([0, 1, 3, 4])
            (lambda d: d[0])
            (prove.equals(10))
            (res.unwrap)
        )
        ```
"""

from pythonix.internals.pipe import Bind, Do
