from unittest import TestCase
from typing import Callable
from pythonix.prelude import trail as t
from pythonix.prelude import pipe as p


class TestTrail(TestCase):
    blaze = t.Blaze(5, t.info("Starting"))
    bind = p.Bind(t.new(t.info("Starting in Bind"))(5))

    def test_blaze(self) -> None:
        decorated: Callable[[int], int] = t.trail(t.info("Using decorator"))(
            lambda x: x
        )
        logs = self.blaze(lambda x: x, t.info("Returning same"))(decorated).logs

        self.assertEqual(len(logs), 3, str(logs))

    def test_bind(self) -> None:
        def round_one(trail: t.Trail[int]) -> t.Trail[int]:
            return t.new(t.info("Adding a new log"), *trail.logs)(trail.inner + 1)

        def round_two(trail: t.Trail[int]) -> t.Trail[int]:
            return t.new(t.info("Adding a new log"), *trail.logs)(trail.inner + 1)

        logs = self.bind(round_one)(round_two)(t.logs).inner

        for log in logs:
            print(log)
        self.assertEqual(len(logs), 3)
