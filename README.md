# PYTHONIX

A collection of functional modules in Python 11 inspired by Gleam and Rust.
If you like functional oriented programming, but have to program in Python, then check this out.

The goal is to take some great features of Rust like strong types, errors by value with Results
and Options, error unpacking like in Go, and some other great features from Gleam like piping with `|>` and classes as
modules, and combine them for use in Python without any external dependencies.

Here are examples of my favorite features:

## Pipes and Pipe Likes

`P` and `Piper` are special wrapper classes the take what's on the left, and put it into the function on the right.

You can take statements like this:

    ```python
    data = list(range(0, 300))
    total = reduce(lambda x, y: x + y, map(lambda x: x + 10, filter(lambda x: x % 2 == 0), data))
    print(total)
    ```

And turn them into more readable statements like this:

    ```python
    (
        Piper(range(0,10))
        >> list
        >> op.where(fn(int, bool)(lambda x: x % 2 == 0))
        >> op.map_over(fn(int, int)(lambda x: x + 10))
        |  print
        > op.fold(fn(int, int, int)(lambda x, y: x + y))
    )    
    ```

Most of the functions in pythonix are curried and have the subject as the last argument.
Curried means the arguments are passed in as function calls, and having the subject last
makes piping possible without changing Python's syntax. To make functions that work with
piping, take your functions that are like this:

    ```python
    def get(data: list[int], index: int | slice) -> int:
        return data[index]
    
    first = get([1, 2, 3], 0)

    ```

And make them like this.

    ```python
    def get(index: int | slice):

        def inner(data: list[int]):

            return data[index]

        return inner 

    first = get(0)([1, 2, 3])

    ```

Or if that's too much, use the `curry` decorators to make it easier.

    ```python
    @curry.two
    @curry.first_to_end
    def get(data: list[int], index: int | slice) -> int:
        return data[index]

    first = get(0)([1, 2, 3])

    ```

Back to Piping, there are three functions worth knowing with `Piper`.

1. `>>`: Put the value inside `Piper` into the function, and return a new `Piper` with the result.
2. `|`: Put the value inside `Piper` into the function, but keep `Piper` the same.
3. `>`: Put the value inside `Piper` into the function, and only return the result. Useful for exiting
the Piper's context and returning the final result.

If the operators aren't working for whatever reason, you can always use the `bind`, `do`, and `apply` methods, which map
to `>>`, `|`, and `>` respectively.

You can also use the `P` operator with pipes for quick bespoke piping of values. Like so:

    ```python
    (
        range(0, 10)
        |P| list
        |P| op.where(fn(int, bool)(lambda x: x % 2 == 0))
        |P| op.map_over(fn(int, int)(lambda x: x + 10))
        |P| op.fold(fn(int, int, int)(lambda x, y: x + y))
        |P| print
    )
    ```

It doesn't always save space, but it does make it easier to read
sequential function calls. Because the functions are decoupled
from their objects, you can pipe arbitrary functions over anything.

## Obvious Errors and Nulls

One of my favorite features of Rust is handling Exceptions as values
rather than try catching and throwing them. It's great because it makes
it very obvious when and how things can go wrong and encourages you
to handle the errors intentionally.

It is a little more verbose though, but the tradeoff is worth it.

### Error Catching

Instead of doing this:

```python
def get_customer_data(customer_id: int) -> dict:
    try:
        customer_data = get_data(customer_id)
        return customer_data
    except ValueError as e:
        print("Wrong id")

data: dict = get_customer_data(10)

```

You do this instead:

```python
def get_customer_data(customer_id: int) -> Res[dict, ValueError]:
    try:
        customer_data = get_data(customer_id)
        return Ok(customer_data)
    except ValueError as e:
        return Err(e)

data: Res[dict, ValueError] = get_customer_data(10)

```

Or you can do this automatically with a decorator:

```python
@res.safe(ValueError)
def get_customer_data(customer_id: int) -> dict:
    return get_data(customer_id)

data: Res[dict, ValueError] = get_customer_data(10)

```

Now it's obvious when things can go wrong and your type hints on your IDE will 
show you when things can fail.

### Error Handling

You can handle errors with pattern matching a la Rust, unpacking a la Go, or
with the `res` module a la Gleam.

Here is an example with pattern matching:

```python
data: Res[dict, ValueError] = get_customer_data(10)

match data:
    case Ok(customer_data):
        return customer_data
    case Err(e):
        logging.error(e)
        raise e
    case _:
        raise TypeError('Something went wrong')

```

This is great for being thorough with your results. You can see each case
and easily unpack the data from Ok and Err. It also makes it easy to apply
a default case or handle complex situations.

But what if I want something simple and fast like in Go? Say no more.

Try this instead:

    ```python

    data, err = unpack(get_customer_data(10))
    if err is not None:
        logging.error(e)
        raise e
    if data is None:
        raise TypeError('Something went wrong')

```

But wait?! In Go I can do `val, err = could_fail()`. Why do I have to use `unpack`?

It's a python thing. Because `Res` is actually `Ok | Err`, the type hints don't work
correctly if you unpack them normally, even if you have an `__iter__` method set up,
and base classes for `__iter__` and blah blah blah.

In short, I had to choose between better unpacking or better pattern matching. I chose
pattern matching because I think it looks neat, and you only sacrifice one function to
get it done.

Plus, it's easy to apply functions to results with `P` and `Piper`, remember?

    ```python
    data, err = get_customer_data(10) |P| unpack
    if err is not None:
        logging.error(e)
        raise e
    if data is None:
        raise TypeError('Something went wrong')
    ```

You can also handle results with the `res` module, which has a lot of utilties
for unwrapping, handling, and transforming results safely. The module shamelessly
stolen from Rust's excellent methods, but implemented like Gleam.

Here is an example:

    ```python
    data = res.unwrap(get_customer_data(10))
    ```

The above example will give you the Ok data if any, or raise the E instead. You can
also unwrap the err with `unwrap_err`. Since this is such a common thing, there is
a shorthand variant called `q` and `qe` which are unwrap and unwrap_err respectively.
`q` and `qe` are inspired by `?` in Rust.

The res module has a lot inside. Here is an example of an entire flow where we
are getting customer ids, and then getting total orders from the customer data.
There are a lot of steps that can fail, so we use `q` to unwrap the errors
and `safe` to catch them as we do. We can also combine multiple errors into one
with `combine_errors`.

    ```python
    @res.safe(HTTPError, ValueError)
    def get_customer_data(customer_id: int) -> dict:
        return get_data(customer_id)

    @res.combine_errors(ValueError(), True)
    @res.safe(HTTPError, ValueError, Nil)
    def accumulate_customer_orders() -> int:
        customer_ids: list[int] = (
            Piper(get(customer_endoint))
            >> fn(Response, dict)(lambda response: response.json())
            >> op.item('ids')
            > q
        ) 
        total_orders = (
            Piper(customer_ids)
            >> op.map_over(get_customer_data)
            >> op.where(res.is_ok)
            >> op.map_over(q)
            >> op.map_over(op.item('orders'))
            >> op.map_over(q)
            > op.fold(fn(int, int, int)(lambda x, y: x + y))
        )
        return total_orders

    def main():
        current_orders: Res[int, ValueError] = accumulate_customer_orders()
        match current_orders:
            case Ok(orders):
                print(f'Currently there are {orders} orders')
            case Err(e):
                logging.error(e)
                ping_slack_error_channel(str(e))
                raise e

    ```

### Null Handling

You handle `None` values the same way you handle Exceptions, by using
decorators or functions to catch values that could be None, and then
use pattern matching, unpacking, or the `res` module to go from there.

Here are some ways you can catch null values:

If a function value could be `None`, you can use the `some` function to
catch that and return a `Res[T, Nil]` result, which can be abbreviated to
`Opt[T]`.

    ```python
    val: str | None = {'hello': 'world'}.get('hello')
    opt: Opt[str] = some(val)
    ```

For function calls that could return `None`, you can have them return `Opt[T]`
instead.

    ```python
    # With some
    def get_hello(data: dict[str]) -> Opt[str]:
        return some(data.get('hello'))

    hello: Opt[str] = get_hello({'hello': 'world'})

    # With ok and err
    def get_hola(data: dict[str]) -> Res[str, Nil]:
        try:
            return ok(Nil)(data['hola'])
        except KeyError as e:
            return err(str)(Nil(str(e)))
    
    hola: Res[str, Nil] = get_hola({'hola': 'mundo'})
    # Res[str, Nil] is the same as Opt[str]
    ```

Or you can use the `res.null_safe` or `res.null_and_error_safe` decorators to do that for you.

    ```python
    @null_safe
    def get_hello(data: dict[str]) -> str | None:
        return data.get('hello')
    
    hello: Opt[str] = get_hello({'hello': 'world'})

    @null_and_error_safe(KeyError)
    def get_hola(data: dict[str]) -> str | None:
        return data['hola']
    
    hola: Res[str, Nil] = get_hola({'hola': 'mundo'})
    # Res[str, Nil] is the same as Opt[str]
    ```

Using these patterns makes it almost impossible to have unexpected or unhandled null
values in your code. Isn't that great?!

## Additional Features

Some other notable features include:

    * Log concatentation with the `trail` module
    * Pipeable asserts with `prove`
    * Supplement modules for common data structures with `pair`, `tup`, `dict_utils`, and `deq`.
    * Custom operator decorators with `grammar`
    * Type hinted lambda functions with `fn`

Each module is available for import like this:

    ```python
    from pythonix.prelude import *
    ```

Import all from prelude will include all of the essentials like `Piper`, `P`, common `res` classes and functions, `fn`, etc.

Or you can specify a particular module like this:

    ```python
    import pythonix.op as op
    import pythonix.tup as tup
    import pythonix.deq as deq
    ```

All the modules are fully tested, promote immutability, fully type checked and transparent, and fully documented.

Enjoy!
