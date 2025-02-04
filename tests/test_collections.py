from unittest import TestCase
from pythonix.prelude import fn, unwrap
from pythonix.collections import Listad, Dictad, Tuplad, Set, Deq
from pythonix.traits import Colladic

from operator import add


increment = fn(int, int)(lambda x: x + 1)
is_even = fn(int, bool)(lambda n: n % 2 == 0)


class TestDeq(TestCase):

    def test_sequences(self) -> None:
        data = [1, 2, 3]
        for arr in [Listad(data), Tuplad(data), Deq(data), Set(data)]:
            arr >>= increment
            arr //= is_even
            arr **= add
            arr <<= unwrap
            self.assertEqual(arr, 6)

    def test_dictad(self) -> None:
        d = Dictad({"foo": 10, "bar": 20})
        d |= {"baz": 30}
        d //= fn(str, int, bool)(lambda k, _: k != "baz")
        d >>= increment
        d ^= str.upper
        d **= add
        d <<= unwrap
        self.assertEqual(d, 32)

    def test_colladicness(self) -> None:

        arr = Listad([1, 2, 3])
        if not isinstance(arr, Colladic):
            self.fail()

        arr = Set([1, 2, 3])
        if not isinstance(arr, Colladic):
            self.fail()

        arr = Tuplad([1, 2, 3])
        if not isinstance(arr, Colladic):
            self.fail()
