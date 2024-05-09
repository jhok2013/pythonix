from typing import Callable, TypeVar, TypeAlias

Val = TypeVar("Val")
NewVal = TypeVar("NewVal")
Fn: TypeAlias = Callable[[Val], NewVal]
FnOnce: TypeAlias = Callable[[], NewVal]
