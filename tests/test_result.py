from unittest import TestCase
from pythonix.prelude import *

class TestResult(TestCase):

    def setUp(self) -> None:
        self.test_res = res.ok(5)(Exception)
        return super().setUp()

    def test_is_funcs(self) -> None:
        self.assertTrue(res.is_ok(self.test_res))
        self.assertFalse(res.is_err(self.test_res))
        self.assertTrue(res.is_ok_and(lambda _: True)(self.test_res))
        self.assertFalse(res.is_ok_and(lambda _: False)(self.test_res))
        self.assertFalse(res.is_err_and(lambda _: True)(self.test_res))
    
    def test_unwrap_funcs(self) -> None:
        self.assertEqual(res.unwrap(self.test_res), 5)
        self.assertEqual(res.unwrap_or(0)(self.test_res), 5)
        self.assertEqual(res.unwrap_or_else(lambda: 0)(self.test_res), 5)
        with self.assertRaises(ValueError):
            res.unwrap_err(self.test_res)
    
    def test_map_funcs(self) -> None:
        self.assertEqual(res.map(lambda x: x + 1)(self.test_res).inner, 6)
        self.assertEqual(res.map_or(lambda x: x + 1)(0)(self.test_res).inner, 6)
        self.assertEqual(res.map_or_else(lambda x: x + 1)(lambda: 0)(self.test_res).inner, 6)
        self.assertEqual(res.map_catch(lambda x: x + 1)(Exception)(self.test_res).inner, 6)
    
    def test_and_funcs(self) -> None:
        self.assertEqual(res.and_then(lambda x: res.ok(x + 5)(Exception))(self.test_res).inner, 10)
        self.assertEqual(res.and_then_catch(lambda x: x + 5)(Exception)(self.test_res).inner, 10)
        self.assertEqual(res.and_res(res.ok(10)(Exception))(self.test_res).inner, 10)

    def test_or_funcs(self) -> None:
        self.assertEqual(res.or_else(lambda e: 10)(self.test_res).inner, 5)
        self.assertEqual(res.or_res(res.err(int)(ValueError))(self.test_res).inner, 5)


class TestErr(TestCase):

    def setUp(self) -> None:
        self.test_res = res.err(int)(Exception())
        
    def test_is_funcs(self) -> None:
        self.assertTrue(res.is_err(self.test_res))
        self.assertFalse(res.is_ok(self.test_res))

    def test_unwrap_funcs(self) -> None:
        ...

    def test_map_funcs(self) -> None:
        ...

    def test_and_funcs(self) -> None:
        ...

    def test_or_funcs(self) -> None:
        ...


class TestDo(TestCase):
   
    def setUp(self) -> None:
        self.bind = pipe.Bind(5)
        self.do = pipe.Do("hello world")
        return super().setUp()
    
    def test_bind(self) -> None:
        (
            self.bind
            (lambda x: x + 1)
            (lambda x: x * 2)
            (float)
            (str)
            (lambda _: True)
            (self.assertTrue)
        )

    def test_do(self) -> None:
        (
            self.do
            (print)
            (print)
            (print)
        )