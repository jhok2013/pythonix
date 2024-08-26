from unittest import TestCase
from pythonix.res import *
from pythonix.trail import *

class TestTrail(TestCase):

    def setUp(self) -> None:
        self.t = Trail(10, [Info("10 created")])
        return super().setUp()
    
    def test_log(self):
        l = Log("hello")
        self.assertEqual(l.message, "hello")
    
    def test_child_logs(self):
        info = Info("hello")
        debug = Debug("hello")
        warning = Warning("hello")
        error = Error("hello")
        critical = Critical("hello")
    
    def test_extend(self):
        self.t.logs.extend([Info("Oi cunt"), Info("Hello world")])
        match self.t:
            case Trail(inner, logs):
                *rest, last = logs
                match last:
                    case Info(message, dt):
                        self.assertEqual(message, "Hello world")
                    case _:
                        self.fail()
            case _:
                self.fail()

    def test_extend_left(self):
        self.t.logs.extendleft([Info("Oi cunt"), Info("Hello world")])
        match self.t:
            case Trail(_, logs):
                first, *_ = logs
                match first:
                    case Info(message, dt):
                        self.assertEqual(message, "Hello world")
                    case _:
                        self.fail()
            case _:
                self.fail()
    
    def test_to_tuple(self):
        val, logs = self.t.to_tuple()
        self.assertEqual(val, 10)
    
    def test_map(self):
        self.t = self.t.map(lambda x: x * 2, Info("Multiplied by two"))
        self.assertEqual(self.t.inner, 20)
        self.assertEqual(self.t.logs[-1].message, "Multiplied by two")
        
    def test_and_then(self):
        self.t = self.t.and_then(
            lambda x: Trail(x + 10, [Info("Added 10")]),
            Info("Performed operation")
        )
        self.assertEqual(self.t.inner, 20)
    
    def test_map_with_res(self):
        res = Ok(10, ValueError)
        self.t = Trail(res, [Info("Received result")])
        self.t = (
            self.t
            .map(lambda r: r.map(lambda x: x + 10), Info("Added 10"))
            .map(lambda r: r.map(lambda x: x * 2), Info("Multiplied by 2"))
            .map(lambda r: r.q)
        )
        self.assertEqual(40, self.t.inner)
    

class TestDecorators(TestCase):


    def setUp(self):
        self.t = Trail(10, [Info("10 created")])
        return super().setUp()
    
    def test_start(self):

        @start(Info("Starting addition function"))
        def add(x: int, y: int) -> int:
            return x + y
        
        trail = add(2, 2)
        log = trail.logs.pop()
        self.assertEqual("Starting addition function", log.message)
    
    def test_then_top(self):

        @then_log_top(Info("Hello there!"))
        @start(Info("Starting addition function"))
        def add(x: int, y: int) -> int:
            return x + y
        
        trail = add(1, 1)
        log = trail.logs.popleft()
        self.assertEqual("Hello there!", log.message)
    
    def test_then_bottom(self):
        message = "Done"
        @then_log(Info(message))
        @start(Info("Starting addition function"))
        def add(x: int, y: int) -> int:
            return x + y
        
        trail = add(1, 1)
        log = trail.logs.pop()
        self.assertEqual(message, log.message)
    
    def test_then_top_and_bottom(self):

        message = "Done"

        @then_log(Info(message))
        @then_log_top(Info("Hello"))
        @start(Info("Starting addition function"))
        def add(x: int, y: int) -> int:
            return x + y
        
        trail = add(1, 1)
        first, middle, last, *rest = trail.logs
        self.assertEqual(first.message, "Hello")
        self.assertEqual(middle.message, "Starting addition function")
        self.assertEqual(last.message, message)
    
    def test_start_with_res(self):

        @start(Info("Starting division"))
        @safe(ZeroDivisionError)
        def divide(x: int, y: int) -> float:
            return x / y

        trail = divide(10, 2)
        print(trail)
        
        
    def test_with_res(self):

        @safe(ZeroDivisionError)
        @then_log("Successfully divided")
        @start(Info("Starting division"))
        def divide(x: int, y: int) -> float:
            return x / y
        
        x = divide(10, 0)
