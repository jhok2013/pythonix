"""
Module that provides object types for performing consecutive operations on a value
in a pipeline. This emulates `|>` operator in other programming languages.
#### Example
```python
from pythonix import pipes

# Perform a series of transformations cleanly with `Bind`
bind: Bind[int] = Bind(5)
(
    bind
    (lambda x: x * 2)   # (y: int) Perform an arbitrary function
    (lambda x: x == 10) # (y: bool) Perform a function that changes type
    (str)               # (y: str) Convert to a new type
    (print)             # (y: None) Make a side effect
)
assert bind.inner is None

# If you want to perform operations without changing the content of the value, use `Do` instead
do: Do[str] = Do("hello world")
(
    do
    (print)
    (type)
    (lambda s: print(f'{s}, the sun says hello!'))
)
assert do.inner = "hello world"
```
"""

from pythonix.internals.pipe import Bind, Do
