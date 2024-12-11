# PYTHONIX V3

Pythonix V3 brings powerful error handling inspired by Rust and Go, type hinted lambda functions, and slick operator syntax like Haskell to Python. It makes writing Python code more sleek, easy to read, safe, and reliable with full type transparency. Lastly, using Pythonix looks nice, which **matters**. It even extends to the most common data structures like `list`, `dict`, and `tuple`.

The most important part of programming is knowing what can break and why, and being able to handle those issues the right way. Usingn Pythonix's `Res` type
allows you to do that easily, in the way that looks best to you.

TL;DR: You can use operators like `>>=`, `^=`, `**=`, `//=`, `<<=`, their normal operators, or their methods `map`, `map_alt` / `map_err`, `fold`, `where`, `apply` respectively on classes that use the right traits. You handle errors with `Res`, None values with `Res.Some()`, and quickly do stuff to data without having to write comprehensions, for loops, or use the ugly builtin functions. Plus you can make type hinted lamdbda functions with `fn()`, which honestly should have been a thing already. If you don't like the operator grammar then you can use the methods on each class instead.

### Quick Example

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
    val >>= get_data                    # Run another function that could fail using api key
    val ^= lambda: Res.Ok([])           # If err replace with default empty data
    val >>= Listad                      # Convert data to Listad
    data = val << unwrap 
    data >>= lambda r: r.copy()["foo"]  # Run getting foo over each dict
    data //= lambda foo: f % 10 == 0    # Keep only values that are divisiable by 10
    total = Piper(data << sum)          # Sum the totals and put in Piper
    total << print                      # Run print over total

```

## Features

### Dedicated Operator Grammar

Pythonix brings dedicated operator syntax to Python on special classes or classes that implement the right traits. The grammar is as follows:

| Operator | Inplace | Method     | Purpose                             | Example                    |
|----------|---------|------------|-------------------------------------|----------------------------|
| `>>`     | `>>=`   | `map()`    | Change value with function          | `res >>= lambda x: x + 1`  |
| `^`      | `^=`    | `map_alt()`| Change other value with function    | `res ^= ValueError`        | 
| `<<`     | `<<=`   | `apply()`  | Run func over self                  | `res <<= unwrap`           | 
| `**`     | `**=`   | `fold()`   | Run pairs of values thru function.  | `l **= lambda x, y: x + y` | 
| `//`     | `//=`   | `where()`  | Filter elements with function       | `l //= lambda x: x == 0`   |

Note that `fold` and `where` are only applicable to iterable classes like lists, tuples, etc. This grammar is held consistently accross the entire package.
The operators were chosen at **random**! Just kidding, I made sure to use the operators that are used the least and would be least likely to interfere with other processes and still could communicate their intent.

### Handling Exceptions as Values with Res

`Res` is by far the most important class you can use. It wraps the potential for an action to fail and shows you what to expect if it succeeded or failed. You can use the decorators like `safe`, `catch_all`, and `null_safe` to capture the potential for errors or None values.

#### Capturing Without Decorators

```python
def attempt_thing() -> Res[int, Exception]:
    try:
        return Res.Ok(0)
    except Exception as e:
        return Res.Err(e)
```

If you are in a function that doesn't have a return output decorated as `Res` then you'll need to explicitly type hint the `Res` like this.

```python
some: Res[int, Nil] = Res.Ok(10) # Using assignment
ok = Res[int, Exception].Ok(10)  # Using explicit type hints
```

#### Capturing With Decorators

To make things easier the `res` module provides decorators to make working with Exceptions cleaner. There are quite a few, but the most useful are `safe`, `catch_all`, and `null_safe`.

`safe` will catch specific errors and let others slip by. It won't catch None values that are returned.

```python
@safe(KeyError, IndexError)
def get_foo(data: dict[str, int]) -> int:
    return data.copy()['foo']

foo: Res[int, KeyError | IndexError] = get_foo({"foo": 10})
```

`catch_all` will catch all Exceptions thrown. Useful, but not very specific. It's recommended to use `safe` if you know exactly what could happen.

```python
@catch_all
def get_foo(data: dict[str, int]) -> int:
    return data.copy()['foo']

foo: Res[int, Exception] = get_foo({"foo": 10})

```

`null_safe` will catch a returned value that is None. Useful for eliminating the potential for unexpected None values. `Nil` is a special Exception that shows that an None was found.

```python
@null_safe
def get_foo(data: dict[str, int]) -> int:
    return data.copy().get('foo')

foo: Res[int, Nil] = get_foo({"foo": 10})
```

#### Getting values out of `Res`

Getting data out of `Res` is easy and you have a lot of ways to do it. You can use pattern matching, unpacking, methods, and iteration.

##### Pattern Matching a la Rust

Pattern matching works well with `Res`, but requires some extra type hinting if you are using a static type checker. This will be a favorite for Rusty people.

```python
match Res.Some(10):
    case Res(int(inner), True):
        ... # Do stuff with inner now
    case Res(e):
        ... # Do stuff with Nil. Raise it, log it, whatever.
```

##### Unpacking a la Go

You can unpack the `Res` with the `unpack` method. Very similar to error handling in Go.

```python
val, err = Res[int, Exception].Ok(10)
if err is not None:
    raise err
```

##### Handling with Unwrap methods

You can use methods on res to pull out the Ok or Err values. It's recommended that you inspect the `Res` first though, since using them can panic your program if they are not in the expected state.

This is a safe example because it checkd for an Ok state before unwrapping.

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

`safe` will catch any Exception that is thrown by its function, and `unwrap` or `unwrap_err` will throw an exception if they are in an invalid state. So, you could pass throw the exception without any worries, knowing it would be passed up into its value later. Since this is so common, `unwrap` and `unwrap_err` have shortcuts with `q` and `e`.

```python
@safe(Exception)
def go_thing() -> int:
    data_attempt: Res[list, Exception] = get_data()
    data = data_attempt.q
    return data

```

##### Handling with Transformations

You can also handle Exceptions without extracting the desired value from the `Res` by using `map` and `map_alt`. They go to `>>` and `^` respectively.

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

You can also iterate through the `Res` to extract its Ok value. It will only return an item if its in an Ok state. It can automatically iterate through 
`lists`, `tuples`, and `sets` automatically if in an Ok state.

Here's an example with a normal Ok `Res`.

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

Will return an empty iterator if in an Err state

```python
for val in Res[int, Nil].Nil():
    val # This code would never be executed
```

### Upgraded collections

A big point of Pythonix is to make working with data clean and concise while reducing the chance for errors. Part of that is `Res`, which makes Exceptions safer to handle and more obvious. The other part is upgrading the most common data structures to be better.

The most common data types in Python are `list`, `dict`, `tuple`, `set`, and `deque`. To make working with them easier, the most common operations for those data types have been
added as methods, and then as operators using the operator grammar shown above.

To get started, just wrap your data structures as their respective upgraded versions. `Listad`, `Dictad`, `Tuplad`, `Set` and `Deq`. All of these types have the same operators and methods added on, as well as making some of their methods that could panic more safe with `Res`.

Here's a pretty common example of some work with normal `list`. Obviously this is redundant but bear with me.

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
data: Listad[int] = Listad([i for i in range(0, 100)])
data >>= fn(int, int)(lambda x: x + 10)
data //= fn(int, bool)(lambda x: x % 2 == 0)
data >>= str
data >>= str.split
data //= fn(str, bool)(lambda c: c == '0')
data **= operator.concat
```

For clarity here it is with methods.

```python
data: Listad[int] = Listad([i for i in range(0, 100)])
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

Some additional features can be found in the supplementary modules, included with Pythonix.

| Module Name | Purpose                                                     |
|-------------|-------------------------------------------------------------|
| crumb       | Attach logs to values and accumulate them                   |
| prove       | Simple assertion functions                                  |
| utils       | Safe functions to help working with Res and collections     |
| fn          | Lambda function utilities                                   |
| curry       | Automatic currying of functions                             |
| grammar     | Classes and pipes for custom grammar                        |
| traits      | Classes to make custom classes that use the operator syntax |