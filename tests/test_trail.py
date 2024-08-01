from unittest import TestCase
from pythonix.prelude import trail as t
from pythonix.prelude import fn

class TestTrail(TestCase):
    
    def test_new(self):
        trail = t.new(
            t.Info("Starting"), t.Debug("Starting"), t.Error("Starting"), t.Critical("Starting")
        )(10)
        self.assertEqual(4, len(trail.logs))
    
    def test_on_start(self):

        add_ten = t.on_start(t.Info('Adding ten'))(fn(int, int)(lambda x: x + 10))
        y = add_ten(10)
        first, *_ = y.logs
        self.assertEqual('Adding ten', first.message)
        print(first)
    
    def test_append(self):

        trail = t.new(t.Info("Starting"))(10)
        trail = t.append(t.Info("Continuing"))(trail)
        self.assertEqual(2, len(trail.logs))
    
    def test_blaze(self):

        add_ten = t.on_start(t.Info('Adding ten'))(fn(int, int)(lambda x: x + 10))
        add_five = t.on_start(t.Info('Adding 5'))(fn(int, int)(lambda x: x + 5))
        to_str = t.on_start(t.Info("Converting to str"))(fn(int, str)(lambda x: str(x)))
        ten = t.new(t.Info('Starting'))(10)
        twenty = t.blaze(add_ten, t.Info("Putting in ten"))(ten)
        thirty = t.blaze(add_ten, t.Info("Puttingin twenty"))(twenty)
        thirty_five = t.blaze(add_five, t.Info("Puttingin thirty"))(thirty)
        as_str = t.blaze(to_str, t.Info("Putting in 35"))(thirty_five)
        finished = t.append(t.Info("Done"))(as_str)
        inner, logs = t.unpack(finished)
        *_, last = logs
        self.assertEqual(inner, '35')
        self.assertEqual('Done', last.message)

    def test_logs(self):

        log = t.Info("Hello world")
        message, *_ = log