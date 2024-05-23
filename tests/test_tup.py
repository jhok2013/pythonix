from pythonix.prelude import *
from unittest import TestCase


class TestTup(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_new(self) -> None:
        expected = ("foo", "bar")
        actual = tup.new("foo", "bar")
        self.assertTupleEqual(expected, actual)

    def test_push(self) -> None:
        bind = Piper(tup.new("Hello"))
        expected = (5, "Hello", 10.0, True)
        seq = (
            bind.bind(tup.push_left(5))
            .bind(tup.push_right(10.0))
            .bind(tup.push()(True))
            .inner
        )
        self.assertTupleEqual(expected, seq)

    def test_extend(self) -> None:
        bind = Piper(tup.new("Hello"))
        expected = (5, "Hello", 10.0, True)
        seq = (
            bind.bind(tup.extend_left(tup.new(5)))
            .bind(tup.extend_right(tup.new(10.0)))
            .bind(tup.extend()(tup.new(True)))
            .inner
        )
        self.assertTupleEqual(expected, seq)

    def test_getters(self) -> None:
        seq = tup.new("Hello", "there", "Joe")
        bind = Piper(seq)
        bind.bind(tup.first).bind(lambda x: x.inner == "Hello").bind(self.assertTrue)
        bind.bind(tup.last).bind(lambda x: x.inner == "Joe").bind(self.assertTrue)
        bind.bind(tup.get(1)).bind(lambda x: x.inner == "there").bind(self.assertTrue)

    def test_insertions(self) -> None:
        (
            Piper(tup.new("Hello"))
            .bind(tup.insert(1)("Joe"))
            .do(lambda seq: self.assertTupleEqual(seq, ("Hello", "Joe")))
            .bind(tup.insert(0)("Well"))
            .bind(tup.remove(0))
            .bind(q)
            .bind(tup.index("Joe"))
            .bind(q)
            .bind(lambda index: index == 1)
            .bind(self.assertTrue)
        )

    def test_counts(self) -> None:
        (
            Piper(tup.new("Hello", "Joe"))
            .do(
                lambda seq: Piper(seq)
                .bind(tup.count_occurrences("Hello"))
                .bind(lambda count: count == 1)
                .bind(self.assertTrue)
            )
            .do(
                lambda seq: Piper(seq)
                .bind(tup.count_occurrences("Pickles"))
                .bind(lambda count: count == 0)
                .bind(self.assertTrue)
            )
        )
