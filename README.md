# PYTHONIX

A collection of functional modules in Python 11 inspired by Gleam and Rust.
If you have like functional programming, but have to program in Python, then check this out.

## Features

1. Exceptions as values support similar to Rust
2. Emphasis on immutable types
3. Great support for immutable data structures
4. Wrapper types to enable consecutive function calls via pipelike types
5. Strongly typed hints with generic support
6. Emphasis on composability with partially applied functions
7. Emphasis on removing nullability

## Examples

### Piping with Bind and Do
```python
from pythonix.prelude import *

# Use Bind to transform a value by chaining function calls
(
    Bind(5) # Start as int
    (str)   # Cast as str
    (       # Join with a lambda
        lambda s: ' '.join([s, "times 3"])
    )
    (print) # Print to screen. Inner is now None
)

# Use do when you need to change a mutable datatype or do something without changing the value
x = (
    Do(5)   # Start as int
    (info)  # Log value to info
    (str)   # Convert to str
)

assert x == 5

```

### Error as Value
```python
from pythonix.prelude import *
from pythonix.res import Res

# Capture errors as types with the res decorators
@res.safe(TypeError)
def foo(bar: int) -> int:
    if not isinstance(bar, int):
        raise TypeError("Invalid type")
    return bar

# Make functions that return `Ok` or `Err` to show the possibility of failure
def far(boo: int) -> Res[int, TypeError]:
    if not isinstance(boo, int):
        return Err(TypeError("Invalid type"))
    return Ok(boo)

# The result is captured to show errors and success
bar: Res[int, TypeError] = foo(5)

# Pipe through consecutive functions to handle errors
bar: int = (
    pipe.Bind(bar)
    (res.map(lambda x: x + 5))
    (res.map_err(lambda e: Exception("New error")))
    (res.and_then(lambda x: foo(x)))
    (res.unwrap)
    .inner
)

# Use match case statements to handle errors too
match bar:
    case Ok(x):
        print(x)
    case Err(e):
        print(e)

# Unpack `Res` types to handle them like in Go
val, err = bar
if err is not None:
    raise err
```

### Concatenate logs for thread safe logging
You can attach logs to data types with `Trail`. Use the `Blaze` pipe
to run functions with logs and concatenate them safely

```python
from pythonix.trail import Trail, info, trail, new, log, Blaze
from pythonix.tuple import first

# Decorate a function with @trail to have it always log a certain message
@trail(info("Added one"))
def add_one(x: int) -> int:
    return x + 1

def add_two(x: int) -> Trail[int]:
    return new(x + 2)(info("Added two"))

two: Trail[int] = add_one(1)
three: Trail[int] = add_two(1)

assert two.inner == 2
match first(three.logs):
    case Ok(log):
        assert log.message == "Added two"
    case Err(e):
        raise e

logs = (
    Blaze(two, info("Wrapped in Blaze"))
    (add_two, info("Did a thing"))
    (add_one, info("Did another"))
    (add_two, info("Finished"))
    .logs
)

assert len(logs) == 8

```




