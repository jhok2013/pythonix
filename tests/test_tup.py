import pythonix.tup as tup
from logging import info
from pythonix.pipe import Bind
import pythonix.res as res
from pythonix.res import q
from unittest import TestCase

class TestTup(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    

    def test_new(self) -> None:
        expected = ('foo', 'bar')
        actual = tup.new('foo', 'bar')
        self.assertTupleEqual(expected, actual)

    def test_push(self) -> None:
        bind = Bind(tup.new('Hello'))
        expected = (5, 'Hello', 10.0, True)
        seq = (
            bind
            (tup.push_left(5))
            (tup.push_right(10.0))
            (tup.push()(True))
            .inner
        )
        self.assertTupleEqual(expected, seq)
    
    def test_extend(self) -> None:
        bind = Bind(tup.new('Hello'))
        expected = (5, 'Hello', 10.0, True)
        seq = (
            bind
            (tup.extend_left(tup.new(5)))
            (tup.extend_right(tup.new(10.0)))
            (tup.extend()(tup.new(True)))
            .inner
        )
        self.assertTupleEqual(expected, seq)

    def test_getters(self) -> None:
        seq = tup.new('Hello', 'there', 'Joe')
        bind = Bind(seq)
        bind(tup.first)(lambda x: x.inner == 'Hello')(self.assertTrue)
        bind(tup.last)(lambda x: x.inner == 'Joe')(self.assertTrue)
        bind(tup.get(1))(lambda x: x.inner == 'there')(self.assertTrue)

    def test_insertions(self) -> None:
        (
            Bind(tup.new('Hello'))
            (tup.insert(1)('Joe'))
            .do
            (lambda seq: self.assertTupleEqual(seq, ('Hello', 'Joe')))
            .bind
            (tup.insert(0)('Well'))
            (tup.remove(0))(q)
            (tup.index('Joe'))(q)
            (lambda index: index == 1)
            (self.assertTrue)
        )
    
    def test_counts(self) -> None:
        (
            Bind(tup.new('Hello', 'Joe'))
            .do
            (
                lambda seq:
                Bind(seq)
                (tup.count_occurrences('Hello'))
                (lambda count: count == 1)
                (self.assertTrue)
            )(
                lambda seq:
                Bind(seq)
                (tup.count_occurrences('Pickles'))
                (lambda count: count == 0)
                (self.assertTrue)
            )
        )
