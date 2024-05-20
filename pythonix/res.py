"""
Functions and types for handling expected and unexpected outcomes, like Exceptions and errors.
Works well with `Bind` and `Do` to capture, handle, and unwrap the results of operations as values.

The basic flow is as follows:
1. Capture Errors
2. Handle Errors
3. Retrieve Desired Values

### 1. Capture errors
```python
# This function could fail, let's make it obvious how and why so
# we are not surprised
def get(index: int, data: list[int]) -> int:
    return data[index]

# Let's capture the error in a result
def get(index: int, data: list[int]) -> Res[int, IndexError]:
    try:
        return res.ok(IndexError)(data[index]) 
    except IndexError as e:
        return res.err(int)(e)
    
# Or, we can use the safe decorator to do the boilerplate for us
# This is now the same as the previous definition
@safe(IndexError)
def get(index: int, data: list[int]) -> int:
    return data[index]
```

### 2. Handle Errors
We know how to capture errors, now how can we handle them and use their values?
There are a few ways:
1. Pattern Matching
2. Unpacking
3. Wrapper type functions

#### Pattern Matching
If we have a result that could be `Ok` or `Err`, we can use pattern matching to get our values safely.
This is a great way to handle errors but it can be cumbersome if there are a lot of
errors possible.
```python
res: Res[int, IndexError] = res.ok(IndexError)(10)

# Use Ok and Err to handle the outcome
match res:
    case Ok(value):
        print(f'The value is {value}')
    case Err(e):
        print(f'An error occurred. {str(e)}')
```

#### Unpacking
We can unpack an `Res` using the unpacking syntax. Very similar to Go's method of
handling errors as values. This is an easy way to handle errors, but it can make type hints
a bit cumbersome since each value is its type or `None`
```python
res: Res[int, IndexError] = res.ok(IndexError)(10)

# Unpack and check if None to handle the errors
val, err = res
if err is not None:
    print(f'An err occurred. {str(err)}')
```

#### Wrapper Type Functions
These functions allow you to keep the value inside the `Res` type and still operate on it
without the risk of errors. You can use the functions normally, or you can
use the `Bind` and `Do` wrapper types to make it even easier. This method can be a
little harder to read for those not familiar with it.

There are specific functions that only work if `Ok`, and others that only work if `Err`. Using
the functions normally is great if you only need to do a few things to an outcome. Otherwise
it can become a bit cumbersome.
#### With Only Functions
```python
outcome: Res[int, IndexError] = res.ok(IndexError)(10)
add_10: Res[int, IndexError] = res.map(lambda x: x + 10)(outcome)
```

#### With Bind
The `Bind` or `B` wrapper type will take its wrapper value and put it into the
function given to it, returning a new `Bind` to repeat the process. It works
great with repeated functions like the `res` functions.

This is best when needing a lot of operations on a result, otherwise it's overly
verbose.
```python
(
    B(res.ok(IndexError)(10))
    (res.map(add(10)))
    (res.map(sub(30)))
    (res.and_then(do_thing))
    (res.or_else(do_if_failed))
)
```

#### With Pipe
The `P` wrapper type takes whatever is on its left, and puts it into the function on its
right. It uses the `|` symbol to define left and right. It can be substituted for the `Bind`
type in a pinch, but it does not retain type information as well.

This is best when you need a quick application of a function and using `Bind` or 
a series of normal functions would be too much.
```python
add_10: Res[int, IndexError] = (
    res.ok(IndexError)(10) |P| res.map(lambda x: x + 10)
)
```

### 3. Retrieving or Unwrapping Results
If you use Pattern Matching or Unpacking then you don't need to worry about this part.
If you are using the functions then this can make things easier though. You can use
the `res.unwrap`, `res.unwrap_err`, or the shorthand functions `q` and `qe` respectively
to get the expected values and panic if they are not what you expect.

You generally want to avoid using these functions unless you are in a function
scope wrapped with @safe, and then only if the potential error matches the captured error.

For example
```python
# This could be an int or it could have failed, who knows
outcome: Res[int, IndexError] = res.ok(IndexError)(10)

# You can unwrap the result
# This will panic with the wrapped error
with_unwrap: int = res.unwrap(outcome)
with_q: int = q(outcome)

with_pipe: int = outcome |P| q
with_bind: int = B(outcome)(q).inner
```

#### Safe Error Handling Sugar
Here is an example of handling potential errors in a program.
For the sake of simplicity, assume that the unnamed functions like `get_data`
are valid.

```python
@safe(IOError)
def get_file(path: Path) -> StreamBuffer:
    return open(path)

@safe(IOError)
def parse_file(stream: StreamBuffer) -> int:
    return (
        stream
        |P| get_data
        |P| q
        |P| accumulate
        |P| q
    )

@safe(HTTPError)
def send_total(email: str, total: int) -> None:
    return (
        B(email)
        (prep_email)
        (add_total)
        (send)
        (q)
    )

@safe(IOError, HTTPError)
def execute() -> None:
    path: Path = Path('.config')
    (
        B(path)
        (get_file)(q)
        (parse_file)(q)
        (send_total)(q)
    )

def main():
    match execute():
        case Ok(_):
            debug('Success')
        case Err(e):
            match e:
                case IOError(message):
                    error(message)
                    raise e
                case HTTPError(message):
                    error(message)
                    notify_sales_team(message)
                    raise e
                case _:
                    error('Unidentified error')
                    raise _
        case _:
            error(f'Unexpected value was found {_}')
            raise Exception('An unidentified value was returned')
```
"""
from pythonix.internals.res import (
    and_res,
    and_then,
    err,
    flatten,
    is_err,
    is_err_and,
    is_ok,
    is_ok_and,
    map,
    map_err,
    map_or,
    map_or_else,
    null_safe,
    ok,
    or_else,
    safe,
    map_err,
    unwrap,
    some,
    Res,
    Nil,
    or_res,
    unwrap_err,
    unwrap_or,
    unwrap_or_else,
    Ok,
    Err,
    null_and_error_safe,
    q,
    qe,
)
