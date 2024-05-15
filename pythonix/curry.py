'''
Decorator functions used to curry functions and provide new type annotations.
The number of arguments in the function must match the decorator.
#### Example
```python
# The two function definitions are identical
@two
def add(x: int, y: int) -> int:
    return x + y

def add(x: int) -> Fn[int, int]:
    def inner(y: int) -> int:
        return x + y
    return inner
```
'''
from pythonix.internals.curry import two, three, four, five, six, seven, eight, nine
