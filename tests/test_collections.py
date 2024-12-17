from unittest import TestCase
from pythonix.prelude import *
from pythonix.collections import Listad, Dictad, Tuplad, Set, Deq, LazyPlan

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
    

class TestLazyAd(TestCase):

    def test_lazy_ad(self) -> None:
        plan = LazyPlan[int, int]()
        new = (
            plan
            .map(fn(int, int)(lambda x: x + 10))
            .map(str)
            .map(str.split)
            .map(lambda chars: '/'.join(chars))
            .where(lambda w: len(w.split()) > 10)
            .build([1, 2, 3, 4, 5])
        )

        plan >>= fn(int, int)(lambda x: x + 10)
        plan >>= fn(int, str)(lambda x: str(x))
        plan >>= str.split
        plan >>= fn(list[str], str)(lambda l: '/'.join(l))
        plan //= fn(str, bool)(lambda w: len(w.split()) > 0)
        lazy = plan.build([1, 2, 3])