from unittest import TestCase
import pythonix.pair as p
from pythonix.prelude import *
from pythonix.shortcuts import unpack


class TestPair(TestCase):
    def setUp(self) -> None:
        self.expected_key = "Hello"
        self.expected_value = "Joe"
        return super().setUp()

    def test_new(self) -> None:
        pair = p.new(self.expected_key)(self.expected_value)
        key, value = unpack(pair)
        self.assertEqual(key, self.expected_key)
        self.assertEqual(value, self.expected_value)
        with self.assertRaises(AttributeError):
            pair.value = "Bob"

    def test_get_methods(self) -> None:
        pair = p.new(self.expected_key)(self.expected_value)
        key = p.key(pair)
        value = p.value(pair)
        self.assertEqual(key, self.expected_key)
        self.assertEqual(value, self.expected_value)

    def test_get_methods_bind(self) -> None:
        pair = p.new(self.expected_key)(self.expected_value)
        bind = Piper(pair)
        key = bind.bind(p.key).inner
        value = bind.bind(p.value).inner
        self.assertEqual(key, self.expected_key)
        self.assertEqual(value, self.expected_value)

    def test_set_methods(self) -> None:
        pair = p.new("hola")("jose")
        pair_1 = p.key(self.expected_key)(pair)
        pair_2 = p.value(self.expected_value)(pair_1)
        key = pair_2.key
        value = pair_2.value
        self.assertEqual(key, self.expected_key)
        self.assertEqual(value, self.expected_value)

    def test_set_methods_with_bind(self) -> None:
        pair = p.new("hola")("jose")
        bind = Piper(pair)
        pair_2 = (
            bind.bind(p.key(self.expected_key)).bind(
                p.value(self.expected_value)
            )
        ).inner
        key = pair_2.key
        value = pair_2.value
        self.assertEqual(key, self.expected_key)
        self.assertEqual(value, self.expected_value)

    def test_map(self) -> None:
        pair = p.new(self.expected_key)(self.expected_value)
        new_expected = "JoeBoy"
        using = lambda _: new_expected
        pair_2 = p.map_value(using)(pair)
        key = pair_2.key
        value = pair_2.value
        self.assertEqual(key, self.expected_key)
        self.assertEqual(value, new_expected)

    def test_map_with_bind(self) -> None:
        pair = p.new(self.expected_key)(self.expected_value)
        new_expected = "JoeBoy"
        using = lambda _: new_expected
        bind = Piper(pair)
        pair_2 = bind.bind(p.map_value(using)).inner
        key = pair_2.key
        value = pair_2.value
        self.assertEqual(key, self.expected_key)
        self.assertEqual(value, new_expected)
