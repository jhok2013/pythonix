from unittest import TestCase
from pythonix.prelude import *
from typing import Callable
from pythonix.internals.res import safe


class TestOk(TestCase):

    test_res: Res[int, Exception]

    def setUp(self) -> None:
        self.test_res = Res[int, Exception].Ok(5)
        return super().setUp()
    
    def test_dos(self):
        self.assertEqual(self.test_res.do(lambda _: "hello").unwrap(), 5, f"{self.test_res}")
        self.assertEqual(self.test_res.do_err(lambda _: TypeError()).unwrap(), 5)

    def test_is_funcs(self) -> None:
        self.assertTrue(self.test_res.is_ok)
        self.assertFalse(self.test_res.is_err)
        self.assertTrue(self.test_res.is_ok_and(lambda _: True))
        self.assertFalse(self.test_res.is_ok_and(lambda _: False))
        self.assertFalse(self.test_res.is_err_and(lambda _: True))

    def test_unwrap_funcs(self) -> None:
        self.assertEqual(self.test_res.unwrap(), 5)
        self.assertEqual(self.test_res.unwrap_or(0), 5)
        self.assertEqual(self.test_res.unwrap_or(0), 5)
        self.assertEqual(self.test_res.unwrap_or_else(lambda: 0), 5)
        with self.assertRaises(res.UnwrapError):
            self.test_res.unwrap_err()

    def test_map_funcs(self) -> None:
        self.assertEqual(self.test_res.map(lambda x: x + 1).inner, 6)
        self.assertEqual(self.test_res.map_or(lambda x: x + 1, 0).inner, 6)
        self.assertEqual(
            self.test_res.map_or_else(lambda x: x + 1, lambda e: 0).inner, 6
        )
        self.assertEqual(
            self.test_res.map_err(lambda e: ValueError(str(e))).inner, 5
        )

    def test_and_funcs(self) -> None:
        self.assertEqual(self.test_res.and_then(lambda x: Res[int, Exception].Ok(x + 5)).inner, 10)
        self.assertEqual(self.test_res.and_(Res[int, Exception].Ok(10)).inner, 10)

    def test_or_funcs(self) -> None:
        self.assertEqual(self.test_res.or_else(lambda e: Res[int, Exception].Ok(10)).inner, 5)
        self.assertEqual(self.test_res.or_(Res.Err(ValueError())).inner, 5)


class TestErr(TestCase):

    test_res: Res[int, Exception]

    def setUp(self) -> None:
        self.test_res = Res[int, Exception].Err(Exception())

    def test_is_funcs(self) -> None:
        self.assertTrue(self.test_res.is_err)
        self.assertFalse(self.test_res.is_ok)

    def test_unwrap_funcs(self) -> None:
        with self.assertRaises(Exception):
            self.test_res.unwrap()
        self.assertEqual(self.test_res.unwrap_or(0), 0)
        self.assertEqual(self.test_res.unwrap_or_else(lambda: 0), 0)
        self.assertIsInstance(self.test_res.unwrap_err(), Exception)
        e = self.test_res.unwrap_err()

    def test_map_funcs(self) -> None:
        self.assertIsInstance(self.test_res.map(lambda x: x + 1).unwrap_err(), Exception)
        self.assertEqual(self.test_res.map_or(lambda x: x + 1, 0).inner, 0)
        self.assertEqual(
            self.test_res.map_or_else(lambda x: x + 1, lambda e: 0).inner, 0
        )

    def test_and_funcs(self) -> None:
        self.assertIsInstance(
            self.test_res.and_then(lambda x: Res[int, Exception].Ok(x + 5)).inner,
            Exception,
        )
        self.assertIsInstance(
            self.test_res.and_(Res[int, Exception].Ok(10)).inner, Exception
        )

    def test_or_funcs(self) -> None:
        self.assertIsInstance(
            self.test_res.or_(Res[int, Exception].Err(ValueError())).inner, ValueError
        )
        self.assertIsInstance(
            self.test_res.or_else(lambda e: Res[int, ValueError].Err(ValueError(str(e)))).inner,
            ValueError
        )
    
    def test_dos(self):
        self.assertIsInstance(self.test_res.do(lambda _: "hello").unwrap_err(), Exception)
        self.assertIsInstance(self.test_res.do_err(lambda _: TypeError()).unwrap_err(), Exception)


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
        self.assertEqual(Res.Some(10).unwrap(), 10)
        self.assertIsInstance(Res.Some(None).unwrap_err(), Nil)
    