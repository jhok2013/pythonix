# PYTHONIX V3

Pythonix brings errors-as-values a la Go and Rust, typed anonymous functions,
and slick operator syntax. It makes sleeker and safer code with full type
transparency. It looks clean and nice, which **matters**. And, it
extends common data types like `list`, `dict`, and `tuple`.

Knowing what can break, why, and how to fix it is the most important part of
programming. Pythonix's `Res` type does that cleanly, in the style you prefer.

TL;DR: Use operators `>>=`, `^=`, `**=`, `//=`, and `<<=` to declaratively handle
errors, nulls, and process data. If that style doesn't suit you, then use their
associated methods like `map`, `map_alt`, `fold`, `where`, and `apply`.

## Quick Example

```python

# Catch all potential errors in a Res
@catch_all
def get_data(api_key: str) -> list[dict[str, str]]:
    """Pretend API call that could fail"""
    return [{"foo": 10, "bar": 10}] * 100

@catch_all
def get_api_key() -> str:
    return "hello there"

def main():
    val = get_api_key()
    val >>= get_data                    # Run fallible func using api key
    val ^= lambda: Res.Ok([])           # If err replace with default empty data
    val >>= Listad                      # Convert data to Listad
    data = val << unwrap 
    data >>= lambda r: r.copy()["foo"]  # Run getting foo over each dict
    data //= lambda foo: f % 10 == 0    # Keep values divide by 10
    total = Piper(data << sum)          # Sum the totals and put in Piper
    total << print                      # Run print over total

```

## Features

### Operator Syntax

Pythonix has operator syntax on special classes. The grammar is as follows:

| Op.| Method | Purpose | Example |
|----|--------|---------|---------|
| `>>` | `map`    | func on value | `rs >>= lambda x: x + 1` |
| `^`  | `map_alt`| func on alt. value | `rs ^= ValueError` |
| `<<` | `apply`  | func on self | `rs <<= unwrap` |
| `**` | `fold`   | func on pairs | `l **= lambda x, y: x + y` |
| `//` | `where`  | func filters values | `l //= lambda x: x == 0` |

Note that `fold` and `where` are only applicable to iterable classes like lists,
tuples, etc. This syntax can be extended by inheriting from the operator's
base class.

### Handling Exceptions as Values with Res

`Res` is the most important class you can use. It wraps fallible actions,
showing the value on success and failure, similar to the `Result` enum in Rust.

#### Capturing Without Decorators

```python
def attempt_thing() -> Res[int, Exception]:
    try:
        return Res.Ok(0)
    except Exception as e:
        return Res.Err(e)
```

Explicitly type hint a `Res` as so, if the outer function doesn't already.

```python
some: Res[int, Nil] = Res.Ok(10) # Using assignment
ok = Res[int, Exception].Ok(10)  # Using explicit type hints
```

#### Capturing With Decorators

For convenience, the `res` module has decorators to wrap implement common patterns.

`safe` will catch specific errors and let others slip by. It won't catch None
values that are returned.

```python
@safe(KeyError, IndexError)
def get_foo(data: dict[str, int]) -> int:
    return data.copy()['foo']

foo: Res[int, KeyError | IndexError] = get_foo({"foo": 10})
```

`catch_all` captures all thrown Exceptions. It's recommended to use `safe` if
you know exactly what could happen, and `catch_all` if there are too many
Exceptions to capture.

```python
@catch_all
def get_foo(data: dict[str, int]) -> int:
    return data.copy()['foo']

foo: Res[int, Exception] = get_foo({"foo": 10})

```

`null_safe` captures None output. `Nil` is the Exception that
shows a capture None.

```python
@null_safe
def get_foo(data: dict[str, int]) -> int:
    return data.copy().get('foo')

foo: Res[int, Nil] = get_foo({"foo": 10})
```

#### Getting values out of `Res`

Getting data out of `Res` is easy and you have a lot of ways to do it. You can
use pattern matching, unpacking, methods, and iteration.

##### Pattern Matching a la Rust

Pattern matching works well with `Res`, but requires some extra type hinting
if you are using a static type checker. This will be a favorite for Rusty people.

```python
match Res.Some(10):
    case Res(int(inner), True):
        ... # Do stuff with inner now
    case Res(e):
        ... # Do stuff with Nil. Raise it, log it, whatever.
```

##### Unpacking a la Go

You can unpack the `Res` with the `unpack` method. Very similar to error
handling in Go.

```python
val, err = Res[int, Exception].Ok(10).unpack()
if err is not None:
    raise err
```

##### Handling with Unwrap methods

`unwrap` and `expect` return the `Ok` value or raise the Exception. Be sure to inspect
the `Res` before using them, unless the program cannot recover from the error.

This is a safe example because it checked for an `Ok` state before unwrapping.

```python
res = Res[int, Exception].Ok(10)
if res:
    val = res.unwrap()
```

This is an unsafe example that could cause your code to panic.

```python
res = Res[int, Exception].Err(Exception("oops"))
res.unwrap()
```

##### Handling with @safe

Throwing an Exception using `unwrap` is safe if the function is wrapped with
a capturing decorator. This is similar to using `?` in Rust. The `q` and `e`
properties are convenient shortcuts for this pattern.

```python
@catch_all
def go_thing() -> int:
    data_attempt: Res[list, Exception] = get_data()
    data = data_attempt.q
    return data

```

##### Handling with Transformations

You can also handle Exceptions without extracting the desired value from the
`Res` by using `map` and `map_alt`. They go to `>>` and `^` respectively.

Here's an example with the methods:

```python
    some: Res[int, Nil] = get_data()
    data = (
        some
        .map(lambda x: x + 10)
        .map(do_foo)
        .map_err(send_error_report)
        .map_err(lambda: Res.Some(0))
    )
```

Here's the same example using operator grammar.

```python
    some: Res[int, Nil] = get_data()
    some >>= lambda x: x + 10
    some >>= do_foo
    some ^= send_error_report
    some ^= lambda: Res.Some(0)
```

##### Handle with Iteration

You can iterate through the `Res` to extract its `Ok` value. It will only return
an item if its in an `Ok` state. It iterates through `lists`,`tuples`, and
`sets` if in an `Ok` state.

Here's an example with a normal `Ok` `Res`.

```python
for val in Res.Some(10):
    val # Code inside this loop is okay

val = [val for val in Res.Some(10)] # Will only have a value if Ok

```

Here's an example of automatically iterating through a contained `list`.

```python
for val in Res.Some([1, 2, 3]):
    val # Will be 1, then 2, then 3

```

It will return an empty iterator if in an Err state

```python
for val in Res[int, Nil].Nil():
    val # This code would never be executed
```

### Upgraded collections

Pythonix enables cleaner, safer, and conciser code. Part of that is `Res` for
better error handling. Another is upgrading the common data
structures with convenient operators and methods.

To get started, just wrap your data structures as their upgraded versions.
`Listad`, `Dictad`, `Tuplad`, `Set` and `Deq`. All of these types have the same
operators and methods, and their fallible methods are safer with `Res`.

Here's a messy example with a `list`:

```python
out = []
for i in range(0, 100):
    i += 10
    if i % 2 == 0:
        w = str(i)
        chars = w.split()
        for char in chars:
            if char == '0':
                out.append(char)
final = reduce(operator.concat, out)
```

Here's the same result using `Listad`.

```python
data: Listad[int] = Listad(range(100))
data >>= fn(int, int)(lambda x: x + 10)
data //= fn(int, bool)(lambda x: x % 2 == 0)
data >>= str
data >>= str.split
data //= fn(str, bool)(lambda c: c == '0')
data **= operator.concat
```

The code can become more declarative and clear using named functions.

```python
data = Listad(range(100))
data >>= add(10)
data //= is_even
data >>= str
data >>= str.split
data //= str_eq('0')
data **= concat
```

For clarity here it is with methods.

```python
data: Listad[int] = Listad(range(100))
chars = (
    data
    .map(fn(int, int)(lambda x: x + 10))
    .where(fn(int, bool)(lambda x: x % 2 == 0))
    .map(str)
    .where(fn(str, bool)(lambda c: c == '0'))
    .fold(operator.concat)
)
```

Pretty nice right?!

### Other Features

Some additional features can be found in the supplementary modules, included
with Pythonix.

| Module Name | Purpose                                                     |
|-------------|-------------------------------------------------------------|
| crumb       | Attach logs to values and accumulate them                   |
| prove       | Simple assertion functions                                  |
| utils       | Safe functions to help working with Res and collections     |
| fn          | Lambda function utilities                                   |
| curry       | Automatic currying of functions                             |
| grammar     | Classes and pipes for custom grammar                        |
| traits      | Classes to make custom classes that use the operator syntax |

### To Dos and Future Features

- [] Simplifying of names for Collections, Results, Trails, and Pipes
- [] Better cohesion for Trail and other Collads
- [] Adding Eager and Lazy modes for collections
- [] Upgraded expect methods
- [] Make E not exclusive to Exception types

