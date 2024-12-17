from pythonix.prelude import *
from pythonix import prove
from unittest import TestCase


class TestProve(TestCase):
    def setUp(self) -> None:
        self.start = Piper(10)
        return super().setUp()

    def test_that(self) -> None:
        self.start >>= prove.that(lambda x: x == 10)
        self.start <<= unwrap

    def test_equal(self) -> None:
        self.start >>= prove.equals(10)
        self.start <<= unwrap

    def test_is_true(self) -> None:
        self.start >>= lambda x: x + 10
        self.start >>= prove.is_true
        self.start <<= unwrap

    def test_is(self) -> None:
        self.start >>= prove.is_an(int)
        self.start <<= unwrap

    def test_contains(self) -> None:
        self.start >>= lambda x: [x] * 5
        self.start >>= prove.contains(10)
        self.start <<= unwrap
