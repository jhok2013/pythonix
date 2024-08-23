from unittest import TestCase
from pythonix.prelude import *
from typing import Callable
from pythonix.internals.res import safe


class TestOk(TestCase):
    def setUp(self) -> None:
        self.test_res = res.Ok.new_pair(5, Exception)
        return super().setUp()
    
    def test_dos(self):
        self.assertEqual(self.test_res.do(lambda _: "hello").unwrap(), 5, f"{self.test_res}")
        self.assertEqual(self.test_res.do_other(lambda _: TypeError()).unwrap(), 5)

    def test_is_funcs(self) -> None:
        self.assertTrue(self.test_res.is_not_other())
        self.assertFalse(self.test_res.is_other())
        self.assertTrue(self.test_res.is_not_other_and(lambda _: True))
        self.assertFalse(self.test_res.is_not_other_and(lambda _: False))
        self.assertFalse(self.test_res.is_other_and(lambda _: True))

    def test_unwrap_funcs(self) -> None:
        self.assertEqual(self.test_res.unwrap(), 5)
        self.assertEqual(self.test_res.unwrap_or(0), 5)
        self.assertEqual(self.test_res.unwrap_or(0), 5)
        self.assertEqual(self.test_res.unwrap_or_else(lambda: 0), 5)
        with self.assertRaises(ValueError):
            self.test_res.unwrap_other()

    def test_map_funcs(self) -> None:
        self.assertEqual(self.test_res.map(lambda x: x + 1).inner, 6)
        self.assertEqual(self.test_res.map_or(lambda x: x + 1, 0).inner, 6)
        self.assertEqual(
            self.test_res.map_or_else(lambda x: x + 1, lambda: 0).inner, 6
        )
        self.assertEqual(
            self.test_res.map_other(lambda e: ValueError(str(e))).inner, 5
        )

    def test_and_funcs(self) -> None:
        self.assertEqual(self.test_res.and_then(lambda x: res.Ok.new_pair(x + 5, Exception)).inner, 10)
        self.assertEqual(self.test_res.and_(res.Ok.new_pair(10, Exception)).inner, 10)

    def test_or_funcs(self) -> None:
        self.assertEqual(self.test_res.or_else(lambda e: 10).inner, 5)
        self.assertEqual(self.test_res.or_(res.Err.new_pair(ValueError(), int)).inner, 5)


class TestErr(TestCase):
    # TODO: Finish updating tests
    def setUp(self) -> None:
        self.test_res = res.Err.new_pair(Exception(), int)

    def test_is_funcs(self) -> None:
        self.assertTrue(self.test_res.is_other())
        self.assertFalse(self.test_res.is_not_other())

    def test_unwrap_funcs(self) -> None:
        with self.assertRaises(Exception):
            self.test_res.unwrap()
        self.assertEqual(self.test_res.unwrap_or(0), 0)
        self.assertEqual(self.test_res.unwrap_or_else(lambda e: 0), 0)
        self.assertIsInstance(self.test_res.unwrap_other(), Exception)

    def test_map_funcs(self) -> None:
        self.assertIsInstance(self.test_res.map(lambda x: x + 1).unwrap_other(), Exception)
        self.assertEqual(self.test_res.map_or(lambda x: x + 1, 0).inner, 0)
        self.assertEqual(
            self.test_res.map_or_else(lambda x: x + 1, lambda: 0).inner, 0
        )

    def test_and_funcs(self) -> None:
        self.assertIsInstance(
            self.test_res.and_then(lambda x: res.Ok.new_pair(x + 5, Exception)).inner,
            Exception,
        )
        self.assertIsInstance(
            self.test_res.and_(res.Ok.new_pair(10, Exception)).inner, Exception
        )

    def test_or_funcs(self) -> None:
        self.assertIsInstance(
            self.test_res.or_(res.Err.new_pair(ValueError(), int)).inner, ValueError
        )
        self.assertIsInstance(
            self.test_res.or_else(lambda e: Err.new_pair(ValueError(str(e)), int)).inner,
            ValueError
        )
    
    def test_dos(self):
        self.assertIsInstance(self.test_res.do(lambda _: "hello").unwrap_other(), Exception)
        self.assertIsInstance(self.test_res.do_other(lambda _: TypeError()).unwrap_other(), Exception)


class TestDecorators(TestCase):
    def test_safe(self) -> None:
        op: Callable[[str], str] = lambda x: x
        proto_op = safe(TypeError, AttributeError)(op)
        self.assertEqual("hello", proto_op("hello").unwrap())

    def test_safe_fail(self) -> None:
        @safe(TypeError)
        def will_throw_type_error(_):
            raise TypeError("Failed successfully")
        
        self.assertIsInstance(will_throw_type_error(None).unwrap_err(), TypeError)

class TestOpt(TestCase):

    def test_some(self):
        self.assertIsInstance(res.Ok(None).some(), res.Err)
        self.assertIsInstance(res.Ok(10).some(), res.Ok)
    