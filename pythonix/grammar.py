'''
Decorator classes that used to simulate prefix, infix, and suffix applications. Includes
the special `p` object to pipe values from left to right into functions.
#### Example
```python
# Prefix Example
@PipePrefix
def absorb_right[T](val: T) -> T:
    return val

assert absorb_right | 10 == 10
assert absorb_right(10) == 10

# Infix Example
@PipeInfix
def fold[T, U, V](func: Callable[[T, U], V], iterable: Iterable[T | U]) -> V:
    return reduce(func, iterable)

assert operator.add | fold | [1, 2, 3, 4] == 10
assert fold(operator.add)([1, 2, 3, 4]) == 10

# Suffix Example
@PipeSuffix
def inner[T](val: HasInner[T]) -> T:
    return val.inner

assert Ok(5) | inner == 5
assert inner(Ok(5)) == 5

# |p| Example
add: Fn[Tuple[int, int], int] = lambda elems: sum(elems)

assert (5, 5) |p| sum == 10
assert p((5, 5))(sum) == 10
```
'''
from pythonix.internals.grammar import PipeApply, PipeSuffix, PipeInfix, PipePrefix, Pipe