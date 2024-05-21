from unittest import TestCase
import pythonix.dict_utils as du
import pythonix.res as res
from pythonix.prelude import *


class TestDictUtils(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_maps(self) -> None:
        x = (
            Piper({"hello": 0, "joe": 1})
            >> du.map_values(fn(int, int)(lambda x: x + 1))
            >> du.map_keys(fn(str, str)(str.upper))
            >> du.merge({'FOO': 3})
            >> du.put('BAR')(3)
            >> du.filter_values(fn(int, bool)(lambda v: v != 3))
            >> du.filter_keys(fn(str, bool)(lambda k: k == 'JOE'))
            >> du.get('JOE')
            >> res.unwrap
            >> fn(int, bool)(lambda x: x == 2)
            > self.assertTrue
        )
