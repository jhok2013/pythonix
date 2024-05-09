from unittest import TestCase
from pythonix.pipe import Bind, Do


class TestPipes(TestCase):
    def setUp(self) -> None:
        self.bind = Bind(5)
        self.do = Do("hello world")
        return super().setUp()

    def test_bind(self) -> None:
        (
            self.bind(lambda x: x + 1)(lambda x: x * 2)(float)(str)(lambda _: True)(
                self.assertTrue
            )
        )
    
    def test_to_do(self) -> None:
        (
            self.bind
            .to_do(lambda _: True)(lambda _: 'Hello')
            .to_bind(lambda _: True)(self.assertTrue)
        )

    def test_do(self) -> None:
        (self.do(print)(print)(print))
