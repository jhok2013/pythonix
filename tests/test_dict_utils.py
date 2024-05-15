from unittest import TestCase
import pythonix.dict_utils as dict_utils
import pythonix.res as res
from pythonix.pipe import Bind as B

class TestDictUtils(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    
    def test_maps(self) -> None:

        (
            B({'hello': 0, 'joe': 1})
            (dict_utils.map_values(lambda x: x + 1))
            (dict_utils.map_values(str))
            (dict_utils.map_values(str.upper))
            (dict_utils.merge({'foo': '3'}))
            (dict_utils.put('bar')('3'))
            (dict_utils.filter_values(lambda v: v != '3'))
            (dict_utils.filter_keys(lambda k: k == 'joe'))
            (dict_utils.get('joe'))
            (res.map(int))
            (res.q)
            (lambda x: x == 2)
            (self.assertTrue)
        )