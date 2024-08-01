from pythonix.prelude import *
from unittest import TestCase

class TestJSON(TestCase):

    def test_encode(self):

        encoded = q(jsn.encode(**jsn.pretty())({"hello": "world"}))
        self.assertIsInstance(encoded, str)
    
    def test_decode(self):

        decoded: dict[str, str] = unwrap(jsn.decode(dict)('{"hello": "world"}'))
        value = unwrap(dict_utils.get('hello')(decoded))
        self.assertEqual(value, 'world')

