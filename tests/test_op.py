from pythonix.prelude import *
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
            Piper(self.test_class)
            .do(lambda point: Piper(point).bind(op.attr("x")).bind(q))
            .do(lambda point: Piper(point).bind(op.attr("y")).bind(q))
            .do(lambda point: Piper(point).bind(op.attr("z")).bind(qe))
        )

    def test_item(self) -> None:
        (
            Piper(self.test_class)
            .bind(lambda point: point._asdict())
            .do(lambda mapping: Piper(mapping).bind(op.item("x")).bind(q))
            .do(lambda mapping: Piper(mapping).bind(op.item("y")).bind(q))
            .do(lambda mapping: Piper(mapping).bind(op.item("z")).bind(qe))
        )

    def test_mapx(self) -> None:
        (
            Piper(tuple(self.test_class._asdict().values()))
            .bind(op.map_over(lambda x: x + 1))
            .bind(op.map_over(lambda x: x + 2))
            .bind(op.map_over(str))
            .bind(tuple)
            .bind(lambda data: self.assertTupleEqual(data, ("8", "7")))
        )

    def test_filterx(self) -> None:
        (
            Piper(tuple(self.test_class._asdict().values()))
            .bind(op.where(lambda x: x % 2 == 0))
            .bind(tuple)
            .bind(op.item(0))
            .bind(q)
            .bind(lambda res: self.assertEqual(4, res))
        )

    def test_reducex(self) -> None:
        (
            Piper(tuple(self.test_class._asdict().values()))
            .bind(op.fold(add))
            .bind(int)
            .bind(lambda x: self.assertEqual(x, 9))
        )
