from unittest import TestCase
from typing_extensions import reveal_type
from pythonix.internals.grammar import (
    ShiftApplyInfix,
    x,
    ShiftApplySuffix,
    ShiftApplyPrefix
)
import pythonix.res as res
from pythonix.fn import fn

class TestShiftOps(TestCase):

    def test_apply_prefix(self) -> None:
        in_arg: int = 10
        prefix = ShiftApplyPrefix(in_arg)
        message: str = ' is written as ten'
        expected: str = str(in_arg) +  message
        op = fn(int, str)(lambda x: str(x) + message)
        actual = prefix >> op
        self.assertEqual(actual, expected)
    
    def test_apply_prefix_res(self) -> None:
        in_arg = res.Ok(10, Exception)
        prefix = ShiftApplyPrefix(in_arg)
        actual = prefix >> fn(res.Res[int, Exception], res.Res[str, Exception])(
            lambda r: r.map(str)
        )  # res.map(fn(int, str)(lambda x: str(x)))
        match actual:
            case res.Res(str(inner)):
                self.assertEqual(inner, '10')
            case res.Res(Exception(e)):
                self.fail(str(e))
    
    def test_apply_prefix(self) -> None:
        ...
    
    def test_apply_infix(self) -> None:
        ...