from pythonix.prelude import *
from unittest import TestCase


class TestProve(TestCase):
    def setUp(self) -> None:
        self.start = Piper(10)
        return super().setUp()

    def test_that(self) -> None:
        (
            self.start
            >> prove.that(lambda x: x == 10)
            > q
        )

    def test_equal(self) -> None:
        (self.start.bind(prove.equals(10)).bind(q))

    def test_is_true(self) -> None:
        (self.start.bind(lambda x: x == 10).bind(prove.is_true).bind(q))

    def test_is(self) -> None:
        (self.start.bind(prove.is_an(int)).bind(q))

    def test_contains(self) -> None:
        (self.start.bind(lambda x: [x] * 5).bind(prove.contains(10)).bind(q))
