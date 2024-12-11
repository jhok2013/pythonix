from pythonix.prelude import *
from pythonix.utils import (
    arg,
    attr,
    item,
)
from pythonix.grammar import Piper, PipeFn, p
from unittest import TestCase

class TestOp(TestCase):

    def test_item(self) -> None:
        it = [1, 2, 3]
        val = item(0)(it) 
        self.assertIn(1, val)
        val = item(4)(it)
        self.assertFalse(bool(val))
        it = [None]
        val = item(0)(it)
        self.assertFalse(bool(val))
    
    def test_attr(self) -> None:

        class Foo:
            def __init__(self, x: int) -> None:
                self.x = x
        
        foo = Foo(10)

        val = attr(int)('x')(foo)
        self.assertIn(10, val)


        nil = attr(int)('y')(foo)
        nil <<= unwrap_alt
        self.assertIsInstance(nil, Nil)

    def test_arg(self) -> None:
        add_ten = lambda x: x + 10

        val = arg(10)(add_ten)
        self.assertEqual(20, val)
    
    def test_piper(self) -> None:
        val = Piper(10)
        val >>= lambda x: x + 10
        val >>= lambda x: x - 10
        val >>= str
        val >>= str.split
        val >>= item(0)
        val >>= unwrap
        val <<= unwrap
        self.assertEqual('10', val) 


    def test_fn_pipe(self) -> None:
        @PipeFn
        def add_10(x: int) -> int:
            return x + 10
        val: int = 10
        val |= add_10
        val |= add_10
        self.assertEqual(30, val)
