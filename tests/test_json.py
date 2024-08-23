from pythonix.prelude import *
from unittest import TestCase

class TestJSON(TestCase):

    def test_encode(self):

        encoded = jsn.encode(**jsn.pretty())({"hello": "world"}).q
        self.assertIsInstance(encoded, str)
    
    def test_decode(self):

        res = jsn.decode(dict)('{"hello": "world"}').q
        val = res.get("hello")
        self.assertEqual(val, "world") 

