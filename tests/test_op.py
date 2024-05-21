from pythonix.prelude import op
from pythonix.pipe import Bind as B
from pythonix.res import q, qe
from operator import add
from typing import NamedTuple
from unittest import TestCase


class Point(NamedTuple):
    x: int
    y: int


class TestOp(TestCase):
    def setUp(self) -> None:
        self.test_class = Point(5, 4)
        return super().setUp()

    def test_attr(self) -> None:
        (
            B(self.test_class).do(lambda point: B(point)(op.attr("x"))(q))(
                lambda point: B(point)(op.attr("y"))(q)
            )(lambda point: B(point)(op.attr("z"))(qe))
        )

    def test_item(self) -> None:
        (
            B(self.test_class)(lambda point: point._asdict()).do(
                lambda mapping: B(mapping)(op.item("x"))(q)
            )(lambda mapping: B(mapping)(op.item("y"))(q))(
                lambda mapping: B(mapping)(op.item("z"))(qe)
            )
        )

    def test_mapx(self) -> None:
        (
            B(tuple(self.test_class._asdict().values()))(op.map_over(lambda x: x + 1))(
                op.map_over(lambda x: x + 2)
            )(op.map_over(str))(tuple)(lambda data: self.assertTupleEqual(data, ("8", "7")))
        )

    def test_filterx(self) -> None:
        (
            B(tuple(self.test_class._asdict().values()))(
                op.where(lambda x: x % 2 == 0)
            )(tuple)(op.item(0))(q)(lambda res: self.assertEqual(4, res))
        )

    def test_reducex(self) -> None:
        (
            B(tuple(self.test_class._asdict().values()))(op.fold(add))(int)(
                lambda x: self.assertEqual(x, 9)
            )
        )
