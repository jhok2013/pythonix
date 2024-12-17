from unittest import TestCase
from pythonix.crumb import *
from pythonix.prelude import *

class TestTrail(TestCase):

    def test_crumb(self) -> None:

        @crumb(Info("Starting add_10"))
        def add_10(x: int) -> int:
            return x + 10
        
        def add_20(x: int) -> Crumb[int]:
            try:
                val = Crumb[int](x)
                val.logs.append(Info("Starting"))
                val.logs += [Debug(f"Starting with {x}")]
                val >>= fn(int, int)(lambda x: x + 20)
                val.logs += [Info(f"Added {x} to 20")]
            except Exception as e:
                val.logs += [Warning("Something went wrong")]
                val.logs += [Error(str(e))]
            finally:
                return val
        
        val = Crumb(10)
        val >>= add_10
        val >>= add_20
        last_log = val.logs.pop()
        last_log <<= unwrap
        self.assertTrue(last_log.message == "Added 20 to 20")
        val <<= unwrap
        self.assertEqual(40, val)

    