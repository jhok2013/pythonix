from pythonix.prelude import *
from unittest import TestCase
from pythonix.either import (
    Either,
    Left,
    Right,
)

class TestEither(TestCase):

    def test_left(self):

        left_or_right = Left.new_pair(10, str)
        match left_or_right:
            case Left(int(val)):
                self.assertEqual(val, 10)
            case _:
                self.fail()
