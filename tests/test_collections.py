from unittest import TestCase, skip
from pythonix.collections import *
from pythonix.res import *
from pythonix.internals.collections import DictPlus

class TestDeq(TestCase):

    def setUp(self) -> None:
        self.deq = Deq([1, 2, 3])

    def test_iteration(self):
        it = iter(self.deq)
        n = next(it)
        self.assertIsInstance(n, int)
    
    def test_right(self):
        expected = 1
        self.deq.append(expected)
        actual = self.deq.pop().unwrap()
        self.assertEqual(expected, actual)
    
    def test_left(self) -> None:
        expected = 1
        self.deq.appendleft(expected)
        actual = self.deq.popleft().unwrap()
        self.assertEqual(expected, actual)


    def test_clear(self) -> None:
        self.deq.clear()
        self.assertEqual(len(self.deq), 0)
    
    def test_copy(self) -> None:
        copied = self.deq.copy()
        self.assertEqual(copied.pop().unwrap(), self.deq.pop().unwrap())
    
    def test_count(self) -> None:
        expected = 1
        actual = self.deq.count(1)
        self.assertEqual(expected, actual)
    
    def test_extend(self) -> None:
        expected = 5
        self.deq.extend([4, 5])
        actual = self.deq.pop().unwrap()
        self.assertEqual(expected, actual)
    
    def test_extend_left(self) -> None:
        expected = 5
        self.deq.extendleft([4, 5])
        actual = self.deq.popleft().unwrap()
        self.assertEqual(expected, actual)
    
    def test_get(self) -> None:
        self.assertEqual(self.deq.get(0).unwrap(), 1)
        self.assertIsInstance(self.deq.get(10).unwrap_err(), Nil)
    
    def test_pops(self) -> None:
        self.deq.clear()
        self.assertIsInstance(self.deq.pop().unwrap_err(), Nil)
        self.assertIsInstance(self.deq.popleft().unwrap_err(), Nil)
    
    def test_index(self) -> None:
        self.assertEqual(self.deq.index(1).unwrap(), 0)
        self.assertIsInstance(self.deq.index(10).unwrap_err(), Nil)
    
    def test_map(self) -> None:
        self.assertEqual(self.deq.map(lambda x: x + 1).pop().unwrap(), 4)

    def test_where(self) -> None:
        self.assertEqual(self.deq.where(lambda x: x == 1).pop().unwrap(), 1)
    
    def test_maxlen(self) -> None:
        self.assertIsInstance(self.deq.maxlen.unwrap_err(), Nil)
    
    def test_remove(self) -> None:
        self.assertEqual(self.deq.remove(1).q.popleft().q, 2)
        self.assertIsInstance(self.deq.remove(10).unwrap_err(), ValueError)
    
    def test_rotate(self) -> None:
        self.assertEqual(self.deq.rotate().pop().q, 2)

    def test_reverse(self) -> None:
        self.assertEqual(self.deq.reverse().pop().q, 1)


class TestDictPlus(TestCase):

    def setUp(self) -> None:
        self.d = DictPlus({"hello": "world"})
        return super().setUp()
    
    def test_init(self) -> None:
        self.assertIsInstance(DictPlus({"hello": "world"}), DictPlus)
    
    def test_get_item(self) -> None:
        self.assertEqual(self.d["hello"].unwrap(), "world")
        self.assertIsInstance(self.d["world"].unwrap_err(), Nil)
    
    def test_iteration(self) -> None:
        i = iter(self.d)
        n = next(i)
        self.assertIsInstance(n, str)

    
    def test_len(self) -> None:
        self.assertEqual(len(self.d), 1)
    
    def test_get(self):
        self.assertEqual(self.d.get("hello").unwrap(), "world")
    
    def test_pop(self):
        self.assertEqual(self.d.pop("hello").unwrap(), "world")
        self.assertIsInstance(self.d.pop("world").unwrap_err(), Nil)

    def test_popitem(self):
        self.assertEqual(self.d.popitem().unwrap(), ("hello", "world"))
        self.assertIsInstance(self.d.popitem().unwrap_err(), Nil)
    
    def test_update(self):
        key, value = "hola", "mundo"
        updatable = {key: value}
        self.assertEqual(self.d.update(updatable).pop("hola").unwrap(), value)
        
        updatable = [(key, value)]
        self.assertEqual(self.d.update(updatable).pop("hola").unwrap(), value)
    
    def test_put(self):
        self.assertEqual(
            "mundo",
            self.d.put("hola", "mundo").pop("hola").unwrap()
        )
    
    def test_map(self):
        self.assertEqual(
            "mundo",
            self.d.map(lambda v: "mundo").pop("hello").unwrap()
        )
    

    def test_items(self):
        first, *_ = self.d.items()
        key, value = first
        print(first)
        print(_)
        print(key, value)
        self.assertEqual(key, "hello")
        self.assertEqual(value, "world")
    
    def test_map_keys(self):
        self.assertEqual(
            "world",
            self.d.map_keys(lambda k: "mundo").pop("mundo").unwrap()
        )
    
    def test_where(self):
        self.assertEqual(
            "world",
            self.d.where(lambda k, v: k == "hello").get("hello").q
        )
        

    def test_clear(self):
        self.d.clear()
        self.assertIsInstance(self.d.pop("hello").unwrap_err(), Nil)
    
    def test_copy(self):
        copied = self.d.copy()
        self.assertEqual(
            self.d.pop("hello").q,
            copied.pop("hello").q
        )

    def test_fromkeys(self):
        fromkeys = self.d.fromkeys(["hello"], "world")
        self.assertDictEqual(fromkeys, self.d)
        self.assertEqual(
            fromkeys.pop("hello").q,
            self.d.pop("hello").q
        )

class TestStrictDict(TestCase):

    def setUp(self):
        self.d = StrictDict.new(str, str).update({"hello": "world"})
    
    def test_setting(self):
        self.d["hello"] = "mundo"
        self.assertEqual(self.d["hello"].q, "mundo")

        with self.assertRaises(ValueError):
            self.d[0] = 10

        with self.assertRaises(ValueError):
            self.d["hello"] = 10
    
    def test_get_item(self) -> None:
        self.assertEqual(self.d["hello"].unwrap(), "world")
        self.assertIsInstance(self.d["world"].unwrap_err(), Nil)
    
    def test_len(self) -> None:
        self.assertEqual(len(self.d), 1)
    
    def test_get(self):
        self.assertEqual(self.d.get("hello").unwrap(), "world")
    
    def test_pop(self):
        self.assertEqual(self.d.pop("hello").unwrap(), "world")
        self.assertIsInstance(self.d.pop("world").unwrap_err(), Nil)

    def test_popitem(self):
        self.assertEqual(self.d.popitem().unwrap(), ("hello", "world"))
        self.assertIsInstance(self.d.popitem().unwrap_err(), Nil)
    
    def test_update(self):
        key, value = "hola", "mundo"
        updatable = {key: value}
        self.assertEqual(self.d.update(updatable).pop("hola").unwrap(), value)
        
        updatable = [(key, value)]
        self.assertEqual(self.d.update(updatable).pop("hola").unwrap(), value)
    
    def test_put(self):
        self.assertEqual(
            "mundo",
            self.d.put("hola", "mundo").pop("hola").unwrap()
        )
    
    def test_map(self):
        self.assertEqual(
            "mundo",
            self.d.map(lambda _: "mundo").pop("hello").unwrap()
        )
    

    def test_items(self):
        first, *_ = self.d.items()
        key, value = first
        print(first)
        print(_)
        print(key, value)
        self.assertEqual(key, "hello")
        self.assertEqual(value, "world")
    
    def test_map_keys(self):
        self.assertEqual(
            "world",
            self.d.map_keys(lambda k: "mundo").pop("mundo").unwrap()
        )
    
    def test_where(self):
        self.assertEqual(
            "world",
            self.d.where(lambda k, v: k == "hello").get("hello").q
        )
        

    def test_clear(self):
        self.d.clear()
        self.assertIsInstance(self.d.pop("hello").unwrap_err(), Nil)
    
    def test_copy(self):
        copied = self.d.copy()
        self.assertEqual(
            self.d.pop("hello").q,
            copied.pop("hello").q
        )

    def test_fromkeys(self):
        fromkeys = self.d.fromkeys(["hello"], "world")
        self.assertDictEqual(fromkeys, self.d)
        self.assertEqual(
            fromkeys.pop("hello").q,
            self.d.pop("hello").q
        )
