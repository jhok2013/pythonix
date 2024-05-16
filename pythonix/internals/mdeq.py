"""
Functions used to create and perform operations safely on a singly typed mutable linked list.
"""
from collections import deque
from typing import Iterable, Generic, TypeVar
from pythonix.internals.res import null_and_error_safe, safe, Ok
from pythonix.internals.curry import two, three

Val = TypeVar("Val")
NewVal = TypeVar("NewVal")


class MDeq(Generic[Val], object):
    """
    `MDeq` is a singly-typed mutable linked list. `push` and `pop` operations are thread safe and run in
    `O(1)` time. Insert and get operations run in `O(n)` time. As a mutable data structure there are some
    rules to keep in mind.

    #### Rules
    - Only share one reference to a `MDeq` at a time
    - Use the `copy` function to share copies of it if necessary
    - Use the `pipes.Do` class to perform consecutive functions on it

    #### Example
    ```python
    data = mdeq.new(int)(1, 2, 3, 4, 5, 6)
    (
        pipes.Do(data)
        (md.push(7))
        (md.push(8))
        (md.push(9))
    )
    ```
    """

    inner: deque[Val] = deque()

    def __init__(self, *args: Val):
        self.inner = deque(args)


def new(*vals: Val) -> MDeq[Val]:
    """
    Creates a new instance of `MDeq` with the `vals` passed in.
    Make sure all the types are the same or you'll have weird type hints.
    """
    return MDeq(*vals)


@two
def push(element: Val, deq: MDeq[Val]) -> Ok[None]:
    """
    Pushes a new element `T` to the end of an `MDeq`.

    Note:
        This function is curried automatically. Apply function arguments
        separated by brackets.
    """
    deq.inner.append(element)
    return Ok(None)


@two
def pushleft(element: Val, deq: MDeq[Val]) -> Ok[None]:
    """
    Pushes a new element `T` to be the new first element in an `MDeq`
    """
    deq.inner.appendleft(element)
    return Ok(None)


@three
def insert(element: Val, index: int, deq: MDeq[Val]) -> Ok[None]:
    """
    Inserts a new element at the provided index. Runs on `O(n)` time.

    Provide the new element `T`
    """
    deq.inner.insert(index, element)
    return Ok(None)


def copy(deq: MDeq[Val]) -> MDeq[Val]:
    """
    Returns a shallow copy of the `MDeq` as a new object.
    """
    return new(*deq.inner.copy())


@null_and_error_safe(IndexError)
def pop(deq: MDeq[Val]) -> Val:
    """
    Removes and returns the last element in an `MDeq` if it exists.
    """
    return deq.inner.pop()


@null_and_error_safe(IndexError)
def popleft(deq: MDeq[Val]) -> Val:
    """
    Removes and returns the first element in an `MDeq` if it exists.
    """
    return deq.inner.popleft()


@null_and_error_safe(IndexError)
def first(deq: MDeq[Val]) -> Val:
    """
    Returns the first element in an `MDeq` if it exists.
    """
    return deq.inner[0]


@null_and_error_safe(IndexError)
def last(deq: MDeq[Val]) -> Val:
    """
    Returns the last element in an `MDeq` if it exists.
    """
    return deq.inner[-1]


@two
@null_and_error_safe(IndexError)
def at(index: int, deq: MDeq[Val]) -> Val:
    """
    Returns the element at the provided index in an `MDeq` if it exists.
    """
    return deq.inner[index]


@two
@safe(IndexError)
def remove(index: int, deq: MDeq[Val]) -> None:
    """
    Removes the element from the `MDeq` if it exists at the given index.
    """
    del deq.inner[index]


@two
def extend(src: Iterable[Val], tgt: MDeq[Val]) -> Ok[None]:
    """
    Combines an iterable with a provided `MDeq` with all new elements being appended.
    """

    tgt.inner.extend(src)
    return Ok(None)


@two
def extendleft(src: Iterable[Val], tgt: MDeq[Val]) -> Ok[None]:
    """
    Combines an iterable with a provided `MDeq` with all new elements going first.
    """

    tgt.inner.extendleft(src)
    return Ok(None)


def index(find: Val, start: int = 1):
    """
    Retrieves the index of the provide dvalue, if it exists.
    """

    @null_and_error_safe(ValueError)
    def inner(deq: MDeq[Val]) -> int:
        return deq.inner.index(find, start)

    return inner
