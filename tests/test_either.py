from pythonix.prelude import *
from unittest import TestCase
from pythonix.either import (
    Either,
    Left,
    left,
    map as map_either,
    Right,
    right
)

class TestEither(TestCase):

    def test_left(self):

        left_or_right: Either[int, str] = left(str)(10)
        match left_or_right:
            case Left(int(val)):
                self.assertEqual(val, 10)
            case _:
                self.fail()

    def test_right(self):

        left_or_right: Either[int, str] = right(int)('hello')
        r = unwrap(Right)(left_or_right)
        self.assertEqual(r, 'hello')
    
    def test_map_either(self):

        left_or_right: Either[int, str] = right(int)('hello')
        new_left_or_right = map_either(Left)(fn(int, str)(lambda x: str(x)))(left_or_right)
        l, r = unpack(new_left_or_right)
        if l is not None:
            self.assertIs(l, str)
        if r is not None:
            self.assertEqual(r, 'hello')
        
