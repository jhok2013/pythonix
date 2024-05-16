from unittest import TestCase
from pythonix.prelude import *
from pythonix.internals.res import safe, safe


class TestOk(TestCase):
    def setUp(self) -> None:
        self.test_res = res.ok(Exception)(5)
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
        self.assertEqual(
            res.map_or_else(lambda x: x + 1)(lambda: 0)(self.test_res).inner, 6
        )
        self.assertEqual(
            res.map_catch(lambda x: x + 1)(Exception)(self.test_res).inner, 6
        )
        self.assertEqual(
            res.map_err(lambda e: ValueError(str(e)))(self.test_res).inner, 5
        )

    def test_and_funcs(self) -> None:
        self.assertEqual(
            res.and_then(lambda x: res.ok(Exception)(x + 5))(self.test_res).inner, 10
        )
        self.assertEqual(
            res.and_then_catch(lambda x: x + 5)(Exception)(self.test_res).inner, 10
        )
        self.assertEqual(res.and_res(res.ok(Exception)(10))(self.test_res).inner, 10)

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
        with self.assertRaises(Exception):
            res.unwrap(self.test_res)
        self.assertEqual(res.unwrap_or(0)(self.test_res), 0)
        self.assertEqual(res.unwrap_or_else(lambda: 0)(self.test_res), 0)
        self.assertIsInstance(res.unwrap_err(self.test_res), Exception)

    def test_map_funcs(self) -> None:
        self.assertIsInstance(res.map(lambda x: x + 1)(self.test_res).inner, Exception)
        self.assertEqual(res.map_or(lambda x: x + 1)(0)(self.test_res).inner, 0)
        self.assertEqual(
            res.map_or_else(lambda x: x + 1)(lambda: 0)(self.test_res).inner, 0
        )
        self.assertIsInstance(
            res.map_catch(lambda x: x + 1)(Exception)(self.test_res).inner, Exception
        )

    def test_and_funcs(self) -> None:
        self.assertIsInstance(
            res.and_then(lambda x: res.ok(x + 5)(Exception))(self.test_res).inner,
            Exception,
        )
        self.assertIsInstance(
            res.and_then_catch(lambda x: x + 5)(Exception)(self.test_res).inner,
            Exception,
        )
        self.assertIsInstance(
            res.and_res(res.ok(10)(Exception))(self.test_res).inner, Exception
        )

    def test_or_funcs(self) -> None:
        self.assertIsInstance(
            res.or_res(res.err(int)(ValueError()))(self.test_res).inner, ValueError
        )
        self.assertIsInstance(
            res.or_else(lambda e: res.err(int)(ValueError(str(e))))(
                self.test_res
            ).inner,
            ValueError,
        )


class TestDecorators(TestCase):

    def test_safe(self) -> None:
        op: Fn[str, str] = lambda x: x
        proto_op = safe(TypeError, AttributeError)(op)
        (
            pipe.Bind('hello')
            (proto_op)            
            (res.q)
            (lambda s: self.assertEqual(s, 'hello'))
        )


    def test_safe_fail(self) -> None:

        @safe(TypeError)
        def will_throw_type_error(_):
            raise TypeError('Failed successfully')
        
        (
            pipe.Bind(None)
            (will_throw_type_error)
            (res.qe)
            (self.assertIsNotNone)
        )
        

