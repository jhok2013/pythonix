from unittest import TestCase
from typing import Callable, cast, Iterable
from pythonix.prelude import *
from pythonix.res import ExpectError, UnwrapError
from pythonix.collections import Listad
from pythonix.internals.traits import Colladic


class TestOk(TestCase):

    def test_map(self) -> None:
        add_10: Callable[[int], int] = lambda x: x + 10
        replace: Callable[[], int] = lambda: 10
        and_then: Callable[[int], Res[int, Nil]] = lambda x: Res.Some(x + 10)
        and_replace: Callable[[], Res[int, Nil]] = lambda: Res.Some(10)
        ok = Res.Some(10)
        ok >>= add_10
        ok >>= replace
        ok >>= and_then
        ok >>= and_replace
        ok <<= unwrap
        self.assertEqual(10, ok)

    def test_map_alt(self) -> None:
        err = Res[int, ValueError].Err(ValueError("foo"))
        err ^= lambda e: ValueError(str(e))
        err ^= convert_err(ValueError)
        err ^= lambda: Exception("foo")
        err ^= lambda: Res[int, ValueError].Err(ValueError("foo"))
        err ^= lambda e: Res[int, Exception].Err(Exception(str(e)))
        err <<= unwrap_alt
        self.assertIsInstance(err, Exception)

    def test_terminators(self):
        ok = Res.Some(10)
        err = Res[int, Nil].Nil()
        self.assertTrue(ok.ok_and(lambda t: t == 10))
        self.assertFalse(ok.ok_and(lambda t: t > 10))
        self.assertTrue(ok << ok_and(lambda t: t == 10))
        self.assertFalse(ok << ok_and(lambda t: cast(int, t) > 10))
        self.assertTrue(bool(ok))
        self.assertFalse(bool(err))
        self.assertTrue(err.err_and(lambda e: isinstance(e, Nil)))
        self.assertFalse(err.err_and(lambda e: e is ValueError))
        self.assertTrue(err << err_and(lambda e: isinstance(e, Nil)))
        self.assertFalse(err << err_and(lambda e: e is ValueError))
        self.assertIsInstance(ok.expect("Oops"), int)
        self.assertIsInstance(err.expect_err("Oops"), Nil)
        self.assertIsInstance(ok << expect("Oops"), int)
        self.assertIsInstance(err << expect_err("Oops"), Nil)
        with self.assertRaises(ExpectError):
            err.expect("Oops")
        with self.assertRaises(ExpectError):
            _ = err << expect("Oops")
        with self.assertRaises(ExpectError):
            ok.expect_err("oops")
        with self.assertRaises(ExpectError):
            _ = ok << expect_err("oops")
        self.assertIsInstance(ok.unwrap(), int)
        self.assertIsInstance(ok << unwrap, int)
        with self.assertRaises(Nil):
            err.unwrap()
        with self.assertRaises(Nil):
            _ = err << unwrap
        self.assertIsInstance(err.unwrap_alt(), Nil)
        self.assertIsInstance(err << unwrap_alt, Nil)
        with self.assertRaises(UnwrapError):
            ok.unwrap_alt()
        with self.assertRaises(UnwrapError):
            _ = ok << unwrap_alt
        val, nil = ok.unpack()
        if val is not None:
            self.assertTrue(True)
        if nil is not None:
            self.fail()
        val, nil = err.unpack()
        if nil is not None:
            self.assertTrue(True)
        if val is not None:
            self.fail()

    def test_do(self) -> None:
        ok = Res.Some(10)
        err = Res[int, Nil].Nil()
        self.assertTrue(ok.do(lambda t: t + 20).unwrap() == 10)
        self.assertIsInstance(err.do_err(lambda e: ValueError(e)).unwrap_alt(), Nil)
        ok >>= do(lambda t: cast(int, t) + 10)
        ok <<= unwrap
        err ^= do(lambda e: ValueError(e))
        err <<= unwrap_alt
        self.assertEqual(10, ok)
        self.assertIsInstance(err, Nil)

    def test_extras(self) -> None:
        ok = Res.Some(10)
        err = Res[int, Nil].Nil()

        if not ok:
            self.fail()

        if err:
            self.fail()

        match ok:
            case Res(t, True):
                self.assertEquals(10, t)
            case Res(e):
                self.assertIsInstance(e, Nil)
            case _:
                self.fail()

        match err:
            case Res(t, True):
                self.assertEquals(10, t)
            case Res(e):
                self.assertIsInstance(e, Nil)
            case _:
                self.fail()

        self.assertIn(10, ok)
        self.assertNotIn(10, err)

        ok = Res.Some([1, 2, 3])
        err = Res[list[int], Nil].Nil()

        for i in ok:
            self.assertIsInstance(i, int)

        for i in err:
            self.fail()

        ok = Res.Some((1, 2, 3))
        err = Res[list[int], Nil].Nil()

        for i in ok:
            self.assertIsInstance(i, int)

        for i in err:
            self.fail()

        ok = Res.Some({1, 2, 3})
        err = Res[list[int], Nil].Nil()

        for i in ok:
            self.assertIsInstance(i, int)

        for i in err:
            self.fail()
        
        ok = Res.Some(Listad([1, 2, 3]))
        for l in ok:
            self.assertIsInstance(l, Listad)
        
        self.assertTrue(ok == ok)
        self.assertTrue(ok != Res.Some(10))
        self.assertTrue(err == err)
        self.assertTrue(err != Res.Err(ValueError("oops")))
        self.assertFalse(ok == err)

