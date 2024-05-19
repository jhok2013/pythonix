from pythonix.prelude import *
from pythonix.prelude import Bind as B
from unittest import TestCase, skip


class TestProve(TestCase):
    def setUp(self) -> None:
        self.start = B(10)
        return super().setUp()

    def test_that(self) -> None:
        (self.start(prove.that(lambda x: x == 10))(q))

    def test_equal(self) -> None:
        (self.start(prove.equals(10))(q))

    def test_is_true(self) -> None:
        (self.start(lambda x: x == 10)(prove.is_true)(q))

    def test_is(self) -> None:
        (self.start(prove.is_an(int))(q))

    def test_contains(self) -> None:
        (self.start(lambda x: [x] * 5)(prove.contains(10))(q))
